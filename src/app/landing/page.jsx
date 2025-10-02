import React from 'react'
import Hero from './components/Hero'
import Navbar from './components/Navbar'
import Demo from './components/Demo'
import Introductory from './components/Introductory'
import '../globals.css'
import Sponsors from './components/Sponsors'
import Features from './components/Features'

const page = () => {
  return (
    <div>
        <Navbar/>
        <Hero/>
        <Introductory/>
        <Demo />
        <Features />
        <Sponsors/>
    </div>
  )
}

export default page
