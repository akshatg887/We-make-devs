// components/Features.jsx
'use client';

import React from 'react';
import Image from 'next/image';
import { ChevronRight } from 'lucide-react';
import GlowingButton from '../assets/UI elements/GlowingButton';
// import RadialBlobs from './assets/UI elements/RadialBlobs'; // Keep if you want blobs in this section, remove if not.

// New data structure for the alternating feature layout
const featuresData = [
  {
    title: 'Geo-Spatial Competitor Analysis',
    description: 'Pinpoint competitor locations and market penetration with advanced spatial data visualization. Understand market gaps and opportunities with a visual edge.',
    image: '/assets/feature-analysis.png', // <-- REPLACE with your actual image path
    alt: 'Geo-Spatial Competitor Analysis Dashboard',
    buttonText: 'Explore Analysis',
  },
  {
    title: 'Real-time Trend Forecasting & CSV Data Diagnosis', // Combined title
    description: 'Anticipate market shifts and consumer behavior with AI-driven predictive analytics. Upload your raw CSV data for instant, comprehensive analysis and actionable insights, all in one place.', // Combined description
    image: '/assets/feature-forecasting.png', // <-- REPLACE with your actual image path
    alt: 'Real-time Trend Forecasting Dashboard',
    buttonText: 'Try Forecasting',
  },
  {
    title: 'Interactive Dashboards & Reporting', // Renamed for clarity after merging
    description: 'Visualize your business metrics with custom, interactive dashboards for informed decision-making. Generate detailed reports to share insights and drive strategy forward.', // Combined description
    image: '/assets/feature-dashboards.png', // <-- REPLACE with your actual image path
    alt: 'Interactive Business Dashboards',
    buttonText: 'View Dashboards',
  },
];

const Features = () => {
  return (
    <section id="features" className="relative bg-white py-16 md:py-24">
      {/* If you want radial blobs here, uncomment this line: */}
      {/* <RadialBlobs /> */} 

      <div className="relative z-10 max-w-7xl mx-auto px-6">
        
        <h2 className="text-center text-5xl sm:text-5xl font-regular tracking-tight text-[#1b4963] mb-16 leading-15">
          What Makes <br/> GrowthPilot Effortless Yet Powerful
        </h2>

        {featuresData.map((feature, index) => (
          <div 
            key={index} 
            className={`flex flex-col lg:flex-row items-center justify-between gap-12 lg:gap-24 py-16 ${index % 2 === 1 ? 'lg:flex-row-reverse' : ''}`}
          >
            {/* Text Content */}
            <div className="w-full lg:w-1/2 text-center lg:text-left">
              {/* Optional: Add a subtle badge/tag here if needed */}
              <span className="text-sm font-regular text-gray-600 bg-blue-50/5 px-3 py-1 rounded-full mb-4 inline-block border-1">Llama Integration</span>
              <h3 className="text-5xl font-semibold text-[#1b2023] mb-4 leading-tight">
                {feature.title}
              </h3>
              <p className="text-lg text-gray-600 mb-8 leading-relaxed">
                {feature.description}
              </p>
              <GlowingButton text='Try now'/>
            </div>

            {/* Image */}
            <div className="w-full lg:w-1/2 flex justify-center lg:justify-end">
              <div className="relative w-full max-w-lg h-80 md:h-96 bg-gray-100 rounded-3xl overflow-hidden shadow-xl border border-gray-200">
                <Image 
                  src={feature.image} 
                  alt={feature.alt} 
                  layout="fill" 
                  objectFit="cover" // or 'contain' depending on your images
                  className="rounded-3xl"
                />
              </div>
            </div>
          </div>
        ))}

      </div>
    </section>
  );
};

export default Features;