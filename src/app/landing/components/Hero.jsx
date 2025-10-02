// components/Hero.jsx
'use client'

import React from 'react';
import Image from 'next/image';
import { ChevronRight } from 'lucide-react';

// --- STEP 1: Import your background image ---
// Make sure the path is correct from this file to your image.
// A common place for images is a folder like `src/assets/`.
import HeroBgImage from '../assets/HeroBg.jpg'; 

const Hero = () => {
  return (
    <section className="relative flex items-center justify-center w-full min-h-screen p-0 m-0 overflow-hidden">
      
      {/* --- STEP 2: Use the Image as the background --- */}
      {/* This is the only div needed for the background. */}
      <div className="absolute inset-0 z-0">
        <Image 
          src={HeroBgImage} // <-- STEP 3: Use the imported image variable here
          alt="Abstract background" 
          layout="fill"
          objectFit="cover"
          priority
          // Optional: Add opacity if your image is too bright for the text
          className="opacity-80" 
        />
        {/* You can add a dark overlay for better text readability if needed */}
        {/* <div className="absolute inset-0 bg-black/30"></div> */}
      </div>

      {/* Hero Content (This stays on top because of the z-index) */}
      <div className="relative z-10 flex flex-col items-center max-w-4xl text-center">
        
        <div className="inline-flex items-center gap-2 px-5 py-2 mt-8 mb-4 text-base font-medium text-gray-600 bg-gray-800/10 border-4 border-white/50 rounded-full shadow-md">
          <span className="text-xl">🦾</span>
          <span className="text-gray-800">Powered by Llama, Docker, and Cerebras</span>
        </div>

        <h1 className="text-5xl font-semibold leading-tight text-[#193242dd] lg:text-6xl">
          Your On-Demand<br />
          Business Strategist.
        </h1>

        <p className="max-w-3xl mt-6 mb-12 text-lg leading-relaxed text-gray-600 lg:text-xl">
          Our AI agent analyzes real-time market trends, competitor locations, and your own data to give you a clear, actionable growth plan.
        </p>

        <form className="flex flex-col w-full max-w-lg gap-3 lg:flex-row">
          <input 
            type="email" 
            placeholder="Enter your email" 
            className="flex-1 px-6 py-4 text-base bg-white border-none rounded-full shadow-lg outline-none font-poppins focus:ring-2 focus:ring-[#4bbbdd]/50"
          />
          <button type="submit" className="flex items-center justify-center gap-3 px-8 py-4 text-base font-light text-white bg-[#4bbbdd] rounded-full cursor-pointer whitespace-nowrap shadow-lg transition-all hover:bg-[#2ca0c3] hover:scale-105 font-poppins">
            Join Waitlist
            <ChevronRight size={20} />
          </button>
        </form>
      </div>
    </section>
  );
};

export default Hero;