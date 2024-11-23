import { LineChart, Timer, Calendar } from 'lucide-react';

export function History() {
  // Simulated session history data
  const sessions = [
    {
      date: '2024-02-28',
      duration: '30 minutes',
      type: 'Alpha Training',
      peakAlpha: 0.82,
    },
    {
      date: '2024-02-27',
      duration: '20 minutes',
      type: 'Theta Training',
      peakAlpha: 0.75,
    },
    {
      date: '2024-02-26',
      duration: '45 minutes',
      type: 'Alpha Training',
      peakAlpha: 0.91,
    },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <header className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Session History</h1>
        <p className="text-gray-600">Track your progress over time</p>
      </header>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Sessions</h2>
          <div className="space-y-4">
            {sessions.map((session, index) => (
              <div
                key={index}
                className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-gray-500" />
                    <span>{session.date}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Timer className="w-5 h-5 text-gray-500" />
                    <span>{session.duration}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Brain className="w-5 h-5 text-gray-500" />
                    <span>{session.type}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <LineChart className="w-5 h-5 text-gray-500" />
                    <span>Peak Alpha: {session.peakAlpha}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold mb-2">Total Sessions</h3>
          <p className="text-3xl font-bold text-indigo-600">24</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold mb-2">Average Duration</h3>
          <p className="text-3xl font-bold text-indigo-600">32 min</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold mb-2">Peak Alpha Score</h3>
          <p className="text-3xl font-bold text-indigo-600">0.91</p>
        </div>
      </div>
    </div>
  );
}