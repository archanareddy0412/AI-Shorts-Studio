"use client";

import { Menu, Sparkles } from "lucide-react";

export default function Navbar() {
  return (
    <header className="fixed top-0 left-0 w-full z-50">
      <div className="mx-auto max-w-7xl px-6 py-5">
        <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl px-6 py-4">

          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-blue-600 flex items-center justify-center">
              <Sparkles className="text-white" size={20}/>
            </div>

            <div>
              <h1 className="text-xl font-bold text-white">
                AI Shorts Studio
              </h1>

              <p className="text-xs text-gray-400">
                AI Video Clipping
              </p>
            </div>
          </div>

          <nav className="hidden md:flex gap-10 text-gray-300">

            <a href="#" className="hover:text-white">
              Features
            </a>

            <a href="#">
              Dashboard
            </a>

            <a href="#">
              Documentation
            </a>

            <a href="#">
              About
            </a>

          </nav>

          <div className="hidden md:flex gap-3">

            <button className="px-5 py-2 rounded-lg text-white hover:bg-white/10">
              Login
            </button>

            <button className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold">
              Get Started
            </button>

          </div>

          <button className="md:hidden">
            <Menu className="text-white"/>
          </button>

        </div>
      </div>
    </header>
  );
}