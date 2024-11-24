import React, { useState } from 'react';
import Wavelet from './Wavelet';

const WaveletDemo: React.FC = () => {
  const [waveletData, setWaveletData] = useState({
    delta: 100,
    theta: 80,
    lowAlpha: 60,
    highAlpha: 50,
    lowBeta: 40,
    highBeta: 30,
    lowGamma: 20,
    highGamma: 10,
  });

  const handleRandomize = () => {
    setWaveletData({
      delta: Math.random() * 100,
      theta: Math.random() * 100,
      lowAlpha: Math.random() * 100,
      highAlpha: Math.random() * 100,
      lowBeta: Math.random() * 100,
      highBeta: Math.random() * 100,
      lowGamma: Math.random() * 100,
      highGamma: Math.random() * 100,
    });
  };

  return (
    <div className="flex flex-col items-center space-y-4 p-4">
      <h1 className="text-2xl font-bold">Wavelet Component Demo</h1>
      <div className="flex space-x-4">
        <Wavelet data={waveletData} size={100} interactive={true} />
        <Wavelet data={waveletData} size={60} />
      </div>
      <button
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        onClick={handleRandomize}
      >
        Randomize Data
      </button>
    </div>
  );
};

export default WaveletDemo;

