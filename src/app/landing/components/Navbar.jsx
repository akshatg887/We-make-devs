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
  const primaryBtnClasses = "py-3 px-7 rounded-full font-medium text-base text-white bg-[#3dbbe1] shadow-[0_4px_14px_rgba(59,130,246,0.25)] transition-all hover:bg-[#2ca0c3] hover:scale-105";
  const secondaryBtnClasses = "py-3 px-7 rounded-full font-medium text-base text-gray-700 bg-gray-200 transition-all hover:bg-gray-300 hover:text-gray-800";

  return (
    <header className="absolute top-6 left-0 right-0 flex justify-center z-50">
      <nav className="flex justify-between items-center w-full max-w-6xl py-3 px-6 rounded-full bg-white/90 backdrop-blur-lg border border-gray-200 shadow-lg">
        
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 text-xl font-light text-[#2ca0c3] font-poppins">
          <PlaneTakeoff size={25} strokeWidth={1.5} />
          GrowthPilot
        </Link>

        {/* Desktop Menu & Buttons */}
        <div className="hidden lg:flex items-center gap-8">
          <ul className="flex items-center gap-8 list-none m-0 p-0">
            <li><Link href="#features" className="text-gray-600 font-medium transition-colors hover:text-gray-900">Features</Link></li>
            <li><Link href="#use-cases" className="text-gray-600 font-medium transition-colors hover:text-gray-900">Use Cases</Link></li>
            <li><Link href="#pricing" className="text-gray-600 font-medium transition-colors hover:text-gray-900">Pricing</Link></li>
          </ul>
          <div className="flex items-center gap-2">
            <button className={secondaryBtnClasses}>Log in</button>
            <button className={primaryBtnClasses}>Level up</button>
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
             <ul className=" h-[85vh] flex flex-col items-center gap-8 p-8 bg-white/95 backdrop-blur-lg rounded-3xl shadow-xl border border-gray-200">
                <li><Link href="#features" className="text-gray-600 font-medium transition-colors hover:text-gray-900 text-lg" onClick={handleLinkClick}>Features</Link></li>
                <li><Link href="#use-cases" className="text-gray-600 font-medium transition-colors hover:text-gray-900 text-lg" onClick={handleLinkClick}>Use Cases</Link></li>
                <li><Link href="#pricing" className="text-gray-600 font-medium transition-colors hover:text-gray-900 text-lg" onClick={handleLinkClick}>Pricing</Link></li>
                <li className="flex flex-col gap-4 w-full pt-4 border-t border-gray-200">
                  <button className={`${secondaryBtnClasses} w-full rounded-xl`}>Log in</button>
                  <button className={`${primaryBtnClasses} w-full rounded-xl `}>Level up</button>
                </li>
             </ul>
           </div>
        )}
      </nav>
    </header>
  );
};

export default Navbar;