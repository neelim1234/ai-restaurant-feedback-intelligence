import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, BarChart3, LineChart, Utensils } from 'lucide-react';

export default function Sidebar() {
  const menuItems = [
    { name: 'Executive Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Branch Performance', path: '/branches', icon: BarChart3 },
    { name: 'Deep Insights', path: '/insights', icon: LineChart },
  ];

  return (
    <aside className="w-64 bg-[#0f172a] border-r border-slate-800 flex flex-col min-h-screen text-slate-300">
      {/* Brand Logo */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-2 select-none">
        <div className="p-1.5 bg-indigo-600 rounded-lg text-white">
          <Utensils className="h-5 w-5" />
        </div>
        <span className="font-bold text-lg text-slate-100 tracking-tight">FeedbackIQ</span>
        <span className="text-[10px] bg-slate-800 text-indigo-400 font-semibold px-1.5 py-0.5 rounded">B2B</span>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 py-6 px-4 space-y-1.5">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 font-medium text-sm select-none ${
                isActive
                  ? 'bg-indigo-600/10 text-indigo-400 border-l-4 border-indigo-500 font-semibold'
                  : 'hover:bg-slate-800/60 hover:text-slate-100 text-slate-400'
              }`
            }
          >
            <item.icon className="h-4.5 w-4.5" />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer / Meta */}
      <div className="p-4 border-t border-slate-800 text-xs text-slate-500 text-center select-none">
        v1.0.0 &bull; Platform Core
      </div>
    </aside>
  );
}
