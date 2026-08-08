"use client";

import Link from "next/link";
import {
  Home,
  Upload,
  FolderOpen,
  Activity,
  Settings,
  Sparkles,
} from "lucide-react";

const menu = [
  { name: "Home", href: "/", icon: Home },
  { name: "Upload", href: "/dashboard", icon: Upload },
  { name: "Projects", href: "#", icon: FolderOpen },
  { name: "Processing", href: "#", icon: Activity },
  { name: "Settings", href: "#", icon: Settings },
];

export default function Sidebar() {
  return (
    <aside className="w-72 bg-[#0B1220] border-r border-white/10 flex flex-col">
      <div className="p-8 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-3 rounded-xl">
            <Sparkles className="text-white" size={22} />
          </div>

          <div>
            <h1 className="text-white font-bold text-xl">
              AI Shorts Studio
            </h1>

            <p className="text-gray-400 text-sm">
              Personal Edition
            </p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {menu.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className="flex items-center gap-4 rounded-xl px-4 py-3 text-gray-300 hover:bg-blue-600 hover:text-white transition"
          >
            <item.icon size={20} />
            {item.name}
          </Link>
        ))}
      </nav>

      <div className="p-5 border-t border-white/10">
        <div className="rounded-xl bg-blue-600/20 p-4">
          <p className="text-white font-semibold">
            AI Engine
          </p>

          <p className="text-green-400 text-sm mt-2">
            Ready
          </p>
        </div>
      </div>
    </aside>
)}