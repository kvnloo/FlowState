"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Slider } from "@/components/ui/slider"
import Wavelet from "./wavelet"

export default function WaveletDemo() {
  const [values, setValues] = useState({
    delta: 0.5,
    theta: 0.4,
    lowAlpha: 0.3,
    highAlpha: 0.6,
    lowBeta: 0.7,
    highBeta: 0.4,
    lowGamma: 0.2,
    highGamma: 0.1
  })

  const setAllToMax = () => {
    setValues({
      delta: 1,
      theta: 1,
      lowAlpha: 1,
      highAlpha: 1,
      lowBeta: 1,
      highBeta: 1,
      lowGamma: 1,
      highGamma: 1
    })
  }

  const resetValues = () => {
    setValues({
      delta: 0.5,
      theta: 0.4,
      lowAlpha: 0.3,
      highAlpha: 0.6,
      lowBeta: 0.7,
      highBeta: 0.4,
      lowGamma: 0.2,
      highGamma: 0.1
    })
  }

  return (
    <Card className="p-6 space-y-8">
      <div className="flex justify-center flex-col items-center gap-4">
        <Wavelet data={values} size={120} />
        <div className="flex gap-2">
          <button
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            onClick={setAllToMax}
          >
            Set All to 100%
          </button>
          <button
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
            onClick={resetValues}
          >
            Reset
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {Object.entries(values).map(([key, value]) => (
          <div key={key} className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">{key}</span>
              <span>{Math.round(value * 100)}%</span>
            </div>
            <Slider
              value={[value]}
              min={0}
              max={1}
              step={0.01}
              onValueChange={([newValue]) =>
                setValues(prev => ({ ...prev, [key]: newValue }))
              }
            />
          </div>
        ))}
      </div>
    </Card>
  )
}

