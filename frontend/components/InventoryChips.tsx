'use client'

import { useState, useEffect } from 'react'
import { Plus, X, Edit3, Check, XCircle } from 'lucide-react'
import { InventoryItem } from '@/app/page'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'

interface InventoryChipsProps {
  inventory: InventoryItem[]
  onInventoryUpdated: (inventory: InventoryItem[]) => void
  onBack: () => void
}

export function InventoryChips({ inventory, onInventoryUpdated, onBack }: InventoryChipsProps) {
  const [editingItem, setEditingItem] = useState<InventoryItem | null>(null)
  const [isAddingNew, setIsAddingNew] = useState(false)
  const [newItem, setNewItem] = useState<Partial<InventoryItem>>({
    name: '',
    category: '',
    quantity: '',
    carbonImpact: 'medium'
  })

  // Mock AI-detected items for demo
  const mockDetectedItems: InventoryItem[] = [
    {
      id: 'detected-1',
      name: 'Organic Tomatoes',
      category: 'Vegetables',
      quantity: '6 pieces',
      carbonImpact: 'low',
      confidence: 0.92
    },
    {
      id: 'detected-2',
      name: 'Ground Beef',
      category: 'Meat',
      quantity: '1 lb',
      carbonImpact: 'high',
      confidence: 0.88
    },
    {
      id: 'detected-3',
      name: 'Whole Milk',
      category: 'Dairy',
      quantity: '1 gallon',
      carbonImpact: 'medium',
      confidence: 0.95
    },
    {
      id: 'detected-4',
      name: 'Cheddar Cheese',
      category: 'Dairy',
      quantity: '8 oz',
      carbonImpact: 'medium',
      confidence: 0.87
    },
    {
      id: 'detected-5',
      name: 'Spinach',
      category: 'Vegetables',
      quantity: '1 bag',
      carbonImpact: 'low',
      confidence: 0.91
    }
  ]

  useEffect(() => {
    if (inventory.length === 0) {
      // Auto-populate with detected items
      onInventoryUpdated(mockDetectedItems)
    }
  }, [inventory.length, onInventoryUpdated])

  const handleAddItem = () => {
    if (!newItem.name || !newItem.category || !newItem.quantity) {
      toast.error('Please fill in all required fields')
      return
    }

    const item: InventoryItem = {
      id: `item-${Date.now()}`,
      name: newItem.name,
      category: newItem.category,
      quantity: newItem.quantity,
      carbonImpact: newItem.carbonImpact || 'medium',
      confidence: 1.0 // User-added items have 100% confidence
    }

    onInventoryUpdated([...inventory, item])
    setNewItem({ name: '', category: '', quantity: '', carbonImpact: 'medium' })
    setIsAddingNew(false)
    toast.success('Item added successfully')
  }

  const handleEditItem = (item: InventoryItem) => {
    setEditingItem(item)
  }

  const handleSaveEdit = () => {
    if (!editingItem?.name || !editingItem?.category || !editingItem?.quantity) {
      toast.error('Please fill in all required fields')
      return
    }

    const updatedInventory = inventory.map(item =>
      item.id === editingItem.id ? editingItem : item
    )
    onInventoryUpdated(updatedInventory)
    setEditingItem(null)
    toast.success('Item updated successfully')
  }

  const handleRemoveItem = (itemId: string) => {
    const updatedInventory = inventory.filter(item => item.id !== itemId)
    onInventoryUpdated(updatedInventory)
    toast.success('Item removed')
  }

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

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Review Your Inventory
          </h1>
          <p className="text-lg text-gray-600">
            Review and edit the items we detected in your fridge
          </p>
        </div>
        <button
          onClick={onBack}
          className="btn btn-outline btn-md"
        >
          ← Back to Upload
        </button>
      </div>

      <div className="space-y-6">
        {/* Detected Items */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Detected Items ({inventory.length})
          </h2>
          <div className="flex flex-wrap gap-3">
            <AnimatePresence>
              {inventory.map((item) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="chip chip-removable group"
                >
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">{item.name}</span>
                    <span className="text-gray-500 text-xs">
                      ({item.quantity})
                    </span>
                    <span className={`badge ${getCarbonBadgeColor(item.carbonImpact)}`}>
                      {getCarbonBadgeText(item.carbonImpact)}
                    </span>
                    {item.confidence < 1.0 && (
                      <span className="text-xs text-gray-400">
                        {Math.round(item.confidence * 100)}%
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-1 ml-2">
                    <button
                      onClick={() => handleEditItem(item)}
                      className="p-1 text-gray-400 hover:text-blue-500 transition-colors"
                    >
                      <Edit3 className="w-3 h-3" />
                    </button>
                    <button
                      onClick={() => handleRemoveItem(item.id)}
                      className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>

        {/* Add New Item */}
        <div>
          <button
            onClick={() => setIsAddingNew(true)}
            className="btn btn-outline btn-md"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Missing Item
          </button>
        </div>

        {/* Add/Edit Form */}
        {(isAddingNew || editingItem) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {editingItem ? 'Edit Item' : 'Add New Item'}
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Item Name *
                </label>
                <input
                  type="text"
                  value={editingItem?.name || newItem.name || ''}
                  onChange={(e) => {
                    if (editingItem) {
                      setEditingItem({ ...editingItem, name: e.target.value })
                    } else {
                      setNewItem({ ...newItem, name: e.target.value })
                    }
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="e.g., Organic Apples"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category *
                </label>
                <select
                  value={editingItem?.category || newItem.category || ''}
                  onChange={(e) => {
                    if (editingItem) {
                      setEditingItem({ ...editingItem, category: e.target.value })
                    } else {
                      setNewItem({ ...newItem, category: e.target.value })
                    }
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">Select category</option>
                  <option value="Vegetables">Vegetables</option>
                  <option value="Fruits">Fruits</option>
                  <option value="Meat">Meat</option>
                  <option value="Dairy">Dairy</option>
                  <option value="Grains">Grains</option>
                  <option value="Beverages">Beverages</option>
                  <option value="Snacks">Snacks</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Quantity *
                </label>
                <input
                  type="text"
                  value={editingItem?.quantity || newItem.quantity || ''}
                  onChange={(e) => {
                    if (editingItem) {
                      setEditingItem({ ...editingItem, quantity: e.target.value })
                    } else {
                      setNewItem({ ...newItem, quantity: e.target.value })
                    }
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="e.g., 1 lb, 6 pieces, 1 bag"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Carbon Impact
                </label>
                <select
                  value={editingItem?.carbonImpact || newItem.carbonImpact || 'medium'}
                  onChange={(e) => {
                    const impact = e.target.value as 'low' | 'medium' | 'high'
                    if (editingItem) {
                      setEditingItem({ ...editingItem, carbonImpact: impact })
                    } else {
                      setNewItem({ ...newItem, carbonImpact: impact })
                    }
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="low">Low Carbon</option>
                  <option value="medium">Medium Carbon</option>
                  <option value="high">High Carbon</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setEditingItem(null)
                  setIsAddingNew(false)
                  setNewItem({ name: '', category: '', quantity: '', carbonImpact: 'medium' })
                }}
                className="btn btn-outline btn-md"
              >
                <XCircle className="w-4 h-4 mr-2" />
                Cancel
              </button>
              <button
                onClick={editingItem ? handleSaveEdit : handleAddItem}
                className="btn btn-primary btn-md"
              >
                <Check className="w-4 h-4 mr-2" />
                {editingItem ? 'Save Changes' : 'Add Item'}
              </button>
            </div>
          </motion.div>
        )}

        {/* Continue Button */}
        <div className="flex justify-center pt-6">
          <button
            onClick={() => onInventoryUpdated(inventory)}
            className="btn btn-primary btn-lg px-8"
          >
            Continue to People Count
          </button>
        </div>
      </div>
    </div>
  )
}
