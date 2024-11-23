import { useEffect, useState } from 'react';
import { AdaptiveAudioEngine } from '../lib/adaptiveAudioEngine';
import { FlowTriggerSystem, FlowActivity, FlowTrigger } from '../lib/flowTriggers';
import { Brain, Play, Square, Volume2, Coffee, Moon, Zap, Target, Activity, Layout } from 'lucide-react';
import { useBrainwaveStore } from '../store/brainwaveStore';

const audioEngine = new AdaptiveAudioEngine(process.env.VITE_OPENAI_API_KEY || '');
const flowSystem = new FlowTriggerSystem(process.env.VITE_OPENAI_API_KEY || '');

interface UserState {
  energy: number;
  skill: number;
  fatigue: number;
  caffeineLevel: number;
  lastSleep: number;
}

export function FlowTraining() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(0.1);
  const [selectedActivity, setSelectedActivity] = useState<FlowActivity | null>(null);
  const [activities, setActivities] = useState<FlowActivity[]>([]);
  const [flowTriggers, setFlowTriggers] = useState<FlowTrigger[]>([]);
  const [userState, setUserState] = useState<UserState>({
    energy: 0.7,
    skill: 0.5,
    fatigue: 0.5,
    caffeineLevel: 0.5,
    lastSleep: 8,
  });
  const [recommendation, setRecommendation] = useState<any>(null);
  const { delta, theta, alpha, beta, gamma } = useBrainwaveStore();

  useEffect(() => {
    // Load available activities and triggers
    setActivities(flowSystem.getAvailableActivities());
    setFlowTriggers(flowSystem.getFlowTriggers());
  }, []);

  useEffect(() => {
    if (isPlaying) {
      // Update brainwave response every 5 seconds
      const brainwaveInterval = setInterval(() => {
        audioEngine.updateBrainwaveResponse({
          alpha: alpha[alpha.length - 1] || 0,
          theta: theta[theta.length - 1] || 0,
          beta: beta[beta.length - 1] || 0,
          gamma: gamma[gamma.length - 1] || 0,
        });
      }, 5000);

      return () => clearInterval(brainwaveInterval);
    }
  }, [isPlaying, alpha, theta, beta, gamma]);

  const handleActivitySelect = async (activity: FlowActivity) => {
    setSelectedActivity(activity);
    
    // Get flow trigger recommendations
    const recommendation = await flowSystem.recommendFlowTriggers({
      energy: userState.energy,
      skill: userState.skill,
      timeOfDay: new Date().getHours(),
      previousSuccess: flowSystem.getUserProfile().preferredTriggers,
    }, activity.id);
    
    setRecommendation(recommendation);
  };

  const handleStart = async () => {
    if (!selectedActivity) return;

    if (isPlaying) {
      audioEngine.stop();
      setIsPlaying(false);
    } else {
      await audioEngine.start('focus', {
        fatigue: userState.fatigue,
        caffeineLevel: userState.caffeineLevel,
        lastSleep: userState.lastSleep,
      });
      setIsPlaying(true);
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    audioEngine.setVolume(newVolume);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 p-6">
      <header className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Flow Training</h1>
        <p className="text-gray-600">Optimize your flow state with research-backed triggers and neural entrainment</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Activity Selection */}
        <div className="space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Target className="w-5 h-5 text-indigo-600" />
            Select Activity
          </h2>
          <div className="grid gap-4">
            {activities.map((activity) => (
              <button
                key={activity.id}
                onClick={() => handleActivitySelect(activity)}
                className={`p-4 rounded-lg border transition-colors ${
                  selectedActivity?.id === activity.id
                    ? 'border-indigo-600 bg-indigo-50'
                    : 'border-gray-200 hover:border-indigo-300'
                }`}
              >
                <h3 className="font-medium text-gray-900">{activity.name}</h3>
                <p className="text-sm text-gray-600">{activity.description}</p>
                <div className="mt-2 flex gap-2 text-xs text-gray-500">
                  <span>{activity.duration}min</span>
                  <span>•</span>
                  <span>Difficulty: {(activity.difficulty * 100).toFixed(0)}%</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* User State & Controls */}
        <div className="space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-600" />
            Current State
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <Brain className="w-4 h-4" />
                Energy Level
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={userState.energy}
                onChange={(e) =>
                  setUserState((prev) => ({
                    ...prev,
                    energy: parseFloat(e.target.value),
                  }))
                }
                className="w-full"
              />
              <div className="text-sm text-gray-600">
                {(userState.energy * 100).toFixed(0)}%
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <Target className="w-4 h-4" />
                Skill Level
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={userState.skill}
                onChange={(e) =>
                  setUserState((prev) => ({
                    ...prev,
                    skill: parseFloat(e.target.value),
                  }))
                }
                className="w-full"
              />
              <div className="text-sm text-gray-600">
                {(userState.skill * 100).toFixed(0)}%
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <Moon className="w-4 h-4" />
                Fatigue Level
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={userState.fatigue}
                onChange={(e) =>
                  setUserState((prev) => ({
                    ...prev,
                    fatigue: parseFloat(e.target.value),
                  }))
                }
                className="w-full"
              />
              <div className="text-sm text-gray-600">
                {(userState.fatigue * 100).toFixed(0)}%
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <Coffee className="w-4 h-4" />
                Caffeine Level
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={userState.caffeineLevel}
                onChange={(e) =>
                  setUserState((prev) => ({
                    ...prev,
                    caffeineLevel: parseFloat(e.target.value),
                  }))
                }
                className="w-full"
              />
              <div className="text-sm text-gray-600">
                {(userState.caffeineLevel * 100).toFixed(0)}%
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <Volume2 className="w-4 h-4" />
                Volume
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={volume}
                onChange={handleVolumeChange}
                className="w-full"
              />
            </div>

            <button
              onClick={handleStart}
              disabled={!selectedActivity}
              className={`w-full flex items-center justify-center gap-2 px-6 py-3 rounded-lg transition-colors ${
                !selectedActivity
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : isPlaying
                  ? 'bg-red-600 text-white hover:bg-red-700'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
              }`}
            >
              {isPlaying ? (
                <>
                  <Square className="w-5 h-5" />
                  Stop Session
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Start Session
                </>
              )}
            </button>
          </div>
        </div>

        {/* Flow Recommendations */}
        <div className="space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Layout className="w-5 h-5 text-indigo-600" />
            Flow Optimization
          </h2>
          
          {recommendation ? (
            <div className="space-y-6">
              {/* Environmental Setup */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium text-gray-900 mb-2">Environment</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>Lighting: {recommendation.environment.lighting}</li>
                  <li>Sound: {recommendation.environment.sound}</li>
                  <li>Space: {recommendation.environment.space}</li>
                </ul>
              </div>

              {/* Flow Triggers */}
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Trigger Sequence</h3>
                <div className="space-y-3">
                  {recommendation.sequence.map((step: any, index: number) => (
                    <div
                      key={index}
                      className="flex items-center gap-3 text-sm"
                    >
                      <div className="w-12 text-gray-500">
                        {step.timing}min
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">
                          {flowTriggers.find(t => t.id === step.trigger)?.name}
                        </div>
                        <div className="text-gray-600">
                          Intensity: {(step.intensity * 100).toFixed(0)}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Challenges */}
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Progressive Challenges</h3>
                <div className="space-y-3">
                  {recommendation.challenges.map((challenge: any, index: number) => (
                    <div
                      key={index}
                      className="bg-white p-3 rounded-lg border border-gray-200"
                    >
                      <div className="font-medium text-gray-900">
                        {challenge.description}
                      </div>
                      <div className="text-sm text-gray-600">
                        Difficulty: {(challenge.difficulty * 100).toFixed(0)}% •{' '}
                        Duration: {challenge.duration}min
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              Select an activity to get personalized flow recommendations
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
