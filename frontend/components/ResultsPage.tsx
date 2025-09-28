'use client'

import { useState } from 'react'
import { 
  RotateCcw, 
  Leaf, 
  Clock, 
  Users, 
  ChefHat, 
  TrendingUp, 
  ArrowRight,
  ExternalLink,
  Star,
  Lightbulb,
  CheckCircle
} from 'lucide-react'
import { AnalysisResults, UploadedImage } from '@/app/page'
import { motion } from 'framer-motion'
import Image from 'next/image'

interface ResultsPageProps {
  results: AnalysisResults
  uploadedImages: UploadedImage[]
  peopleCount: number
  onReset: () => void
}

export function ResultsPage({ results, uploadedImages, peopleCount, onReset }: ResultsPageProps) {
  const [activeTab, setActiveTab] = useState<'inventory' | 'recipes' | 'tips'>('inventory')

  const getCarbonBadgeColor = (impact: 'low' | 'medium' | 'high') => {
    switch (impact) {
      case 'low':
        return 'badge-success'
      case 'medium':
        return 'badge-warning'
      case 'high':
        return 'badge-error'
    }
  }

  const getCarbonBadgeText = (impact: 'low' | 'medium' | 'high') => {
    switch (impact) {
      case 'low':
        return 'Low Carbon'
      case 'medium':
        return 'Medium Carbon'
      case 'high':
        return 'High Carbon'
    }
  }

  const formatTime = (minutes: number) => {
    if (minutes < 60) {
      return `${minutes}m`
    }
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Analysis Complete!
          </h1>
          <p className="text-lg text-gray-600">
            Here's what we found in your fridge for {peopleCount} {peopleCount === 1 ? 'person' : 'people'}
          </p>
        </div>
        <button
          onClick={onReset}
          className="btn btn-outline btn-md"
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Start Over
        </button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-6 text-center hover:scale-105 transition-transform duration-300"
        >
          <div className="w-12 h-12 bg-gradient-to-r from-blue-400 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-3 animate-pulse">
            <ChefHat className="w-6 h-6 text-white" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{results.inventory.length}</div>
          <div className="text-sm text-gray-600">Items Found</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card p-6 text-center hover:scale-105 transition-transform duration-300"
        >
          <div className="w-12 h-12 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-3 animate-pulse">
            <Leaf className="w-6 h-6 text-white" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{results.recipes.length}</div>
          <div className="text-sm text-gray-600">Recipe Ideas</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card p-6 text-center hover:scale-105 transition-transform duration-300"
        >
          <div className="w-12 h-12 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-3 animate-pulse">
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{results.totalCarbonImpact.toFixed(1)}</div>
          <div className="text-sm text-gray-600">kg CO₂</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card p-6 text-center hover:scale-105 transition-transform duration-300"
        >
          <div className="w-12 h-12 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-3 animate-pulse">
            <Clock className="w-6 h-6 text-white" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{results.analysisTime}s</div>
          <div className="text-sm text-gray-600">Analysis Time</div>
        </motion.div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-8">
        <nav className="flex space-x-8">
          {[
            { id: 'inventory', label: 'Inventory', count: results.inventory.length },
            { id: 'recipes', label: 'Recipes', count: results.recipes.length },
            { id: 'tips', label: 'Swap Tips', count: results.swapTips.length }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              {tab.label}
              <span className="ml-2 bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs">
                {tab.count}
              </span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-8">
        {activeTab === 'inventory' && (
          <motion.div
            key="inventory"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            <h2 className="text-2xl font-bold text-gray-900">Your Fridge Inventory</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
              {results.inventory.map((item, index) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="card p-4"
                >
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-semibold text-gray-900">{item.name}</h3>
                    <span className={`badge ${getCarbonBadgeColor(item.carbonImpact)}`}>
                      {getCarbonBadgeText(item.carbonImpact)}
                    </span>
                  </div>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex justify-between">
                      <span>Category:</span>
                      <span>{item.category}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Quantity:</span>
                      <span>{item.quantity}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Confidence:</span>
                      <span>{Math.round(item.confidence * 100)}%</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {activeTab === 'recipes' && (
          <motion.div
            key="recipes"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            <h2 className="text-2xl font-bold text-gray-900">Recommended Recipes</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
              {results.recipes.map((recipe, index) => (
                <motion.div
                  key={recipe.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="card overflow-hidden"
                >
                  <div className="aspect-video bg-gray-100 relative">
                    {recipe.imageUrl ? (
                      <Image
                        src={recipe.imageUrl}
                        alt={recipe.title}
                        fill
                        className="object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <ChefHat className="w-12 h-12 text-gray-400" />
                      </div>
                    )}
                    <div className="absolute top-4 right-4">
                      <span className={`badge ${getCarbonBadgeColor(recipe.carbonImpact)}`}>
                        {getCarbonBadgeText(recipe.carbonImpact)}
                      </span>
                    </div>
                  </div>
                  <div className="p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">{recipe.title}</h3>
                    <p className="text-gray-600 mb-4">{recipe.description}</p>
                    
                    <div className="flex items-center space-x-4 mb-4 text-sm text-gray-500">
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        {formatTime(recipe.prepTime)}
                      </div>
                      <div className="flex items-center">
                        <Users className="w-4 h-4 mr-1" />
                        {recipe.servings} servings
                      </div>
                    </div>

                    <div className="mb-4">
                      <h4 className="font-semibold text-gray-900 mb-2">Ingredients:</h4>
                      <div className="flex flex-wrap gap-2">
                        {recipe.ingredients.map((ingredient, idx) => (
                          <span key={idx} className="chip">
                            {ingredient}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="flex space-x-3">
                      <button className="btn btn-primary btn-md flex-1">
                        View Recipe
                        <ArrowRight className="w-4 h-4 ml-2" />
                      </button>
                      <button className="btn btn-outline btn-md">
                        <ExternalLink className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {activeTab === 'tips' && (
          <motion.div
            key="tips"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            <h2 className="text-2xl font-bold text-gray-900">Eco-Friendly Swap Tips</h2>
            <div className="space-y-4">
              {results.swapTips.map((tip, index) => (
                <motion.div
                  key={tip.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="card p-6"
                >
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                      <Lightbulb className="w-6 h-6 text-green-600" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          Swap {tip.original} for {tip.suggestion}
                        </h3>
                        <span className="badge badge-success">
                          -{tip.carbonSavings}% CO₂
                        </span>
                      </div>
                      <p className="text-gray-600 mb-3">{tip.reason}</p>
                      <div className="flex items-center text-sm text-green-600">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        <span>Recommended for your household</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </div>

      {/* Uploaded Images Preview */}
      {uploadedImages.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Your Uploaded Images</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 sm:gap-4">
            {uploadedImages.map((image) => (
              <div key={image.id} className="aspect-square rounded-lg overflow-hidden bg-gray-100">
                <img
                  src={image.preview}
                  alt="Uploaded fridge content"
                  className="w-full h-full object-cover"
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
