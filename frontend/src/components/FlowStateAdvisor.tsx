import { useEffect, useState } from 'react';
import { Brain, Lightbulb, TrendingUp } from 'lucide-react';
import { AIAdvisor } from '../lib/aiAdvisor';
import { useBrainwaveStore } from '../store/brainwaveStore';

// Initialize AI Advisor with your OpenAI API key
const advisor = new AIAdvisor(process.env.VITE_OPENAI_API_KEY || '');

interface FlowMetrics {
  score: number;
  alphaQuality: number;
  thetaBalance: number;
  betaSuppression: number;
}

export function FlowStateAdvisor() {
  const { delta, theta, alpha, beta, gamma } = useBrainwaveStore();
  const [metrics, setMetrics] = useState<FlowMetrics>({
    score: 0,
    alphaQuality: 0,
    thetaBalance: 0,
    betaSuppression: 0
  });
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const analyzeFlowState = async () => {
      // Only analyze if we have enough data points
      if (alpha.length < 10) return;

      setLoading(true);
      try {
        const result = await advisor.analyzeFlowState({
          delta,
          theta,
          alpha,
          beta,
          gamma
        });

        setMetrics({
          score: result.score,
          alphaQuality: result.alphaQuality,
          thetaBalance: result.thetaBalance,
          betaSuppression: result.betaSuppression
        });
        setRecommendations(result.recommendations);
      } catch (error) {
        console.error('Error analyzing flow state:', error);
      }
      setLoading(false);
    };

    // Analyze flow state every 30 seconds if we have data
    const interval = setInterval(analyzeFlowState, 30000);
    return () => clearInterval(interval);
  }, [delta, theta, alpha, beta, gamma]);

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-orange-600';
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm space-y-6">
      <div className="flex items-center gap-2 mb-4">
        <Brain className="w-5 h-5 text-indigo-600" />
        <h2 className="text-xl font-semibold">Flow State Advisor</h2>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="text-sm text-gray-600">Flow Score</div>
              <div className={`text-2xl font-bold ${getScoreColor(metrics.score)}`}>
                {(metrics.score * 100).toFixed(0)}%
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-sm text-gray-600">Alpha Quality</div>
              <div className={`text-2xl font-bold ${getScoreColor(metrics.alphaQuality)}`}>
                {(metrics.alphaQuality * 100).toFixed(0)}%
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-sm text-gray-600">Theta Balance</div>
              <div className={`text-2xl font-bold ${getScoreColor(metrics.thetaBalance)}`}>
                {(metrics.thetaBalance * 100).toFixed(0)}%
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-sm text-gray-600">Beta Suppression</div>
              <div className={`text-2xl font-bold ${getScoreColor(metrics.betaSuppression)}`}>
                {(metrics.betaSuppression * 100).toFixed(0)}%
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-yellow-600" />
              <h3 className="font-medium">Recommendations</h3>
            </div>
            <ul className="space-y-2">
              {recommendations.map((rec, index) => (
                <li key={index} className="flex items-start gap-2">
                  <TrendingUp className="w-4 h-4 text-indigo-600 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
