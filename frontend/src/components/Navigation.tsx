import { Link, useLocation } from 'react-router-dom';
import { Activity, History, Brain } from 'lucide-react';

export function Navigation() {
  const location = useLocation();

  const links = [
    { to: '/', label: 'Dashboard', icon: Activity },
    { to: '/training', label: 'Training', icon: Brain },
    { to: '/history', label: 'History', icon: History },
  ];

  return (
    <nav className="bg-white shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <Brain className="w-6 h-6 text-indigo-600" />
            <span className="text-xl font-bold text-gray-900">NeuroFeedback</span>
          </div>
          
          <div className="flex space-x-4">
            {links.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  location.pathname === to
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Icon className="w-5 h-5" />
                {label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}