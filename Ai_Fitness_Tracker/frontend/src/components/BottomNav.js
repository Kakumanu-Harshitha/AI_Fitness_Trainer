import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, Dumbbell, TrendingUp, Trophy, User } from 'lucide-react';

const BottomNav = () => {
  const navItems = [
    { to: '/dashboard', icon: Home, label: 'Home' },
    { to: '/workouts', icon: Dumbbell, label: 'Workouts' },
    { to: '/stats', icon: TrendingUp, label: 'Stats' },
    { to: '/leaderboard', icon: Trophy, label: 'Leader' },
    { to: '/profile', icon: User, label: 'Profile' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-zinc-950/80 backdrop-blur-lg border-t border-zinc-900 px-4 py-3 z-50">
      <div className="max-w-2xl mx-auto flex justify-between items-center">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => 
              `flex flex-col items-center gap-1 transition-all duration-300 ${
                isActive ? 'text-primary' : 'text-zinc-500'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon 
                  size={24} 
                  className={isActive ? 'scale-110' : 'scale-100'} 
                  fill={isActive ? 'currentColor' : 'none'}
                  fillOpacity={isActive ? 0.2 : 0}
                />
                <span className="text-[10px] font-bold uppercase tracking-tighter">{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
};

export default BottomNav;
