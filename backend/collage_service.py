from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter()

def hex_to_rgb(hex_str: str) -> tuple:
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def create_pro_collage(images, num_columns: int = 4, watermark_text: str = "KNWLDG MEDIA",
                       blur_images: bool = False, blur_radius: int = 5,
                       bg_color: tuple = (10, 10, 10),
                       watermark_color: tuple = (255, 165, 0),
                       watermark_opacity: int = 60,
                       watermark_size: int = 45):
    if not images:
        raise ValueError("No images provided")

    # 1. Load images and determine adaptive target_width based on max width
    loaded_imgs = []
    max_w = 0
    for img_data in images:
        img = Image.open(BytesIO(img_data)).convert("RGBA")
        if img.width > max_w:
            max_w = img.width
        loaded_imgs.append(img)

    # Adaptive width: use max width of uploaded images, capped at 2500px per column to prevent out-of-memory
    target_width = min(max_w, 2500)
    if target_width < 450:
        target_width = 450

    # Adaptive spacing: ~3% of column width
    spacing = max(15, int(target_width * 0.03))
    
    resized_imgs = []
    for img in loaded_imgs:
        # Apply blur if the option is enabled
        if blur_images:
            # Scale blur radius adaptively based on target_width upscale
            adaptive_blur = int(blur_radius * (target_width / 450.0))
            if adaptive_blur < 1: adaptive_blur = 1
            img = img.filter(ImageFilter.GaussianBlur(radius=adaptive_blur))

        w_percent = (target_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        
        # Only resize if dimension is different
        if abs(img.size[0] - target_width) > 2:
            resized_imgs.append(img.resize((target_width, h_size), Image.Resampling.LANCZOS))
        else:
            resized_imgs.append(img)

    # --- 2. MASONRY LAYOUT ---
    col_heights = [0] * num_columns
    canvas_w = (target_width * num_columns) + (spacing * (num_columns + 1))

    positions = []
    for img in resized_imgs:
        short_col = col_heights.index(min(col_heights))
        x = spacing + (short_col * (target_width + spacing))
        y = spacing + col_heights[short_col]
        positions.append((x, y))
        col_heights[short_col] += img.size[1] + spacing

    canvas_h = max(col_heights) + spacing
    collage = Image.new('RGBA', (canvas_w, canvas_h), (bg_color[0], bg_color[1], bg_color[2], 255))

    for img, pos in zip(resized_imgs, positions):
        collage.paste(img, pos, img)

    # --- 3. WATERMARK OVERLAY ---
    if watermark_text:
        watermark_layer = Image.new('RGBA', (canvas_w * 2, canvas_h * 2), (0,0,0,0))
        draw = ImageDraw.Draw(watermark_layer)

        # Scale watermark adaptively so it doesn't look tiny on high-res collages
        scale_factor = target_width / 450.0
        actual_watermark_size = int(watermark_size * scale_factor)

        try:
            font = ImageFont.truetype("arial.ttf", actual_watermark_size)
        except Exception:
            # Fallback for Linux where Arial might not be present, we can try Dejavu or default
            try:
                font = ImageFont.truetype("DejaVuSans-Bold.ttf", actual_watermark_size)
            except Exception:
                font = ImageFont.load_default()

        # Repeating grid - scale step sizes adaptively
        step_y = max(int(300 * scale_factor), actual_watermark_size * 4)
        step_x = max(int(400 * scale_factor), actual_watermark_size * 5)

        for y in range(0, watermark_layer.height, step_y):
            for x in range(0, watermark_layer.width, step_x):
                fill_color = (watermark_color[0], watermark_color[1], watermark_color[2], watermark_opacity)
                draw.text((x, y), watermark_text, fill=fill_color, font=font)

        watermark_layer = watermark_layer.rotate(25, expand=False)

        # Crop the watermark layer to match the collage size
        left = (watermark_layer.width - canvas_w) // 2
        top = (watermark_layer.height - canvas_h) // 2
        watermark_final = watermark_layer.crop((left, top, left + canvas_w, top + canvas_h))

        # Merge layers
        final_output = Image.alpha_composite(collage, watermark_final)
    else:
        final_output = collage

    # Return as BytesIO
    output_buffer = BytesIO()
    final_output.save(output_buffer, "PNG")
    output_buffer.seek(0)
    return output_buffer

@router.post("/api/collage/generate")
async def generate_collage(
    files: list[UploadFile] = File(...),
    num_columns: int = Form(4),
    watermark_text: str = Form(""),
    blur_images: bool = Form(False),
    blur_radius: int = Form(5),
    bg_color_hex: str = Form("#0A0A0A"),
    watermark_color_hex: str = Form("#FFA500"),
    watermark_opacity: int = Form(60),
    watermark_size: int = Form(45)
):
    try:
        images_data = []
        for file in files:
            data = await file.read()
            images_data.append(data)
            
        bg_rgb = hex_to_rgb(bg_color_hex)
        watermark_rgb = hex_to_rgb(watermark_color_hex)
            
        output_buffer = create_pro_collage(
            images=images_data,
            num_columns=num_columns,
            watermark_text=watermark_text,
            blur_images=blur_images,
            blur_radius=blur_radius,
            bg_color=bg_rgb,
            watermark_color=watermark_rgb,
            watermark_opacity=watermark_opacity,
            watermark_size=watermark_size
        )
        
        return StreamingResponse(
            output_buffer, 
            media_type="image/png",
            headers={"Content-Disposition": 'attachment; filename="collage.png"'}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/debunk")
async def generate_debunk(
    file: UploadFile = File(...),
    color_hex: str = Form("#FF0000"),
    thickness: float = Form(3.0)
):
    try:
        data = await file.read()
        img = Image.open(BytesIO(data)).convert("RGBA")
        
        # Calculate thickness based on image size (e.g. percentage of max dimension)
        diag_thickness = int(max(img.width, img.height) * (thickness / 100.0))
        if diag_thickness < 1:
            diag_thickness = 1
            
        # SUPERSAMPLING FOR ANTI-ALIASING
        scale = 4
        ss_width = img.width * scale
        ss_height = img.height * scale
        ss_thickness = diag_thickness * scale
        
        # Create a large transparent overlay
        overlay = Image.new("RGBA", (ss_width, ss_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        fill_color = (*hex_to_rgb(color_hex), 255)
        
        # Draw cross (X) on the large overlay
        draw.line([(0, 0), (ss_width, ss_height)], fill=fill_color, width=ss_thickness)
        draw.line([(ss_width, 0), (0, ss_height)], fill=fill_color, width=ss_thickness)
        
        # Resize overlay down using Lanczos resampling (this creates perfectly smooth anti-aliased lines)
        overlay = overlay.resize((img.width, img.height), Image.Resampling.LANCZOS)
        
        # Combine the smooth overlay with the original image
        img = Image.alpha_composite(img, overlay)
        
        output_buffer = BytesIO()
        img.save(output_buffer, "PNG")
        output_buffer.seek(0)
        
        return StreamingResponse(
            output_buffer,
            media_type="image/png",
            headers={"Content-Disposition": 'attachment; filename="debunked.png"'}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
