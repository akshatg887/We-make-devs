// components/Hero.jsx
"use client";

import React from "react";
import Image from "next/image";
import { ChevronRight } from "lucide-react";

const Hero = () => {
  return (
    <section className="relative flex items-center justify-center w-full min-h-screen p-0 m-0 overflow-hidden">
      <div className="relative z-15 flex flex-col items-center max-w-4xl text-center">
        <div className="inline-flex items-center gap-2 px-5 py-2 mt-8 mb-4 text-base font-medium text-gray-600 bg-gray-800/10 border-4 border-white/50 rounded-full shadow-md">
          <span className="text-xl">🦾</span>
          <span className="text-gray-800">
            Powered by Llama, Docker, and Cerebras
          </span>
        </div>

        <h1 className="text-5xl font-bold leading-tight text-[#193242dd] lg:text-6xl">
          Your On-Demand
          <br />
          <span className="text-blue-500">Business</span> Strategist.
        </h1>

        <p className="max-w-3xl mt-6 mb-12 text-lg leading-relaxed text-gray-600 lg:text-xl">
          Our AI agent analyzes real-time market trends, competitor locations,
          and your own data to give you a clear, actionable growth plan.
        </p>
      </div>
    </section>
  );
};

export default Hero;
