"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

// Types for our wavelet data
interface WaveletData {
  delta: number    // 0-1 intensity values
  theta: number
  lowAlpha: number
  highAlpha: number
  lowBeta: number
  highBeta: number
  lowGamma: number
  highGamma: number
}

interface WaveletProps {
  data: WaveletData
  size?: number    // Base size in pixels
  interactive?: boolean
  opacity?: number
}

// Color constants for each brainwave type
const COLORS = {
  delta: "#dd0a0a",
  theta: "#ff8500",
  lowAlpha: "#fcea01",
  highAlpha: "#58ed14",
  lowBeta: "#16caf4",
  highBeta: "#022aba",
  lowGamma: "#6f5ba3",
  highGamma: "#e50cbc"
} as const

export default function Wavelet({ 
  data, 
  size = 60, 
  interactive = true,
  opacity = 1
}: WaveletProps) {
  const [isHovered, setIsHovered] = useState(false)

  // Calculate circle sizes based on intensity values
  // Each outer circle needs to be larger to maintain visibility
  const getCircleSize = (intensity: number, index: number) => {
    const baseSize = size * 0.9 // Leave some padding
    const minSize = baseSize * 0.1 // Minimum size when intensity is 0
    const maxSize = baseSize * (1 - (index * 0.1)) // Scale down for inner circles
    return minSize + (intensity * (maxSize - minSize))
  }

  // Order from largest (outer) to smallest (inner)
  const circles = [
    { name: "High Gamma", value: data.highGamma, color: COLORS.highGamma },
    { name: "Low Gamma", value: data.lowGamma, color: COLORS.lowGamma },
    { name: "High Beta", value: data.highBeta, color: COLORS.highBeta },
    { name: "Low Beta", value: data.lowBeta, color: COLORS.lowBeta },
    { name: "High Alpha", value: data.highAlpha, color: COLORS.highAlpha },
    { name: "Low Alpha", value: data.lowAlpha, color: COLORS.lowAlpha },
    { name: "Theta", value: data.theta, color: COLORS.theta },
    { name: "Delta", value: data.delta, color: COLORS.delta },
  ]

  const wavelet = (
    <div 
      className="relative"
      style={{ width: size, height: size }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {circles.map((circle, index) => (
        <div
          key={circle.name}
          className="absolute rounded-full"
          style={{
            backgroundColor: circle.color,
            width: getCircleSize(circle.value, index),
            height: getCircleSize(circle.value, index),
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -50%)',
            transition: interactive ? 'all 0.2s ease-in-out' : 'none',
            zIndex: index + 1,
            opacity: opacity
          }}
        />
      ))}
    </div>
  )

  if (!interactive) return wavelet

  return (
    <TooltipProvider>
      <Tooltip open={isHovered}>
        <TooltipTrigger asChild>
          {wavelet}
        </TooltipTrigger>
        <TooltipContent>
          <div className="space-y-1">
            {circles.map(circle => (
              <div key={circle.name} className="flex items-center gap-2">
                <div 
                  className="w-2 h-2 rounded-full" 
                  style={{ backgroundColor: circle.color }}
                />
                <span className="text-sm">
                  {circle.name}: {Math.round(circle.value * 100)}%
                </span>
              </div>
            ))}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}