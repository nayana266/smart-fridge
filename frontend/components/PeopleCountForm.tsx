'use client'

import { useState } from 'react'
import { Users, ArrowLeft, ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'

interface PeopleCountFormProps {
  peopleCount: number
  onPeopleCountSubmit: (count: number) => void
  onBack: () => void
}

export function PeopleCountForm({ peopleCount, onPeopleCountSubmit, onBack }: PeopleCountFormProps) {
  const [count, setCount] = useState(peopleCount)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onPeopleCountSubmit(count)
  }

  const incrementCount = () => {
    if (count < 10) {
      setCount(count + 1)
    }
  }

  const decrementCount = () => {
    if (count > 1) {
      setCount(count - 1)
    }
  }

  const quickSelectCounts = [1, 2, 3, 4, 6, 8]

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <div className="mx-auto w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
          <Users className="w-8 h-8 text-primary-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          How Many People?
        </h1>
        <p className="text-lg text-gray-600">
          This helps us recommend the right portion sizes for your recipes
        </p>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card p-8"
      >
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Counter Display */}
          <div className="text-center">
            <div className="inline-flex items-center space-x-6">
              <button
                type="button"
                onClick={decrementCount}
                disabled={count <= 1}
                className={`
                  w-12 h-12 rounded-full border-2 border-gray-300 flex items-center justify-center
                  transition-colors
                  ${count <= 1 
                    ? 'opacity-50 cursor-not-allowed' 
                    : 'hover:border-primary-500 hover:bg-primary-50'
                  }
                `}
              >
                <ArrowLeft className="w-6 h-6 text-gray-600" />
              </button>

              <div className="text-center">
                <div className="text-6xl font-bold text-gray-900 mb-2">
                  {count}
                </div>
                <div className="text-lg text-gray-600">
                  {count === 1 ? 'person' : 'people'}
                </div>
              </div>

              <button
                type="button"
                onClick={incrementCount}
                disabled={count >= 10}
                className={`
                  w-12 h-12 rounded-full border-2 border-gray-300 flex items-center justify-center
                  transition-colors
                  ${count >= 10 
                    ? 'opacity-50 cursor-not-allowed' 
                    : 'hover:border-primary-500 hover:bg-primary-50'
                  }
                `}
              >
                <ArrowRight className="w-6 h-6 text-gray-600" />
              </button>
            </div>
          </div>

          {/* Quick Select */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
              Quick Select
            </h3>
            <div className="flex flex-wrap justify-center gap-3">
              {quickSelectCounts.map((num) => (
                <button
                  key={num}
                  type="button"
                  onClick={() => setCount(num)}
                  className={`
                    px-4 py-2 rounded-full border-2 transition-colors
                    ${count === num
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-300 text-gray-700 hover:border-gray-400'
                    }
                  `}
                >
                  {num} {num === 1 ? 'person' : 'people'}
                </button>
              ))}
            </div>
          </div>

          {/* Manual Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 text-center">
              Or enter a custom number
            </label>
            <div className="max-w-xs mx-auto">
              <input
                type="number"
                min="1"
                max="20"
                value={count}
                onChange={(e) => {
                  const value = parseInt(e.target.value)
                  if (value >= 1 && value <= 20) {
                    setCount(value)
                  }
                }}
                className="w-full px-4 py-3 text-center text-2xl font-semibold border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          {/* Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-2">
                Recipe Portions
              </h4>
              <p className="text-sm text-blue-700">
                We'll adjust recipe serving sizes based on your household size
              </p>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-semibold text-green-900 mb-2">
                Carbon Impact
              </h4>
              <p className="text-sm text-green-700">
                Calculate per-person carbon footprint for more accurate insights
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between pt-6">
            <button
              type="button"
              onClick={onBack}
              className="btn btn-outline btn-lg"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back to Inventory
            </button>
            <button
              type="submit"
              className="btn btn-primary btn-lg"
            >
              Analyze My Fridge
              <ArrowRight className="w-5 h-5 ml-2" />
            </button>
          </div>
        </form>
      </motion.div>

      {/* Tips */}
      <div className="mt-8 text-center">
        <div className="inline-flex items-center space-x-2 text-sm text-gray-500">
          <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
          <span>You can change this later in your profile settings</span>
        </div>
      </div>
    </div>
  )
}


