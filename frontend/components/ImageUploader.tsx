'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X, Camera, CheckCircle, AlertCircle } from 'lucide-react'
import { UploadedImage } from '@/app/page'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { getPresignedUploadUrl, uploadToS3, getMockAnalysisResults } from '@/lib/api'

interface ImageUploaderProps {
  onImagesUploaded: (images: UploadedImage[]) => void
  isDemoMode: boolean
}

export function ImageUploader({ onImagesUploaded, isDemoMode }: ImageUploaderProps) {
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([])
  const [isUploading, setIsUploading] = useState(false)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    // Limit to 5 images max
    const filesToProcess = acceptedFiles.slice(0, 5)
    
    setIsUploading(true)
    
    const newImages: UploadedImage[] = filesToProcess.map((file, index) => ({
      id: `img-${Date.now()}-${index}`,
      file,
      preview: URL.createObjectURL(file),
      uploadProgress: 0,
    }))

    setUploadedImages(prev => [...prev, ...newImages])

    try {
      // Upload each file
      for (let i = 0; i < newImages.length; i++) {
        const imageId = newImages[i].id
        const file = newImages[i].file
        
        try {
          // Get presigned URL
          const { uploadUrl, key } = await getPresignedUploadUrl(
            file.name,
            file.type
          )
          
          // Update progress to 50%
          setUploadedImages(prev => 
            prev.map(img => 
              img.id === imageId 
                ? { ...img, uploadProgress: 50 }
                : img
            )
          )
          
          // Check if we're in demo mode (mock URL)
          if (uploadUrl.includes('demo=true')) {
            // In demo mode, skip actual S3 upload and simulate success
            await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate upload time
          } else {
            // Upload to S3 for real
            await uploadToS3(file, uploadUrl)
          }
          
          // Update progress to 100% and set S3 key
          setUploadedImages(prev => 
            prev.map(img => 
              img.id === imageId 
                ? { ...img, s3Key: key, uploadProgress: 100 }
                : img
            )
          )
        } catch (error) {
          console.error('Upload failed for', file.name, error)
          setUploadedImages(prev => 
            prev.map(img => 
              img.id === imageId 
                ? { ...img, error: 'Upload failed' }
                : img
            )
          )
        }
      }

      setIsUploading(false)
      toast.success(`${filesToProcess.length} image(s) uploaded successfully!`)
    } catch (error) {
      console.error('Upload process failed:', error)
      setIsUploading(false)
      toast.error('Upload failed. Please try again.')
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    maxFiles: 5,
    multiple: true
  })

  const removeImage = (imageId: string) => {
    setUploadedImages(prev => {
      const updated = prev.filter(img => img.id !== imageId)
      if (updated.length === 0) {
        onImagesUploaded([])
      }
      return updated
    })
  }

  const handleContinue = () => {
    if (uploadedImages.length > 0) {
      onImagesUploaded(uploadedImages)
    }
  }

  const canContinue = uploadedImages.length > 0 && uploadedImages.every(img => img.uploadProgress === 100)

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4 animate-bounce">
          <Camera className="w-8 h-8 text-white animate-pulse" />
        </div>
        <h1 className="text-3xl font-bold text-white mb-4">
          Upload Fridge Images
        </h1>
        <p className="text-lg text-white/90 mb-2">
          Take photos of your fridge contents to get AI-powered analysis
        </p>
        <p className="text-sm text-white/70">
          Upload up to 5 images • JPG, PNG, WebP supported
        </p>
        {isDemoMode && (
          <div className="mt-4 inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-gradient-to-r from-yellow-400 to-orange-500 text-white shadow-lg">
            <Camera className="w-4 h-4 mr-2" />
            Demo Mode
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
        {/* Upload Area */}
        <div className="space-y-6">
          <div
            {...getRootProps()}
            className={`
              relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300
              ${isDragActive 
                ? 'border-green-400 bg-green-50/20 backdrop-blur-sm' 
                : 'border-white/40 hover:border-white/60 hover:bg-white/5'
              }
              ${isUploading ? 'pointer-events-none opacity-50' : ''}
            `}
          >
            <input {...getInputProps()} />
            <div className="space-y-4">
              <div className="mx-auto w-16 h-16 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center">
                <Upload className="w-8 h-8 text-white" />
              </div>
              <div>
                <p className="text-lg font-medium text-white">
                  {isDragActive ? 'Drop images here' : 'Drag & drop images here'}
                </p>
                <p className="text-sm text-white/70 mt-1">
                  or click to browse files
                </p>
              </div>
            </div>
          </div>

          {uploadedImages.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white">
                Uploaded Images ({uploadedImages.length}/5)
              </h3>
              <div className="space-y-2">
                {uploadedImages.map((image) => (
                  <ImagePreview 
                    key={image.id} 
                    image={image} 
                    onRemove={() => removeImage(image.id)} 
                  />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Preview Area */}
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-white">
            Preview
          </h3>
          {uploadedImages.length === 0 ? (
            <div className="border-2 border-dashed border-white/30 rounded-xl p-8 text-center bg-white/5 backdrop-blur-sm">
              <Camera className="w-12 h-12 text-white/50 mx-auto mb-4" />
              <p className="text-white/70">No images uploaded yet</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 sm:gap-4">
              <AnimatePresence>
                {uploadedImages.map((image) => (
                  <motion.div
                    key={image.id}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    className="relative aspect-square rounded-lg overflow-hidden bg-gray-100"
                  >
                    <img
                      src={image.preview}
                      alt="Uploaded fridge content"
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                      {image.uploadProgress === 100 ? (
                        <CheckCircle className="w-8 h-8 text-green-400" />
                      ) : (
                        <div className="text-white text-sm">
                          {image.uploadProgress}%
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>

      {uploadedImages.length > 0 && (
        <div className="mt-8 flex justify-center">
          <button
            onClick={handleContinue}
            disabled={!canContinue || isUploading}
            className={`
              btn btn-primary btn-lg px-8
              ${!canContinue || isUploading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            {isUploading ? 'Uploading...' : 'Continue to Inventory'}
          </button>
        </div>
      )}
    </div>
  )
}

interface ImagePreviewProps {
  image: UploadedImage
  onRemove: () => void
}

function ImagePreview({ image, onRemove }: ImagePreviewProps) {
  return (
    <div className="flex items-center space-x-3 p-3 bg-white rounded-lg border border-gray-200">
      <div className="flex-shrink-0 w-12 h-12 rounded-lg overflow-hidden bg-gray-100">
        <img
          src={image.preview}
          alt="Preview"
          className="w-full h-full object-cover"
        />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">
          {image.file.name}
        </p>
        <p className="text-xs text-gray-500">
          {(image.file.size / 1024 / 1024).toFixed(1)} MB
        </p>
        {image.uploadProgress < 100 && (
          <div className="mt-1 w-full bg-gray-200 rounded-full h-1.5">
            <div 
              className="bg-primary-600 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${image.uploadProgress}%` }}
            />
          </div>
        )}
        {image.error && (
          <div className="flex items-center mt-1 text-xs text-red-600">
            <AlertCircle className="w-3 h-3 mr-1" />
            Upload failed
          </div>
        )}
      </div>
      <button
        onClick={onRemove}
        className="flex-shrink-0 p-1 text-gray-400 hover:text-red-500 transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}
