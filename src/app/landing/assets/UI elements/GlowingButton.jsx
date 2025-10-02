// components/GlowingButton.jsx
'use client'

import React from 'react';
import { ChevronRight } from 'lucide-react';

const GlowingButton = ({ text = "Get Inshort" }) => {
  return (
    <button
      className="
        inline-flex items-center gap-2
        px-6 py-3
        bg-[#1c344d] text-white
        font-medium text-base
        rounded-full
        transition-all duration-300
        curosr-pointer
        // --- This is the key part for the shadow ---
        shadow-[0_5px_0px_rgba(59,130,246,0.3)] 

        // --- Hover Effects ---
        hover:bg-[#1c344d]
        hover:-translate-y-0.5
        hover:shadow-[0_0px_0px_rgba(59,130,246,0.45)]
        hover:cursor-pointer
      "
    >
      {text}
      <ChevronRight size={20} />
    </button>
  );
};

export default GlowingButton;