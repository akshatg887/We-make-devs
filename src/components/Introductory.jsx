"use client";

import React, { useEffect, useRef } from "react";
// Removed next/image import and local asset imports
import { motion, useAnimation } from "framer-motion";
import { useInView } from "react-intersection-observer";
import Image from "next/image"; // <-- Import next/image for optimized images
const New = "/new.png";
const Idea = "/idea.png";
const Established = "/Established.png";

const Introductory = () => {
  const panels = [
    {
      title: "Idea Stage",
      img: Idea, // Placeholder image
      problem: "Have a location, but no idea? Don't risk it on a gut feeling.",
    },
    {
      title: "New Business",
      img: New, // Placeholder image
      problem: "Launched your business but struggling to find customers?",
    },
    {
      title: "Established Business",
      img: Established, // Placeholder image
      problem: "Sales are down, and you don't know why?",
    },
  ];

  const controls = useAnimation();
  const { ref, inView } = useInView({
    triggerOnce: false, // Animation triggers only once
    threshold: 0.2, // Triggers when 20% of the component is visible
  });

  useEffect(() => {
    if (inView) {
      controls.start("visible");
    }
  }, [controls, inView]);

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
    hidden: { opacity: 0, y: 50, filter: "blur(5px)" },
    visible: {
      opacity: 1,
      y: 0,
      filter: "blur(0px)",
      transition: {
        duration: 0.6,
        ease: "easeOut",
      },
    },
  };

  return (
    <motion.section
      id="features"
      ref={ref}
      className="relative py-16 overflow-hidden bg-transparent"
      initial="hidden"
      animate={controls}
      variants={containerVariants} // Apply container variants here
    >
      <div className="relative z-15 max-w-7xl mx-auto px-6">
        <motion.h2
          variants={itemVariants}
          className="text-center text-[3.25rem] font-semibold text-[#2d3d53] mb-0"
        >
          If You're one of these
        </motion.h2>
        <motion.h2
          variants={itemVariants}
          className="text-center text-4xl font-extralight text-[#2d3d53] mt-0 mb-12"
        >
          Growth Pilot is the perfect choice for you
        </motion.h2>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
          variants={containerVariants}
        >
          {panels.map((panel, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="text-center bg-[#ffffff] rounded-[2.5rem] shadow-lg pb-4 transition-all duration-200 ease-in-out hover:-translate-y-1.5 hover:shadow-xl"
            >
              <div className="relative w-[21rem] h-[17rem] bg-blue-100 rounded-[1.75rem] mx-auto mb-4 mt-5 overflow-hidden">
                {/* Replaced next/image with a standard img tag */}
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
            </motion.div>
          ))}
        </motion.div>
      </div>
    </motion.section>
  );
};

export default Introductory;
