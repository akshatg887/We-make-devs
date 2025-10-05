import React from "react";
import Hero from "../components/Hero";
import Navbar from "../components/Navbar";
import Demo from "../components/Demo";
import Introductory from "../components/Introductory";
import "./globals.css";
import Sponsors from "../components/Sponsors";
import Features from "../components/Features";
import Blob from "./landing/components/Blob";
const page = () => {
  return (
    <>
      <Blob color="#6894f2" />
      <Blob color="#6894f2" />
      <main className="relative z-10">
        <Navbar />
        <Hero />
        <Introductory />
        <Features />
        <Sponsors />
      </main>
    </>
  );
};

export default page;
