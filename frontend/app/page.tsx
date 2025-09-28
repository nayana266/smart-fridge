'use client'

import { useState } from 'react'
import { ImageUploader } from '@/components/ImageUploader'
import { InventoryChips } from '@/components/InventoryChips'
import { PeopleCountForm } from '@/components/PeopleCountForm'
import { ResultsPage } from '@/components/ResultsPage'
import { IntroPage } from '@/components/IntroPage'
import { Logo } from '@/components/Logo'
import { DemoModeToggle } from '@/components/DemoModeToggle'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { ErrorMessage } from '@/components/ErrorMessage'
import { analyzeImages, getMockAnalysisResults } from '@/lib/api'

export type UploadedImage = {
  id: string
  file: File
  preview: string
  uploadProgress: number
  s3Key?: string
  error?: string
}

export type InventoryItem = {
  id: string
  name: string
  category: string
  quantity: string
  carbonImpact: 'low' | 'medium' | 'high'
  confidence: number
}

export type Recipe = {
  id: string
  title: string
  description: string
  ingredients: string[]
  instructions: string[]
  carbonImpact: 'low' | 'medium' | 'high'
  prepTime: number
  servings: number
  imageUrl?: string
}

export type SwapTip = {
  id: string
  original: string
  suggestion: string
  reason: string
  carbonSavings: number
}

export type AnalysisResults = {
  inventory: InventoryItem[]
  recipes: Recipe[]
  swapTips: SwapTip[]
  totalCarbonImpact: number
  analysisTime: number
}

export default function Home() {
  const [currentStep, setCurrentStep] = useState<'intro' | 'upload' | 'inventory' | 'people' | 'results'>('intro')
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([])
  const [inventory, setInventory] = useState<InventoryItem[]>([])
  const [peopleCount, setPeopleCount] = useState<number>(2)
  const [results, setResults] = useState<AnalysisResults | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isDemoMode, setIsDemoMode] = useState(false)

  const handleImagesUploaded = (images: UploadedImage[]) => {
    setUploadedImages(images)
    setCurrentStep('inventory')
  }

  const handleInventoryUpdated = (updatedInventory: InventoryItem[]) => {
    setInventory(updatedInventory)
    setCurrentStep('people')
  }

  const handlePeopleCountSubmit = async (count: number) => {
    setPeopleCount(count)
    setIsLoading(true)
    setError(null)

    try {
      let results: AnalysisResults

      if (isDemoMode) {
        // Use mock data for demo mode
        results = getMockAnalysisResults()
        // Simulate loading time
        await new Promise(resolve => setTimeout(resolve, 2000))
      } else {
        // Use real API
        const imageKeys = uploadedImages
          .filter(img => img.s3Key)
          .map(img => img.s3Key!)
        
        if (imageKeys.length === 0) {
          throw new Error('No images uploaded successfully')
        }

        results = await analyzeImages(imageKeys, count, inventory)
      }
      
      setResults(results)
      setCurrentStep('results')
    } catch (err) {
      console.error('Analysis failed:', err)
      setError('Failed to analyze images. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setCurrentStep('intro')
    setUploadedImages([])
    setInventory([])
    setPeopleCount(2)
    setResults(null)
    setError(null)
  }

  const handleGetStarted = () => {
    setCurrentStep('upload')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-20 h-20 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center mb-6 mx-auto animate-pulse">
            <Logo size="lg" />
          </div>
          <LoadingSpinner size="lg" />
          <h2 className="mt-4 text-xl font-semibold text-white">
            Analyzing your fridge contents...
          </h2>
          <p className="mt-2 text-white/80">
            This usually takes 5-10 seconds
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen relative">
      {/* Animated Background Elements */}
      <div className="floating-particles">
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
      </div>
      
      {/* Gradient Orbs */}
      <div className="gradient-orb orb-1"></div>
      <div className="gradient-orb orb-2"></div>
      <div className="gradient-orb orb-3"></div>
      
      <header className="bg-white/10 backdrop-blur-md shadow-xl border-b border-white/20 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <button 
              onClick={handleReset}
              className="flex items-center space-x-3 hover:scale-105 transition-transform duration-200 cursor-pointer"
            >
              <Logo size="md" />
              <h1 className="text-2xl font-bold text-white">
                Smart Fridge
              </h1>
            </button>
            <DemoModeToggle 
              isDemoMode={isDemoMode} 
              onToggle={setIsDemoMode} 
            />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8 relative z-10">
        {error && (
          <div className="mb-6">
            <ErrorMessage message={error} onDismiss={() => setError(null)} />
          </div>
        )}

        {currentStep === 'intro' && (
          <IntroPage onGetStarted={handleGetStarted} />
        )}

        {currentStep === 'upload' && (
          <ImageUploader 
            onImagesUploaded={handleImagesUploaded}
            isDemoMode={isDemoMode}
          />
        )}

        {currentStep === 'inventory' && (
          <InventoryChips 
            inventory={inventory}
            onInventoryUpdated={handleInventoryUpdated}
            onBack={() => setCurrentStep('upload')}
          />
        )}

        {currentStep === 'people' && (
          <PeopleCountForm 
            peopleCount={peopleCount}
            onPeopleCountSubmit={handlePeopleCountSubmit}
            onBack={() => setCurrentStep('inventory')}
          />
        )}

        {currentStep === 'results' && results && (
          <ResultsPage 
            results={results}
            uploadedImages={uploadedImages}
            peopleCount={peopleCount}
            onReset={handleReset}
          />
        )}
      </main>
    </div>
  )
}
