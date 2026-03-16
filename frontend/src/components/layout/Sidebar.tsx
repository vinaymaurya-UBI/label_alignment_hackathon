import React from "react";
import { NavLink } from "react-router-dom";
import { 
  LayoutDashboard, 
  Pill, 
  ArrowLeftRight, 
  BarChart3, 
  History,
  Settings,
  HelpCircle,
  LogOut,
  Globe,
  Search
} from "lucide-react";
import { cn } from "../../lib/utils";

const Sidebar = () => {
  const navItems = [
    { icon: LayoutDashboard, label: "Dashboard", path: "/" },
    { icon: Search, label: "Intelligence Search", path: "/search" },
    { icon: ArrowLeftRight, label: "Comparison", path: "/compare/selection" },
    { icon: BarChart3, label: "Analytics", path: "/analytics" },
    { icon: History, label: "History", path: "/history" },
  ];

  return (
    <aside className="fixed left-0 top-0 h-screen w-72 bg-white border-r border-slate-100 flex flex-col p-6 z-50">
      {/* Logo */}
      <div className="flex items-center gap-3 px-2 mb-10">
        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary/20">
          <Globe className="text-white w-6 h-6" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-slate-900 leading-none">NeuroNext</h1>
          <span className="text-xs font-medium text-slate-400">Regulatory Intel</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => 
              isActive ? "sidebar-item-active" : "sidebar-item"
            }
          >
            <item.icon className="w-5 h-5" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
