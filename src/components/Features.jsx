"use client";

import React, { useEffect } from "react";
import { motion, useAnimation } from "framer-motion";
import { useInView } from "react-intersection-observer";
import Image from "next/image";

const featuresData = [
  {
    title: "Geo-Spatial Competitor Analysis",
    description:
      "Pinpoint competitor locations and market penetration with advanced spatial data visualization. Understand market gaps and opportunities with a visual edge.",
    image: "/Geo.png",
    alt: "Geo-Spatial Competitor Analysis Dashboard",
  },
  {
    title: "Real-time Trend Forecasting & CSV Data Diagnosis",
    description:
      "Anticipate market shifts and consumer behavior with AI-driven predictive analytics. Upload your raw CSV data for instant, comprehensive analysis and actionable insights, all in one place.",
    image: "/real.png",
    alt: "Real-time Trend Forecasting Dashboard",
  },
  {
    title: "Interactive Dashboards & Reporting",
    description:
      "Visualize your business metrics with custom, interactive dashboards for informed decision-making. Generate detailed reports to share insights and drive strategy forward.",
    image: "/dashboards.png",
    alt: "Interactive Business Dashboards",
  },
];

// A new component to handle animation for each feature row
const FeatureRow = ({ feature, index }) => {
  const controls = useAnimation();
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.3,
  });

  useEffect(() => {
    if (inView) {
      controls.start("visible");
    }
  }, [controls, inView]);

  const fromLeft = {
    hidden: { opacity: 0, x: -100 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.7, ease: "easeOut" },
    },
  };

  const fromRight = {
    hidden: { opacity: 0, x: 100 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.7, ease: "easeOut" },
    },
  };

  const isReversed = index % 2 === 1;

  return (
    <div
      ref={ref}
      className={`flex flex-col lg:flex-row items-center justify-between gap-12 lg:gap-24 py-16 ${
        isReversed ? "lg:flex-row-reverse" : ""
      }`}
    >
      {/* Text Content */}
      <motion.div
        className="w-full lg:w-1/2 text-center lg:text-left"
        variants={isReversed ? fromRight : fromLeft}
        initial="hidden"
        animate={controls}
      >
        <span className="text-sm font-medium text-blue-700 bg-blue-100/50 px-3 py-1 rounded-full mb-4 inline-block border border-blue-200">
          Llama Integration
        </span>
        <h3 className="text-4xl lg:text-5xl font-semibold text-[#1b2023] mb-4 leading-tight">
          {feature.title}
        </h3>
        <p className="text-lg text-gray-600 mb-8 leading-relaxed">
          {feature.description}
        </p>
      </motion.div>

      {/* Image */}
      <motion.div
        className="w-full lg:w-1/2 flex justify-center"
        variants={isReversed ? fromLeft : fromRight}
        initial="hidden"
        animate={controls}
      >
        <div className="relative w-full max-w-lg h-80 md:h-96 rounded-3xl overflow-hidden shadow-xl border border-gray-200">
           {" "}
          <Image
            src={feature.image}
            alt={feature.alt}
            fill={true}
            style={{ objectFit: "cover" }}
            className="rounded-3xl"
          />
        </div>
      </motion.div>
    </div>
  );
};

const Features = () => {
  const controls = useAnimation();
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.2,
  });

  useEffect(() => {
    if (inView) {
      controls.start("visible");
    }
  }, [controls, inView]);

  const headingVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, ease: "easeOut" },
    },
  };

  return (
    <section
      id="features"
      className="relative bg-transparent py-16 md:py-24 overflow-hidden"
    >
      <div className="relative z-10 max-w-7xl mx-auto px-6">
        <motion.h2
          ref={ref}
          className="text-center text-4xl sm:text-5xl font-semibold tracking-tight text-[#1b4963] mb-16 leading-tight"
          variants={headingVariants}
          initial="hidden"
          animate={controls}
        >
          What Makes <br /> GrowthPilot Effortless Yet Powerful
        </motion.h2>

        {featuresData.map((feature, index) => (
          <FeatureRow key={index} feature={feature} index={index} />
        ))}
      </div>
    </section>
  );
};

export default Features;
