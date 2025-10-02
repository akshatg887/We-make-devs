// components/Demo.jsx
'use client'

import React from 'react';
import RadialBlobs from '../assets/UI elements/RadialBlobs'; // Make sure this path is correct

const Demo = () => {
  return (
    // Converted from .demo-section
    <section className="relative overflow-hidden bg-transparent py-8">
      
      {/* Converted from .video-bg */}
      {/* flex, items-center, and justify-center are used to center the child div */}
      <div className="relative flex items-center justify-center w-4/5 h-[700px] mx-auto overflow-hidden bg-transparent border-0 shadow-xl rounded-[2.5rem]">
        
        {/* The blobs will be contained within this div */}
        <RadialBlobs />
        
        {/* Converted from .video-container */}
        {/* flex, items-center, and justify-center are used to center the <p> tag */}
        <div className="relative flex items-center justify-center w-[95%] h-[650px] overflow-hidden bg-transparent border-2 border-[#d9e7eea7] rounded-[2rem]">
          <p className="text-center">video container</p>
        </div>

      </div>
    </section>
  );
};

export default Demo;