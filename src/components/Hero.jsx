// components/Hero.jsx
'use client'

import React from 'react';
import Image from 'next/image';
import { ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';

const DataIcon = (props) => (
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" {...props}>
    <path d="M4 18H20" stroke="currentColor" strokeWidth="1" strokeLinecap="round"/>
    <path d="M7 14V18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    <path d="M12 10V18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    <path d="M17 6V18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    <path d="M4 4.5L6.5 6L9 4L12 7L15 5L17.5 8L20 6" stroke="currentColor" strokeWidth="0.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.7"/>
  </svg>
);

const LocationIcon = (props) => (
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" {...props}>
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" fill="currentColor" opacity="0.3"/>
        <circle cx="12" cy="9.5" r="1.5" fill="white" opacity="0.8"/>
    </svg>
);

const InsightIcon = (props) => (
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" {...props}>
        <path d="M9 18.21C9 18.76 9.45 19.21 10 19.21H14C14.55 19.21 15 18.76 15 18.21V18H9V18.21Z" fill="currentColor" opacity="0.8"/>
        <path d="M12 2C8.69 2 6 4.69 6 8C6 10.38 7.19 12.47 9 13.74V16C9 16.55 9.45 17 10 17H14C14.55 17 15 16.55 15 16V13.74C16.81 12.47 18 10.38 18 8C18 4.69 15.31 2 12 2Z" fill="currentColor" opacity="0.4"/>
        <path d="M4 11H2M22 11H20M12 20V22M7.05 6.05L5.64 4.64M18.36 17.36L16.95 15.95" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
);



// FloatingIcon component for reusable animation logic
const FloatingIcon = ({ icon: Icon, className, duration = 5, delay = 0 }) => (
    <motion.div
        className={`absolute z-10 text-blue-400/60 drop-shadow-lg ${className}`}
        animate={{
            y: ["-12px", "12px"],
            x: ["-8px", "8px"],
        }}
        transition={{
            duration,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut",
            delay,
        }}
    >
        <Icon className="w-full h-full" />
    </motion.div>
);

const Hero = () => {
   const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20, filter: 'blur(5px)' },
    visible: {
      opacity: 1,
      y: 0,
      filter: 'blur(0px)',
      transition: {
        duration: 0.6,
        ease: "easeOut",
      },
    },
  };
  return (
    <section className="relative flex items-center justify-center w-full min-h-screen p-0 m-0 overflow-hidden">
      <div className="relative z-15 flex flex-col items-center max-w-4xl text-center">
      <FloatingIcon icon={DataIcon} className="w-24 h-24 top-[0%] left-[0%] hidden md:block" duration={8} delay={0.5} />
      <FloatingIcon icon={LocationIcon} className="w-20 h-20 top-[15%] right-[5%]" duration={7} delay={1} />
      <FloatingIcon icon={InsightIcon} className="w-16 h-16 bottom-[0%] left-[10%] hidden lg:block" duration={9} />

        <div className="inline-flex items-center gap-2 px-5 py-2 mt-8 mb-4 text-base font-medium text-gray-600 bg-gray-800/10 border-4 border-white/50 rounded-full shadow-md">
          <span className="text-xl">🦾</span>
          <span className="text-gray-900">Powered by Llama and Cerebras</span>
        </div>

        <h1 className="text-5xl font-bold leading-tight text-[#193242dd] lg:text-6xl">
          Your On-Demand<br />
          <span className='text-blue-500 text-6xl'>Business</span> Strategist.
        </h1>

        <p className="max-w-3xl mt-6 mb-12 text-lg leading-relaxed text-gray-600 lg:text-xl">
          Our AI agent analyzes real-time market trends, competitor locations, and your own data to give you a clear, actionable growth plan.
        </p>
        
      </div>
    </section>
  );
};

export default Hero;