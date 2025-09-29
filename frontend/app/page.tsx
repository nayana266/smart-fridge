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
  const [loadingMessage, setLoadingMessage] = useState('')
  const [loadingSubMessage, setLoadingSubMessage] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isDemoMode, setIsDemoMode] = useState(false)

  const handleImagesUploaded = async (images: UploadedImage[]) => {
    setUploadedImages(images)
    setIsLoading(true)
    setLoadingMessage('Detecting food items in your images...')
    setLoadingSubMessage('Using AI vision to identify foods and calculate carbon impact...')
    setError(null)

    try {
      // Get vision detection results for the uploaded images
      const imageKeys = images
        .filter(img => img.s3Key)
        .map(img => img.s3Key!)
      
      if (imageKeys.length === 0) {
        throw new Error('No images uploaded successfully')
      }

      // Call vision detection API
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/vision/detect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          keys: imageKeys,
          bucket: 'smart-fridge-images-nayana'
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to detect food items')
      }

      const visionResults = await response.json()
      
      // Convert vision results to inventory format
      const detectedInventory: InventoryItem[] = visionResults.items.map((item: any, index: number) => ({
        id: `detected-${item.name}-${Date.now()}-${index}`,
        name: item.name,
        category: 'Detected', // Will be updated by carbon planning
        quantity: `${item.count} piece(s)`,
        carbonImpact: 'medium', // Will be updated by carbon planning
        confidence: item.confidence
      }))

      setInventory(detectedInventory)
      setCurrentStep('inventory')
    } catch (err) {
      console.error('Vision detection failed:', err)
      setError('Failed to detect food items. Please try again.')
      // Fall back to empty inventory
      setInventory([])
      setCurrentStep('inventory')
    } finally {
      setIsLoading(false)
    }
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
        setLoadingMessage('Generating demo recipes...')
        setLoadingSubMessage('Creating sample recipes and sustainability tips...')
        results = getMockAnalysisResults()
        // Simulate loading time
        await new Promise(resolve => setTimeout(resolve, 2000))
      } else {
        setLoadingMessage('Analyzing your inventory...')
        setLoadingSubMessage('Calculating carbon impact and finding sustainable swaps...')
        // Get carbon impact and planning data
        const foodNames = inventory.map(item => item.name)
        
        // Call carbon planning API to get proper categories and carbon impacts
        const planResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/plan`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            items: foodNames,
            people: count,
            flags: [],
            demo: false
          }),
        })

        let finalInventory = inventory
        
        if (planResponse.ok) {
          const planData = await planResponse.json()
          
          // Update inventory with proper categories and carbon impacts
          finalInventory = inventory.map(invItem => {
            const planItem = planData.inventory.find((p: any) => 
              p.name.toLowerCase() === invItem.name.toLowerCase()
            )
            return {
              ...invItem,
              category: planItem?.category || invItem.category,
              carbonImpact: planItem?.impact === 'low' ? 'low' : 
                           planItem?.impact === 'high' ? 'high' : 'medium'
            }
          })
          
          setInventory(finalInventory)
        }

        // Use real API for full analysis with updated inventory
        setLoadingMessage('Creating personalized recipes...')
        setLoadingSubMessage('Using AI to generate custom recipes based on your ingredients...')
        
        const imageKeys = uploadedImages
          .filter(img => img.s3Key)
          .map(img => img.s3Key!)
        
        if (imageKeys.length === 0) {
          throw new Error('No images uploaded successfully')
        }

        results = await analyzeImages(imageKeys, count, finalInventory)
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
    setLoadingMessage('')
    setLoadingSubMessage('')
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
            {loadingMessage || 'Processing...'}
          </h2>
          <p className="mt-2 text-white/80">
            {loadingSubMessage || 'Please wait while we analyze your data...'}
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
