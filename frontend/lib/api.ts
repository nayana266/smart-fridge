// API utilities for Smart Fridge frontend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface PresignedUploadResponse {
  uploadUrl: string
  key: string
  expiresIn: number
}

export interface AnalysisRequest {
  imageKeys: string[]
  peopleCount: number
  inventory?: any[]
}

export interface AnalysisResponse {
  inventory: any[]
  recipes: any[]
  swapTips: any[]
  totalCarbonImpact: number
  analysisTime: number
}

// Get presigned upload URL for S3
export async function getPresignedUploadUrl(
  fileName: string,
  fileType: string
): Promise<PresignedUploadResponse> {
  console.log('Getting presigned URL for:', fileName, fileType)
  console.log('API Base URL:', API_BASE_URL)
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/presign`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        fileName,
        fileType,
      }),
    })

    console.log('Presign response status:', response.status)

    if (!response.ok) {
      const errorText = await response.text()
      console.error('Presign failed:', response.status, errorText)
      throw new Error(`Failed to get presigned URL: ${response.status} ${response.statusText} - ${errorText}`)
    }

    const result = await response.json()
    console.log('Got presigned URL successfully')
    return result
  } catch (error) {
    console.error('Presign error:', error)
    throw error
  }
}

// Upload file directly to S3 using presigned URL
export async function uploadToS3(
  file: File,
  presignedUrl: string
): Promise<void> {
  console.log('Starting S3 upload for:', file.name)
  console.log('Presigned URL:', presignedUrl.substring(0, 100) + '...')
  
  try {
    const response = await fetch(presignedUrl, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': file.type,
      },
    })

    console.log('S3 upload response status:', response.status)
    console.log('S3 upload response headers:', Object.fromEntries(response.headers.entries()))

    if (!response.ok) {
      const errorText = await response.text()
      console.error('S3 upload failed:', response.status, errorText)
      throw new Error(`Failed to upload to S3: ${response.status} ${response.statusText} - ${errorText}`)
    }
    
    console.log('S3 upload successful!')
  } catch (error) {
    console.error('S3 upload error:', error)
    throw error
  }
}

// Analyze uploaded images
export async function analyzeImages(
  imageKeys: string[],
  peopleCount: number,
  inventory?: any[]
): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      imageKeys,
      peopleCount,
      inventory,
    }),
  })

  if (!response.ok) {
    throw new Error(`Failed to analyze images: ${response.statusText}`)
  }

  return response.json()
}

// Health check
export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`)
    return response.ok
  } catch {
    return false
  }
}

// Demo mode - returns mock data
export function getMockAnalysisResults(): AnalysisResponse {
  return {
    inventory: [
      {
        id: '1',
        name: 'Organic Tomatoes',
        category: 'Vegetables',
        quantity: '6 pieces',
        carbonImpact: 'low',
        confidence: 0.92
      },
      {
        id: '2',
        name: 'Ground Beef',
        category: 'Meat',
        quantity: '1 lb',
        carbonImpact: 'high',
        confidence: 0.88
      },
      {
        id: '3',
        name: 'Milk',
        category: 'Dairy',
        quantity: '1 gallon',
        carbonImpact: 'medium',
        confidence: 0.95
      }
    ],
    recipes: [
      {
        id: '1',
        title: 'Beef Bolognese',
        description: 'Classic Italian pasta with ground beef and tomatoes',
        ingredients: ['Ground beef', 'Tomatoes', 'Onion', 'Garlic', 'Pasta'],
        instructions: [
          'Brown the ground beef in a large pan',
          'Add diced onions and garlic',
          'Add tomatoes and simmer for 20 minutes',
          'Serve over cooked pasta'
        ],
        carbonImpact: 'high',
        prepTime: 30,
        servings: 4,
        imageUrl: '/api/placeholder/400/300'
      },
      {
        id: '2',
        title: 'Tomato Basil Salad',
        description: 'Fresh and light salad with tomatoes and basil',
        ingredients: ['Tomatoes', 'Fresh basil', 'Olive oil', 'Salt', 'Pepper'],
        instructions: [
          'Slice tomatoes',
          'Chop fresh basil',
          'Drizzle with olive oil',
          'Season with salt and pepper'
        ],
        carbonImpact: 'low',
        prepTime: 10,
        servings: 2,
        imageUrl: '/api/placeholder/400/300'
      }
    ],
    swapTips: [
      {
        id: '1',
        original: 'Ground Beef',
        suggestion: 'Lentils',
        reason: 'Plant-based protein with 90% less carbon footprint',
        carbonSavings: 85
      }
    ],
    totalCarbonImpact: 2.3,
    analysisTime: 8.5
  }
}


