import { ChangeEvent } from 'react';

interface SliderProps {
  value: number[];
  min?: number;
  max?: number;
  step?: number;
  onValueChange: (value: number[]) => void;
}

export function Slider({ value, min = 0, max = 100, step = 1, onValueChange }: SliderProps) {
  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    onValueChange([Number(e.target.value)]);
  };

  return (
    <input
      type="range"
      min={min}
      max={max}
      step={step}
      value={value[0]}
      onChange={handleChange}
      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
    />
  );
}
