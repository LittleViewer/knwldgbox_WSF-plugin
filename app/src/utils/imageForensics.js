export const processELA = (imageObj, canvas, ctx, config) => {
  const originalCanvas = document.createElement('canvas')
  originalCanvas.width = canvas.width
  originalCanvas.height = canvas.height
  const oCtx = originalCanvas.getContext('2d')
  oCtx.drawImage(imageObj, 0, 0)
  
  const jpegUrl = originalCanvas.toDataURL('image/jpeg', config.elaQuality / 100)
  const img2 = new Image()
  img2.onload = () => {
    const tempCanvas = document.createElement('canvas')
    tempCanvas.width = canvas.width
    tempCanvas.height = canvas.height
    const tCtx = tempCanvas.getContext('2d')
    tCtx.drawImage(img2, 0, 0)
    
    const origData = oCtx.getImageData(0, 0, canvas.width, canvas.height).data
    const newData = tCtx.getImageData(0, 0, canvas.width, canvas.height).data
    const outData = ctx.createImageData(canvas.width, canvas.height)
    
    const mult = config.elaErrorScale
    for (let i = 0; i < origData.length; i += 4) {
      outData.data[i] = Math.min(255, Math.abs(origData[i] - newData[i]) * mult)
      outData.data[i+1] = Math.min(255, Math.abs(origData[i+1] - newData[i+1]) * mult)
      outData.data[i+2] = Math.min(255, Math.abs(origData[i+2] - newData[i+2]) * mult)
      outData.data[i+3] = 255
    }
    
    const resultCanvas = document.createElement('canvas')
    resultCanvas.width = canvas.width
    resultCanvas.height = canvas.height
    resultCanvas.getContext('2d').putImageData(outData, 0, 0)
    
    ctx.globalAlpha = 1.0
    ctx.drawImage(imageObj, 0, 0)
    ctx.globalAlpha = config.elaOpacity
    ctx.drawImage(resultCanvas, 0, 0)
    ctx.globalAlpha = 1.0
  }
  img2.src = jpegUrl
}

export const processNoise = (imageObj, canvas, ctx, config) => {
  const originalCanvas = document.createElement('canvas')
  originalCanvas.width = canvas.width
  originalCanvas.height = canvas.height
  const oCtx = originalCanvas.getContext('2d')
  oCtx.drawImage(imageObj, 0, 0)
  const imgData = oCtx.getImageData(0, 0, canvas.width, canvas.height)
  const data = imgData.data
  
  const outData = ctx.createImageData(canvas.width, canvas.height)
  const w = canvas.width
  const mult = config.noiseAmplitude

  const noiseVals = new Uint8Array(canvas.width * canvas.height)

  for (let y = 1; y < canvas.height - 1; y++) {
    for (let x = 1; x < canvas.width - 1; x++) {
      const idx = (y * w + x) * 4
      
      const top = ((y - 1) * w + x) * 4
      const bottom = ((y + 1) * w + x) * 4
      const left = (y * w + (x - 1)) * 4
      const right = (y * w + (x + 1)) * 4

      let totalDiff = 0
      for (let c = 0; c < 3; c++) {
        const avg = (data[top+c] + data[bottom+c] + data[left+c] + data[right+c]) / 4
        const diff = Math.min(255, Math.abs(data[idx+c] - avg) * mult)
        outData.data[idx+c] = diff
        totalDiff += diff
      }
      outData.data[idx+3] = 255
      noiseVals[y*w + x] = Math.min(255, totalDiff / 3)
    }
  }

  if (config.noiseEqualize) {
    const hist = new Array(256).fill(0)
    for (let i = 0; i < noiseVals.length; i++) {
      hist[Math.floor(noiseVals[i])]++
    }
    const cdf = new Array(256).fill(0)
    cdf[0] = hist[0]
    for (let i = 1; i < 256; i++) {
      cdf[i] = cdf[i-1] + hist[i]
    }
    const cdfMin = cdf.find(v => v > 0) || 1
    const totalPixels = canvas.width * canvas.height
    const map = new Array(256)
    for (let i = 0; i < 256; i++) {
      map[i] = Math.round(((cdf[i] - cdfMin) / (totalPixels - cdfMin)) * 255)
    }

    for (let y = 1; y < canvas.height - 1; y++) {
      for (let x = 1; x < canvas.width - 1; x++) {
        const idx = (y * w + x) * 4
        outData.data[idx] = map[Math.min(255, Math.floor(outData.data[idx]))]
        outData.data[idx+1] = map[Math.min(255, Math.floor(outData.data[idx+1]))]
        outData.data[idx+2] = map[Math.min(255, Math.floor(outData.data[idx+2]))]
      }
    }
  }

  const resultCanvas = document.createElement('canvas')
  resultCanvas.width = canvas.width
  resultCanvas.height = canvas.height
  resultCanvas.getContext('2d').putImageData(outData, 0, 0)
  
  ctx.globalAlpha = 1.0
  ctx.drawImage(imageObj, 0, 0)
  ctx.globalAlpha = config.noiseOpacity
  ctx.drawImage(resultCanvas, 0, 0)
  ctx.globalAlpha = 1.0
}

export const processLuminance = (imageObj, canvas, ctx, config) => {
  const originalCanvas = document.createElement('canvas')
  originalCanvas.width = canvas.width
  originalCanvas.height = canvas.height
  const oCtx = originalCanvas.getContext('2d')
  oCtx.drawImage(imageObj, 0, 0)
  const imgData = oCtx.getImageData(0, 0, canvas.width, canvas.height)
  const data = imgData.data
  
  const outData = ctx.createImageData(canvas.width, canvas.height)
  const w = canvas.width
  const intensity = config.lumIntensity
  
  const luma = new Float32Array(canvas.width * canvas.height)
  for(let i=0; i<data.length; i+=4) {
    luma[i/4] = 0.299 * data[i] + 0.587 * data[i+1] + 0.114 * data[i+2]
  }

  const resultVals = new Float32Array(canvas.width * canvas.height * 3)

  for (let y = 1; y < canvas.height - 1; y++) {
    for (let x = 1; x < canvas.width - 1; x++) {
      const idx = y * w + x
      
      const tl = luma[(y-1)*w + (x-1)], tc = luma[(y-1)*w + x], tr = luma[(y-1)*w + (x+1)]
      const l  = luma[y*w + (x-1)],                           r  = luma[y*w + (x+1)]
      const bl = luma[(y+1)*w + (x-1)], bc = luma[(y+1)*w + x], br = luma[(y+1)*w + (x+1)]

      let gx = (-tl + tr - 2*l + 2*r - bl + br) * intensity
      let gy = (-tl - 2*tc - tr + bl + 2*bc + br) * intensity
      let gz = 255.0

      if (config.lumNormalize) {
        const len = Math.sqrt(gx*gx + gy*gy + gz*gz) || 1
        gx /= len
        gy /= len
        gz /= len
      } else {
        gx /= 255.0
        gy /= 255.0
        gz /= 255.0
      }

      resultVals[idx*3] = gx
      resultVals[idx*3+1] = gy
      resultVals[idx*3+2] = gz
    }
  }

  if (config.lumEqualize) {
    let minX = 999, maxX = -999, minY = 999, maxY = -999;
    for (let i = 0; i < resultVals.length; i+=3) {
      if (resultVals[i] < minX) minX = resultVals[i]
      if (resultVals[i] > maxX) maxX = resultVals[i]
      if (resultVals[i+1] < minY) minY = resultVals[i+1]
      if (resultVals[i+1] > maxY) maxY = resultVals[i+1]
    }
    const rangeX = (maxX - minX) || 1;
    const rangeY = (maxY - minY) || 1;
    for (let i = 0; i < resultVals.length; i+=3) {
      resultVals[i] = ((resultVals[i] - minX) / rangeX) * 2.0 - 1.0;
      resultVals[i+1] = ((resultVals[i+1] - minY) / rangeY) * 2.0 - 1.0;
    }
  }

  for (let y = 1; y < canvas.height - 1; y++) {
    for (let x = 1; x < canvas.width - 1; x++) {
      const idx = y * w + x
      const outIdx = idx * 4
      
      outData.data[outIdx] = Math.min(255, Math.max(0, (resultVals[idx*3] + 1.0) * 127.5))
      outData.data[outIdx+1] = Math.min(255, Math.max(0, (resultVals[idx*3+1] + 1.0) * 127.5))
      outData.data[outIdx+2] = Math.min(255, Math.max(0, (resultVals[idx*3+2] + 1.0) * 127.5))
      outData.data[outIdx+3] = 255
    }
  }

  const resultCanvas = document.createElement('canvas')
  resultCanvas.width = canvas.width
  resultCanvas.height = canvas.height
  resultCanvas.getContext('2d').putImageData(outData, 0, 0)
  
  ctx.globalAlpha = 1.0
  ctx.drawImage(imageObj, 0, 0)
  ctx.globalAlpha = config.lumOpacity
  ctx.drawImage(resultCanvas, 0, 0)
  ctx.globalAlpha = 1.0
}

export const processPCA = (imageObj, canvas, ctx, config) => {
  const originalCanvas = document.createElement('canvas')
  originalCanvas.width = canvas.width
  originalCanvas.height = canvas.height
  const oCtx = originalCanvas.getContext('2d')
  oCtx.drawImage(imageObj, 0, 0)
  const imgData = oCtx.getImageData(0, 0, canvas.width, canvas.height)
  const data = imgData.data
  
  const w = canvas.width
  const h = canvas.height
  const N = w * h

  const features = new Float32Array(N * 3)
  if (config.pcaInput === 'Luminance Gradient') {
    const luma = new Float32Array(N)
    for (let i = 0; i < N; i++) {
      luma[i] = 0.299 * data[i*4] + 0.587 * data[i*4+1] + 0.114 * data[i*4+2]
    }
    for (let y = 1; y < h - 1; y++) {
      for (let x = 1; x < w - 1; x++) {
        const idx = y * w + x
        const tl = luma[(y-1)*w+(x-1)], tc = luma[(y-1)*w+x], tr = luma[(y-1)*w+(x+1)]
        const ml = luma[y*w+(x-1)],                            mr = luma[y*w+(x+1)]
        const bl = luma[(y+1)*w+(x-1)], bc = luma[(y+1)*w+x], br = luma[(y+1)*w+(x+1)]
        features[idx*3]   = -tl + tr - 2*ml + 2*mr - bl + br
        features[idx*3+1] = -tl - 2*tc - tr + bl + 2*bc + br
        features[idx*3+2] = luma[idx]
      }
    }
  } else {
    for (let i = 0; i < N; i++) {
      let r = data[i*4], g = data[i*4+1], b = data[i*4+2]
      if (config.pcaLinearize) {
        r = Math.pow(r / 255, 2.2) * 255
        g = Math.pow(g / 255, 2.2) * 255
        b = Math.pow(b / 255, 2.2) * 255
      }
      features[i*3]   = r
      features[i*3+1] = g
      features[i*3+2] = b
    }
  }

  let s0 = 0, s1 = 0, s2 = 0
  for (let i = 0; i < N; i++) {
    s0 += features[i*3]
    s1 += features[i*3+1]
    s2 += features[i*3+2]
  }
  const mean = [s0/N, s1/N, s2/N]

  let cov = [[0,0,0],[0,0,0],[0,0,0]]
  for (let i = 0; i < N; i++) {
    const d0 = features[i*3]   - mean[0]
    const d1 = features[i*3+1] - mean[1]
    const d2 = features[i*3+2] - mean[2]
    cov[0][0] += d0*d0; cov[0][1] += d0*d1; cov[0][2] += d0*d2
    cov[1][1] += d1*d1; cov[1][2] += d1*d2
    cov[2][2] += d2*d2
  }
  cov[1][0] = cov[0][1]; cov[2][0] = cov[0][2]; cov[2][1] = cov[1][2]

  const startVectors = [[1, 0.3, 0.5], [0.3, 1, 0.5], [0.5, 0.3, 1]]
  
  const powerIteration = (mat, startIdx) => {
    let v = startVectors[startIdx].slice()
    for (let iter = 0; iter < 30; iter++) {
      let nx = mat[0][0]*v[0] + mat[0][1]*v[1] + mat[0][2]*v[2]
      let ny = mat[1][0]*v[0] + mat[1][1]*v[1] + mat[1][2]*v[2]
      let nz = mat[2][0]*v[0] + mat[2][1]*v[1] + mat[2][2]*v[2]
      let norm = Math.sqrt(nx*nx + ny*ny + nz*nz)
      if (norm < 1e-10) return { v: [1, 0, 0], lambda: 0 }
      v = [nx/norm, ny/norm, nz/norm]
    }
    const lambda = v[0]*(mat[0][0]*v[0] + mat[0][1]*v[1] + mat[0][2]*v[2]) +
                   v[1]*(mat[1][0]*v[0] + mat[1][1]*v[1] + mat[1][2]*v[2]) +
                   v[2]*(mat[2][0]*v[0] + mat[2][1]*v[1] + mat[2][2]*v[2])
    return { v, lambda: Math.abs(lambda) }
  }

  const deflate = (mat, eigenval, eigenvec) => {
    const out = [[0,0,0],[0,0,0],[0,0,0]]
    for (let i = 0; i < 3; i++) {
      for (let j = 0; j < 3; j++) {
        out[i][j] = mat[i][j] - eigenval * eigenvec[i] * eigenvec[j]
      }
    }
    return out
  }

  const e1 = powerIteration(cov, 0)
  const cov2 = deflate(cov, e1.lambda, e1.v)
  const e2 = powerIteration(cov2, 1)
  const cov3 = deflate(cov2, e2.lambda, e2.v)
  const e3 = powerIteration(cov3, 2)

  const eigens = [e1, e2, e3].sort((a, b) => b.lambda - a.lambda)
  const compIdx = Math.max(0, Math.min(2, config.pcaComponent - 1))
  const pc = eigens[compIdx].v

  const outData = ctx.createImageData(w, h)
  const isColor = config.pcaMode === 'Component'

  if (isColor) {
    const rBuf = new Float32Array(N * 3)
    let minR = [Infinity, Infinity, Infinity], maxR = [-Infinity, -Infinity, -Infinity]

    for (let i = 0; i < N; i++) {
      const d0 = features[i*3] - mean[0]
      const d1 = features[i*3+1] - mean[1]
      const d2 = features[i*3+2] - mean[2]
      let proj = d0*pc[0] + d1*pc[1] + d2*pc[2]
      if (config.pcaInvert) proj = -proj
      rBuf[i*3]   = proj * pc[0] + mean[0]
      rBuf[i*3+1] = proj * pc[1] + mean[1]
      rBuf[i*3+2] = proj * pc[2] + mean[2]
      for (let c = 0; c < 3; c++) {
        if (rBuf[i*3+c] < minR[c]) minR[c] = rBuf[i*3+c]
        if (rBuf[i*3+c] > maxR[c]) maxR[c] = rBuf[i*3+c]
      }
    }

    if (config.pcaEnhancement === 'Stretch Contrast') {
      for (let i = 0; i < N; i++) {
        for (let c = 0; c < 3; c++) {
          const rng = (maxR[c] - minR[c]) || 1
          outData.data[i*4+c] = Math.max(0, Math.min(255, ((rBuf[i*3+c] - minR[c]) / rng) * 255))
        }
        outData.data[i*4+3] = 255
      }
    } else {
      for (let i = 0; i < N; i++) {
        outData.data[i*4]   = Math.max(0, Math.min(255, Math.round(rBuf[i*3])))
        outData.data[i*4+1] = Math.max(0, Math.min(255, Math.round(rBuf[i*3+1])))
        outData.data[i*4+2] = Math.max(0, Math.min(255, Math.round(rBuf[i*3+2])))
        outData.data[i*4+3] = 255
      }
    }
  } else {
    const grayBuf = new Float32Array(N)
    let minG = Infinity, maxG = -Infinity

    for (let i = 0; i < N; i++) {
      const d0 = features[i*3] - mean[0]
      const d1 = features[i*3+1] - mean[1]
      const d2 = features[i*3+2] - mean[2]
      const proj = d0*pc[0] + d1*pc[1] + d2*pc[2]
      let val

      if (config.pcaMode === 'Difference') {
        const r0 = d0 - proj*pc[0]
        const r1 = d1 - proj*pc[1]
        const r2 = d2 - proj*pc[2]
        val = Math.sqrt(r0*r0 + r1*r1 + r2*r2)
      } else if (config.pcaMode === 'Distance') {
        val = Math.sqrt(d0*d0 + d1*d1 + d2*d2)
      } else {
        val = proj
      }

      if (config.pcaInvert) val = -val
      grayBuf[i] = val
      if (val < minG) minG = val
      if (val > maxG) maxG = val
    }

    const gRange = (maxG - minG) || 1

    if (config.pcaEnhancement === 'Equalize Histogram') {
      const scaled = new Uint8Array(N)
      const hist = new Array(256).fill(0)
      for (let i = 0; i < N; i++) {
        const v = Math.max(0, Math.min(255, Math.floor(((grayBuf[i] - minG) / gRange) * 255)))
        scaled[i] = v
        hist[v]++
      }
      const cdf = new Array(256)
      cdf[0] = hist[0]
      for (let i = 1; i < 256; i++) cdf[i] = cdf[i-1] + hist[i]
      const cdfMin = cdf.find(v => v > 0) || 1
      const lut = new Array(256)
      for (let i = 0; i < 256; i++) {
        lut[i] = Math.round(((cdf[i] - cdfMin) / (N - cdfMin)) * 255)
      }
      for (let i = 0; i < N; i++) {
        const v = lut[scaled[i]]
        outData.data[i*4] = v; outData.data[i*4+1] = v; outData.data[i*4+2] = v; outData.data[i*4+3] = 255
      }
    } else if (config.pcaEnhancement === 'Stretch Contrast') {
      for (let i = 0; i < N; i++) {
        const v = Math.max(0, Math.min(255, Math.round(((grayBuf[i] - minG) / gRange) * 255)))
        outData.data[i*4] = v; outData.data[i*4+1] = v; outData.data[i*4+2] = v; outData.data[i*4+3] = 255
      }
    } else {
      for (let i = 0; i < N; i++) {
        const v = Math.max(0, Math.min(255, Math.round(grayBuf[i] + 128)))
        outData.data[i*4] = v; outData.data[i*4+1] = v; outData.data[i*4+2] = v; outData.data[i*4+3] = 255
      }
    }
  }

  const resultCanvas = document.createElement('canvas')
  resultCanvas.width = w
  resultCanvas.height = h
  resultCanvas.getContext('2d').putImageData(outData, 0, 0)
  
  ctx.globalAlpha = 1.0
  ctx.drawImage(imageObj, 0, 0)
  ctx.globalAlpha = config.pcaOpacity
  ctx.drawImage(resultCanvas, 0, 0)
  ctx.globalAlpha = 1.0
}

export const processClone = (imageObj, canvas, ctx, config) => {
  ctx.drawImage(imageObj, 0, 0)
  const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height)
  const data = imgData.data
  const outData = ctx.createImageData(canvas.width, canvas.height)
  const w = canvas.width
  const th = config.cloneThreshold

  for (let y = 1; y < canvas.height - 1; y++) {
    for (let x = 1; x < canvas.width - 1; x++) {
      const idx = (y * w + x) * 4
      for (let c = 0; c < 3; c++) {
        const val = data[idx+c]
        const nb = data[((y)*w + (x+1))*4 + c]
        const diff = Math.abs(val - nb)
        outData.data[idx+c] = diff > th ? 255 : 0
      }
      outData.data[idx+3] = 255
    }
  }
  ctx.putImageData(outData, 0, 0)
}
