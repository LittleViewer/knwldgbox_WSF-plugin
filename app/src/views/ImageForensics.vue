<script setup>
import { ref, watch, shallowRef, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { Aperture, Search, Activity, Sun, Copy, Info, UploadCloud, X, ZoomIn, Sliders } from 'lucide-vue-next'
import exifr from 'exifr'
import { processELA, processNoise, processLuminance, processPCA, processClone } from '../utils/imageForensics'

const { t } = useI18n()

const imageFile = ref(null)
const imageUrl = ref('')
const metadata = ref(null)
const activeTool = ref('metadata')
const isProcessing = ref(false)

const tools = [
  { id: 'metadata', name: 'EXIF Metadata', icon: Info },
  { id: 'magnifier', name: 'Magnifier', icon: ZoomIn },
  { id: 'ela', name: 'Error Level Analysis', icon: Aperture },
  { id: 'noise', name: 'Noise Analysis', icon: Activity },
  { id: 'luminance', name: 'Luminance Gradient', icon: Sun },
  { id: 'pca', name: 'Principal Component Analysis', icon: Activity },
  { id: 'clone', name: 'Clone Sweep', icon: Copy }
]

const canvasRef = ref(null)
const magCanvasRef = ref(null)
const imageObj = shallowRef(null)

// ELA settings
const elaQuality = ref(74)
const elaErrorScale = ref(20)
const elaOpacity = ref(0.95)
const elaMagEnhancement = ref('Auto Contrast')

// Noise Settings
const noiseAmplitude = ref(1)
const noiseEqualize = ref(true)
const noiseOpacity = ref(0.95)
const noiseMagEnhancement = ref('None')

// Other Settings
const magnifierZoom = ref(3)
const cloneThreshold = ref(15)

// Luminance Settings
const lumEqualize = ref(false)
const lumNormalize = ref(true)
const lumIntensity = ref(5.98)
const lumOpacity = ref(0.54)

// PCA Settings
const pcaInput = ref('Color')
const pcaMode = ref('Projection')
const pcaComponent = ref(2)
const pcaLinearize = ref(false)
const pcaInvert = ref(false)
const pcaEnhancement = ref('Equalize Histogram')
const pcaOpacity = ref(1.00)

const magnifierOptions = ['None', 'Auto Contrast']

// Magnifier state
const magX = ref(0)
const magY = ref(0)
const showMag = ref(false)

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  imageFile.value = file
  imageUrl.value = URL.createObjectURL(file)
  
  // Extract EXIF
  try {
    const ex = await exifr.parse(file, true)
    metadata.value = ex || { message: 'No EXIF metadata found in this image.' }
  } catch (err) {
    metadata.value = { error: 'Failed to extract metadata. File might not contain valid EXIF.' }
  }

  const img = new Image()
  img.onload = () => {
    imageObj.value = img
    applyTool()
  }
  img.src = imageUrl.value
}

const clearImage = () => {
  imageFile.value = null
  imageUrl.value = ''
  metadata.value = null
  imageObj.value = null
  if (canvasRef.value) {
    const ctx = canvasRef.value.getContext('2d')
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  }
}

watch(activeTool, () => {
  applyTool()
})
watch([
  elaQuality, elaErrorScale, elaOpacity, 
  noiseAmplitude, noiseEqualize, noiseOpacity, 
  cloneThreshold, lumEqualize, lumNormalize, lumIntensity, lumOpacity,
  pcaInput, pcaMode, pcaComponent, pcaLinearize, pcaInvert, pcaEnhancement, pcaOpacity
], () => {
  if (activeTool.value !== 'magnifier' && activeTool.value !== 'metadata') {
    applyTool()
  }
})

const applyTool = () => {
  if (!imageObj.value || !canvasRef.value) return
  
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  
  // Set canvas size to image size
  canvas.width = imageObj.value.width
  canvas.height = imageObj.value.height
  
  if (activeTool.value === 'metadata' || activeTool.value === 'magnifier') {
    ctx.drawImage(imageObj.value, 0, 0)
    return
  }
  
  isProcessing.value = true
  
  setTimeout(() => {
    if (activeTool.value === 'ela') {
      processELA(imageObj.value, canvas, ctx, {
        elaQuality: elaQuality.value,
        elaErrorScale: elaErrorScale.value,
        elaOpacity: elaOpacity.value
      })
    } else if (activeTool.value === 'noise') {
      processNoise(imageObj.value, canvas, ctx, {
        noiseAmplitude: noiseAmplitude.value,
        noiseEqualize: noiseEqualize.value,
        noiseOpacity: noiseOpacity.value
      })
    } else if (activeTool.value === 'luminance') {
      processLuminance(imageObj.value, canvas, ctx, {
        lumIntensity: lumIntensity.value,
        lumNormalize: lumNormalize.value,
        lumEqualize: lumEqualize.value,
        lumOpacity: lumOpacity.value
      })
    } else if (activeTool.value === 'pca') {
      processPCA(imageObj.value, canvas, ctx, {
        pcaInput: pcaInput.value,
        pcaMode: pcaMode.value,
        pcaComponent: pcaComponent.value,
        pcaLinearize: pcaLinearize.value,
        pcaInvert: pcaInvert.value,
        pcaEnhancement: pcaEnhancement.value,
        pcaOpacity: pcaOpacity.value
      })
    } else if (activeTool.value === 'clone') {
      processClone(imageObj.value, canvas, ctx, {
        cloneThreshold: cloneThreshold.value
      })
    }
    isProcessing.value = false
  }, 50)
}

const handleMouseMove = (e) => {
  if (activeTool.value === 'metadata' || !canvasRef.value) return
  const rect = canvasRef.value.getBoundingClientRect()
  const scaleX = canvasRef.value.width / rect.width
  const scaleY = canvasRef.value.height / rect.height
  magX.value = (e.clientX - rect.left) * scaleX
  magY.value = (e.clientY - rect.top) * scaleY

  updateMagnifier()
}

const updateMagnifier = () => {
  if (!showMag.value || !magCanvasRef.value || !canvasRef.value) return
  const mCtx = magCanvasRef.value.getContext('2d')
  mCtx.clearRect(0, 0, 150, 150)
  
  const z = magnifierZoom.value
  const sw = 150 / z
  const sh = 150 / z
  const sx = magX.value - sw / 2
  const sy = magY.value - sh / 2

  mCtx.imageSmoothingEnabled = false
  mCtx.drawImage(canvasRef.value, sx, sy, sw, sh, 0, 0, 150, 150)

  // Determine enhancement mode based on tool
  let enhancement = 'None'
  if (activeTool.value === 'ela') enhancement = elaMagEnhancement.value
  else if (activeTool.value === 'noise') enhancement = noiseMagEnhancement.value
  else if (activeTool.value === 'magnifier') enhancement = 'None' // Magnifier tool itself

  if (enhancement === 'Auto Contrast') {
    const imgData = mCtx.getImageData(0, 0, 150, 150)
    const data = imgData.data
    let min = 255, max = 0
    for(let i=0; i<data.length; i+=4) {
      if(data[i] < min) min = data[i]
      if(data[i] > max) max = data[i]
    }
    if (max > min) {
      for(let i=0; i<data.length; i+=4) {
        data[i] = ((data[i] - min) / (max - min)) * 255
        data[i+1] = ((data[i+1] - min) / (max - min)) * 255
        data[i+2] = ((data[i+2] - min) / (max - min)) * 255
      }
      mCtx.putImageData(imgData, 0, 0)
    }
  }
}

watch(showMag, (val) => {
  if (val) nextTick(() => updateMagnifier())
})

const formatValue = (val) => {
  if (typeof val === 'object') return JSON.stringify(val)
  return val
}
</script>

<template>
  <div class="forensics-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ t('sidebar.imageForensics') || 'Image Forensics' }}</h1>
        <p class="page-subtitle">Analyze images with ELA, noise extraction, luminance gradients, and EXIF extraction.</p>
      </div>
    </div>

    <div class="main-content">
      <!-- Workspace -->
      <div class="workspace">
        
        <!-- Canvas View (Left side) -->
        <div class="analysis-view glass-panel">
          <div v-if="!imageUrl" class="upload-zone" @click="$refs.fileInput.click()">
            <UploadCloud size="48" class="text-orange" />
            <h3>Upload Image for Forensics</h3>
            <p class="text-muted">Supports JPEG, PNG, WEBP. Data remains entirely in your browser.</p>
            <input type="file" ref="fileInput" accept="image/*" @change="handleFileUpload" style="display: none">
          </div>

          <template v-else>
            <div class="canvas-header">
              <h3>{{ tools.find(t => t.id === activeTool)?.name }}</h3>
              <div class="canvas-actions">
                <span v-if="isProcessing" class="processing-badge">Processing...</span>
                <button class="icon-btn" @click="clearImage" title="Clear Image"><X size="18" /></button>
              </div>
            </div>
            
            <div v-show="activeTool !== 'metadata'"
              class="canvas-container" 
              @mousemove="handleMouseMove"
              @mouseenter="showMag = true"
              @mouseleave="showMag = false"
            >
              <canvas ref="canvasRef" class="main-canvas"></canvas>
              
              <!-- Magnifier overlay using real canvas -->
              <canvas 
                v-show="activeTool !== 'metadata' && showMag" 
                ref="magCanvasRef"
                class="magnifier-glass"
                :style="{
                  left: `calc(${magX * (100 / canvasRef?.width || 1)}% - 75px)`,
                  top: `calc(${magY * (100 / canvasRef?.height || 1)}% - 75px)`
                }"
                width="150" height="150"
              ></canvas>
            </div>

            <!-- Metadata View -->
            <div v-if="activeTool === 'metadata'" class="metadata-panel">
              <div v-if="metadata && Object.keys(metadata).length > 0" class="meta-grid">
                <div v-for="(value, key) in metadata" :key="key" class="meta-item">
                  <span class="meta-key">{{ key }}</span>
                  <span class="meta-value">{{ formatValue(value) }}</span>
                </div>
              </div>
              <div v-else class="no-meta">
                <Info size="24" class="text-muted" />
                <p>No EXIF data found or image format not supported.</p>
              </div>
            </div>
          </template>
        </div>

        <!-- Settings Sidebar (Right side, Accordion) -->
        <div v-if="imageUrl" class="settings-sidebar glass-panel">
          
          <div v-for="tool in tools" :key="tool.id" class="accordion-section">
            <div 
              class="accordion-header"
              :class="{ active: activeTool === tool.id }"
              @click="activeTool = tool.id"
            >
              {{ tool.name }}
            </div>
            
            <div v-show="activeTool === tool.id" class="accordion-content">
              
              <!-- ELA Settings -->
              <div v-if="tool.id === 'ela'" class="settings-panel">
                <div class="setting-item">
                  <div class="setting-header">
                    <label>JPEG Quality</label>
                    <span class="val">{{ elaQuality }}</span>
                  </div>
                  <input type="range" v-model="elaQuality" min="1" max="100" class="range-slider">
                </div>
                <div class="setting-item">
                  <div class="setting-header">
                    <label>Error Scale</label>
                    <span class="val">{{ elaErrorScale }}</span>
                  </div>
                  <input type="range" v-model="elaErrorScale" min="1" max="100" class="range-slider">
                </div>
                <div class="setting-item">
                  <label>Magnifier Enhancement</label>
                  <select v-model="elaMagEnhancement" class="dropdown-select">
                    <option v-for="opt in magnifierOptions" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
                <div class="setting-item">
                  <div class="setting-header">
                    <label>Opacity</label>
                    <span class="val">{{ elaOpacity }}</span>
                  </div>
                  <input type="range" v-model="elaOpacity" min="0" max="1" step="0.01" class="range-slider">
                </div>
              </div>

              <!-- Noise Settings -->
              <div v-if="tool.id === 'noise'" class="settings-panel">
                <div class="setting-item">
                  <div class="setting-header">
                    <label>Noise Amplitude</label>
                    <span class="val">{{ noiseAmplitude }}</span>
                  </div>
                  <input type="range" v-model="noiseAmplitude" min="1" max="50" step="0.5" class="range-slider">
                </div>
                <div class="setting-item checkbox-item">
                  <label>Equalize Histogram</label>
                  <input type="checkbox" v-model="noiseEqualize" class="custom-checkbox">
                </div>
                <div class="setting-item">
                  <label>Magnifier Enhancement</label>
                  <select v-model="noiseMagEnhancement" class="dropdown-select">
                    <option v-for="opt in magnifierOptions" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
                <div class="setting-item">
                  <div class="setting-header">
                    <label>Opacity</label>
                    <span class="val">{{ noiseOpacity }}</span>
                  </div>
                  <input type="range" v-model="noiseOpacity" min="0" max="1" step="0.01" class="range-slider">
                </div>
              </div>

              <!-- Luminance Settings -->
              <div v-if="tool.id === 'luminance'" class="settings-panel">
                <div class="setting-item checkbox-item">
                  <label>Equalize Histogram</label>
                  <input type="checkbox" v-model="lumEqualize" class="custom-checkbox">
                </div>
                <div class="setting-item checkbox-item">
                  <label>Normalize</label>
                  <input type="checkbox" v-model="lumNormalize" class="custom-checkbox">
                </div>
                <div class="setting-item">
                  <div class="setting-header">
                    <label>Intensity</label>
                    <span class="val">{{ lumIntensity }}</span>
                  </div>
                  <input type="range" v-model="lumIntensity" min="0.1" max="20" step="0.01" class="range-slider">
                </div>
                <div class="setting-item">
                  <div class="setting-header">
                    <label>Opacity</label>
                    <span class="val">{{ lumOpacity }}</span>
                  </div>
                  <input type="range" v-model="lumOpacity" min="0" max="1" step="0.01" class="range-slider">
                </div>
              </div>

              <!-- PCA Settings -->
              <div v-if="tool.id === 'pca'" class="settings-panel">
                <div class="setting-item">
                  <label>Input</label>
                  <select v-model="pcaInput" class="dropdown-select">
                    <option value="Color">Color</option>
                    <option value="Luminance Gradient">Luminance Gradient</option>
                  </select>
                </div>
                <div class="setting-item">
                  <label>Mode</label>
                  <select v-model="pcaMode" class="dropdown-select">
                    <option value="Projection">Projection</option>
                    <option value="Difference">Difference</option>
                    <option value="Distance">Distance</option>
                    <option value="Component">Component</option>
                  </select>
                </div>
                <div class="setting-item">
                  <div class="setting-header">
                    <label>Component</label>
                    <span class="val">{{ pcaComponent }}</span>
                  </div>
                  <input type="range" v-model="pcaComponent" min="1" max="3" class="range-slider">
                </div>
                <div class="setting-item checkbox-item">
                  <label>Linearize</label>
                  <input type="checkbox" v-model="pcaLinearize" class="custom-checkbox">
                </div>
                <div class="setting-item checkbox-item">
                  <label>Invert</label>
                  <input type="checkbox" v-model="pcaInvert" class="custom-checkbox">
                </div>
                <div class="setting-item">
                  <label>Enhancement</label>
                  <select v-model="pcaEnhancement" class="dropdown-select">
                    <option value="Equalize Histogram">Equalize Histogram</option>
                    <option value="Stretch Contrast">Stretch Contrast</option>
                    <option value="None">None</option>
                  </select>
                </div>
                <div class="setting-item">
                  <div class="setting-header">
                    <label>Opacity</label>
                    <span class="val">{{ pcaOpacity }}</span>
                  </div>
                  <input type="range" v-model="pcaOpacity" min="0" max="1" step="0.01" class="range-slider">
                </div>
              </div>

              <!-- Clone Settings -->
              <div v-if="tool.id === 'clone'" class="settings-panel">
                <div class="setting-item">
                  <div class="setting-header">
                    <label>Pattern Threshold</label>
                    <span class="val">{{ cloneThreshold }}</span>
                  </div>
                  <input type="range" v-model="cloneThreshold" min="1" max="100" class="range-slider">
                </div>
              </div>

              <!-- Magnifier Settings -->
              <div v-if="tool.id === 'magnifier'" class="settings-panel">
                <div class="setting-item">
                  <div class="setting-header">
                    <label>Zoom Level</label>
                    <span class="val">{{ magnifierZoom }}x</span>
                  </div>
                  <input type="range" v-model="magnifierZoom" min="1" max="10" class="range-slider">
                </div>
              </div>

              <!-- Meta Data (No specific controls needed, handled in left view) -->
              <div v-if="tool.id === 'metadata'" class="settings-panel">
                <p class="text-muted" style="font-size: 0.85rem;">Metadata details are displayed in the main view.</p>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.forensics-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 24px;
  gap: 24px;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  flex: 1;
  min-height: 0;
}

.accordion-section {
  border-bottom: 1px solid var(--border-color);
}
.accordion-header {
  padding: 14px 20px;
  cursor: pointer;
  font-size: 0.95rem;
  color: var(--text-muted);
  background: var(--bg-panel);
  transition: all 0.2s;
  user-select: none;
}
.accordion-header:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-main);
}
.accordion-header.active {
  color: var(--text-main);
  background: rgba(var(--accent-rgb), 0.1);
  border-left: 3px solid var(--accent-orange);
}
.accordion-content {
  background: rgba(0, 0, 0, 0.2);
}

.workspace {
  flex: 1;
  display: flex;
  gap: 24px;
  min-height: 0;
}

.upload-zone {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  cursor: pointer;
  border: 2px dashed var(--border-color);
  transition: var(--transition-base);
}

.upload-zone:hover {
  border-color: var(--accent-orange);
  background: rgba(var(--accent-rgb), 0.05);
}

.settings-sidebar {
  width: 320px;
  padding: 0;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  background: var(--bg-panel);
  overflow-y: auto;
  border-left: 1px solid var(--border-color);
}

.settings-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 16px 20px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.setting-item label {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.setting-item .val {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-family: monospace;
}

.checkbox-item {
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.range-slider {
  width: 100%;
  accent-color: var(--accent-orange);
}

.dropdown-select {
  width: 100%;
  background: var(--bg-dark);
  color: var(--text-main);
  border: 1px solid var(--border-color);
  padding: 8px;
  border-radius: var(--radius-global);
  outline: none;
}

.dropdown-select:focus {
  border-color: var(--accent-orange);
}

.custom-checkbox {
  accent-color: var(--accent-orange);
  width: 16px;
  height: 16px;
}

.analysis-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: 16px;
}

.canvas-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.processing-badge {
  font-size: 0.75rem;
  color: var(--accent-orange);
  background: rgba(var(--accent-rgb), 0.1);
  padding: 4px 8px;
  border-radius: var(--radius-global);
  animation: pulse 1.5s infinite;
}

.canvas-container {
  position: relative;
  width: 100%;
  flex: 1;
  overflow: hidden;
  display: flex;
  justify-content: center;
  background: var(--bg-dark);
  border: 1px solid var(--border-color);
}

.main-canvas {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.magnifier-glass {
  position: absolute;
  width: 150px;
  height: 150px;
  border: 2px solid var(--accent-orange);
  border-radius: 50%;
  pointer-events: none;
  box-shadow: 0 0 15px rgba(0,0,0,0.8);
  background: #000;
  z-index: 10;
}

.metadata-panel {
  flex: 1;
  overflow-y: auto;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  background: var(--bg-dark);
  padding: 12px;
  border: 1px solid var(--border-color);
  border-left: 3px solid var(--accent-orange);
}

.meta-key {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-bottom: 4px;
}

.meta-value {
  font-size: 0.95rem;
  color: var(--text-main);
  word-break: break-all;
}

.no-meta {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  gap: 16px;
  color: var(--text-muted);
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

@media (max-width: 768px) {
  .forensics-container {
    padding: 12px;
    height: auto;
    min-height: 100%;
  }
  .workspace {
    flex-direction: column;
    gap: 16px;
  }
  .analysis-view {
    min-height: 400px;
  }
  .settings-sidebar {
    width: 100%;
    border-left: none;
    border-top: 1px solid var(--border-color);
  }
  .meta-grid {
    grid-template-columns: 1fr;
  }
}
</style>
