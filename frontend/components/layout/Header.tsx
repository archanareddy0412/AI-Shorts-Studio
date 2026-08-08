"use client";

import { Bell, UserCircle } from "lucide-react";

export default function Header() {
  return (
    <header className="flex items-center justify-between border-b border-white/10 pb-6">
      <div>
        <h1 className="text-3xl font-bold text-white">
          Dashboard
        </h1>

        <p className="text-gray-400 mt-2">
          Upload videos and let AI create viral clips.
        </p>
      </div>

      <div className="flex items-center gap-5">
        <button className="rounded-xl bg-white/5 p-3 hover:bg-white/10 transition">
          <Bell className="text-white" size={22} />
        </button>

        <button className="rounded-full bg-blue-600 p-2">
          <UserCircle className="text-white" size={32} />
        </button>
      </div>
    </header>
  );
}