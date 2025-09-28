'use client'

import { motion } from 'framer-motion'
import { 
  Camera, 
  Leaf, 
  ChefHat, 
  TrendingUp, 
  ArrowRight, 
  Sparkles,
  Target,
  Users,
  Zap
} from 'lucide-react'
import { Logo } from './Logo'

interface IntroPageProps {
  onGetStarted: () => void
}

export function IntroPage({ onGetStarted }: IntroPageProps) {
  const features = [
    {
      icon: Camera,
      title: "Smart Photo Analysis",
      description: "Upload photos of your fridge and let AI identify all your ingredients automatically"
    },
    {
      icon: Leaf,
      title: "Carbon Impact Tracking",
      description: "See the environmental impact of your food choices with detailed carbon footprint analysis"
    },
    {
      icon: ChefHat,
      title: "Personalized Recipes",
      description: "Get recipe recommendations based on what you actually have in your fridge"
    },
    {
      icon: TrendingUp,
      title: "Eco-Friendly Tips",
      description: "Discover sustainable food swaps to reduce your environmental footprint"
    }
  ]

  const benefits = [
    {
      icon: Target,
      title: "Reduce Food Waste",
      description: "Use everything in your fridge before it goes bad"
    },
    {
      icon: Users,
      title: "Family-Friendly",
      description: "Get portion recommendations for your household size"
    },
    {
      icon: Zap,
      title: "Quick & Easy",
      description: "Get results in under 10 seconds with our AI-powered analysis"
    }
  ]

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center mb-16"
      >
        <div className="w-24 h-24 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center mx-auto mb-8 animate-bounce">
          <Logo size="lg" />
        </div>
        
        <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
          Welcome to{' '}
          <span className="bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">
            Smart Fridge
          </span>
        </h1>
        
        <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-3xl mx-auto leading-relaxed">
          Transform your fridge into an intelligent kitchen assistant. Get AI-powered insights, 
          reduce food waste, and make sustainable choices with every meal.
        </p>

        <motion.button
          onClick={onGetStarted}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="btn btn-primary btn-lg px-12 py-4 text-lg font-semibold shadow-2xl"
        >
          <Sparkles className="w-6 h-6 mr-3" />
          Get Started
          <ArrowRight className="w-6 h-6 ml-3" />
        </motion.button>
      </motion.div>

      {/* Features Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="mb-16"
      >
        <h2 className="text-3xl md:text-4xl font-bold text-white text-center mb-12">
          How It Works
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 + index * 0.1 }}
              className="card p-6 text-center hover:scale-105 transition-transform duration-300"
            >
              <div className="w-16 h-16 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <feature.icon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Benefits Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.4 }}
        className="mb-16"
      >
        <h2 className="text-3xl md:text-4xl font-bold text-white text-center mb-12">
          Why Choose Smart Fridge?
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {benefits.map((benefit, index) => (
            <motion.div
              key={benefit.title}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 + index * 0.1 }}
              className="card p-8 text-center hover:scale-105 transition-transform duration-300"
            >
              <div className="w-20 h-20 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <benefit.icon className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-4">
                {benefit.title}
              </h3>
              <p className="text-gray-600 leading-relaxed text-lg">
                {benefit.description}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Call to Action */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.6 }}
        className="text-center"
      >
        <div className="card p-12 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-white/30">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Ready to Transform Your Kitchen?
          </h2>
          <p className="text-xl text-gray-700 mb-8 max-w-2xl mx-auto">
            Join thousands of users who are reducing food waste and making 
            sustainable choices with Smart Fridge.
          </p>
          
          <motion.button
            onClick={onGetStarted}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn btn-primary btn-lg px-12 py-4 text-lg font-semibold shadow-2xl"
          >
            <Camera className="w-6 h-6 mr-3" />
            Start Your Journey
            <ArrowRight className="w-6 h-6 ml-3" />
          </motion.button>
        </div>
      </motion.div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.8 }}
        className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-center"
      >
        <div className="card p-6">
          <div className="text-3xl font-bold text-green-600 mb-2">10s</div>
          <div className="text-gray-600">Average Analysis Time</div>
        </div>
        <div className="card p-6">
          <div className="text-3xl font-bold text-emerald-600 mb-2">30%</div>
          <div className="text-gray-600">Food Waste Reduction</div>
        </div>
        <div className="card p-6">
          <div className="text-3xl font-bold text-green-700 mb-2">5+</div>
          <div className="text-gray-600">Recipe Recommendations</div>
        </div>
      </motion.div>
    </div>
  )
}
