export interface ProductImages {
  main: string | null
  additional: string[]
}

export function extractImageUrls(productValue: Record<string, unknown>): ProductImages {
  const result: ProductImages = { main: null, additional: [] }
  if (!productValue) return result

  const mainCandidates = ['g:image_link', 'image_link', 'image', 'img']
  for (const key of mainCandidates) {
    const val = productValue[key]
    if (typeof val === 'string' && val.trim()) {
      result.main = val.trim()
      break
    }
  }

  if (!result.main) {
    const imgs = productValue['imgs']
    if (imgs && typeof imgs === 'object') {
      const imgsObj = imgs as Record<string, unknown>
      const main = imgsObj['main']
      if (main && typeof main === 'object') {
        const mainObj = main as Record<string, unknown>
        if (typeof mainObj['@url'] === 'string') {
          result.main = mainObj['@url']
        }
      } else if (typeof main === 'string') {
        result.main = main
      }
    }
  }

  const additionalCandidates = ['g:additional_image_link', 'additional_image_link']
  for (const key of additionalCandidates) {
    const val = productValue[key]
    if (typeof val === 'string' && val.trim()) {
      result.additional.push(val.trim())
    } else if (Array.isArray(val)) {
      for (const v of val) {
        if (typeof v === 'string' && v.trim()) {
          result.additional.push(v.trim())
        }
      }
    }
  }

  return result
}

export function isImageField(pathIn: string | null): boolean {
  if (!pathIn) return false
  const lower = pathIn.toLowerCase()
  return lower.includes('image') || lower.includes('img') || lower === 'imgs' || lower.includes('photo') || lower.includes('picture')
}
