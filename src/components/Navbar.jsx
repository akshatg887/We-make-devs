// components/Navbar.jsx
'use client'

import React, { useState } from 'react';
import Link from 'next/link';
import { PlaneTakeoff, Menu, X } from "lucide-react";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => setIsOpen(!isOpen);
  const handleLinkClick = () => setIsOpen(false);

  // Common classes for buttons
  const primaryBtnClasses = "py-3 px-7 rounded-full font-medium text-base text-white bg-blue-500 shadow-[0_4px_14px_rgba(59,130,246,0.25)] transition-all hover:bg-blue-600 hover:scale-105";
  const secondaryBtnClasses = "py-3 px-7 rounded-full font-medium text-base text-gray-700 bg-gray-200 transition-all hover:bg-gray-300 hover:text-gray-800";

  return (
    <header className="absolute top-6 left-0 right-0 flex justify-center z-50">
      <nav className="flex justify-between items-center w-full max-w-6xl py-3 px-6 rounded-full bg-white/90 backdrop-blur-lg border border-gray-200 shadow-lg">
        
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 text-xl ml-2 font-black text-blue-950 font-poppins">
          BizGenie AI
        </Link>

        {/* Desktop Menu & Buttons */}
        <div className="hidden lg:flex items-center gap-8">
          <div className="flex items-center gap-2">
            <a href="/root" className={primaryBtnClasses}>Level up</a>
          </div>
        </div>

        {/* Mobile toggle */}
        <div className="lg:hidden cursor-pointer mt-1 text-[#2CA9D4]" onClick={toggleMenu}>
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </div>

        {/* Mobile Menu */}
        {isOpen && (
           <div className="lg:hidden absolute top-[80px] left-0 w-full px-4">
             {/* --- FIX: Added background, blur, and styling to this container --- */}
                  <a href="/root" className={primaryBtnClasses}>Level up</a>
           </div>
        )}
      </nav>
    </header>
  );
};

export default Navbar;