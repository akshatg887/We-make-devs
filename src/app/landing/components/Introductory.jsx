// components/Features.jsx
'use client'

import React from "react";
import Image from "next/image"; // <-- Import next/image for optimized images
import RadialBlobs from "../assets/UI elements/RadialBlobs"; // Make sure this path is correct

const Introductory = () => {
  const panels = [
    {
      title: "Idea Stage",
      img: "/assets/idea.png", // Ensure these images are in your `public/assets` folder
      problem: "Have a location, but no idea? Don't risk it on a gut feeling.",
    },
    {
      title: "New Business",
      img: "/assets/new-business.png",
      problem: "Launched your business but struggling to find customers?",
    },
    {
      title: "Established Business",
      img: "/assets/established.png",
      problem: "Sales are down, and you don't know why?",
    },
  ];

  return (
    <section id="features" className="relative py-8 overflow-hidden bg-transparent">
      <RadialBlobs /> 
      <div className="relative z-10 max-w-7xl mx-auto px-6">
        
        <h2 className="text-center text-[3.25rem] font-semibold text-[#2d3d53] mb-8">
          If You're one of these
        </h2>
        
        {/* Responsive Grid: 1 col on mobile, 2 on tablet, 3 on desktop */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {panels.map((panel, index) => (
            <div 
              key={index} 
              className="text-center bg-[#ffffff] rounded-[2.5rem] shadow-lg pb-4 transition-all duration-200 ease-in-out hover:-translate-y-1.5 hover:shadow-xl"
            >
              {/* Using next/image for optimization */}
              <div className="relative w-[21rem] h-[17rem] bg-blue-100 rounded-[1.75rem] mx-auto mb-4 mt-5 overflow-hidden">
                <Image 
                  src={panel.img}
                  alt={`${panel.title} illustration`}
                  layout="fill"
                  objectFit="contain" // Use "cover" or "contain" based on your image
                  className="p-4" // Adds some padding around the image if needed
                />
              </div>
              <h3 className="text-xl font-semibold text-left text-gray-800 pl-8">
                {panel.title}
              </h3>
              <p className="text-left text-gray-700 text-[0.95rem] leading-normal mb-5 px-8">
                {panel.problem}
              </p>
            </div>
          ))}
        </div>
        
        <h2 className="text-center text-4xl font-extralight text-[#2d3d53] mt-16 mb-8">
          Growth Pilot is the perfect choice for you
        </h2>

      </div>
    </section>
  );
};

export default Introductory;