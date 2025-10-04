import React from 'react'
import Hero from './components/hero'
import Navbar from './components/navbar'
import Demo from './components/demo'
import Introductory from './components/introductory'
import '../globals.css'
import Sponsors from './components/sponsors'
import Features from './components/features'
import RadialBlobs from './assets/UI elements/RadialBlobs'
const page = () => {
  return (
    <>
    <RadialBlobs />

    <main className="relative z-10">
        <Navbar/>
        <Hero/>
        <Introductory/>
        <Demo />
        <Features />
        <Sponsors/>
    </main>
    </>
  )
}

export default page