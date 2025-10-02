'use client'

import React from 'react';
import Image from 'next/image';

// Import your assets
import cerebrasLogo from '../assets/cerebras-color.png'; // Ensure paths are correct
import dockerLogo from '../assets/docker.png';
import metaLogo from '../assets/meta.png';

const Sponsors = () => {
  return (
    <section className="pb-16 md:pb-24">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mt-12 md:mt-20">
          <div className="flex flex-wrap items-center justify-center gap-x-14 gap-y-10 mt-8">
            <div className="flex items-center gap-3 text-2xl font-bold text-gray-800 mb-6">
              <Image src={metaLogo} alt="Meta Llama Logo" width={40} height={40} />
              <span>Llama</span>
            </div>
            <div className="flex items-center gap-3 text-2xl font-bold text-gray-800 mb-6">
              <Image src={dockerLogo} alt="Docker Logo" width={40} height={40} />
              <span>Docker</span>
            </div>
            <div className="flex items-center gap-3 text-2xl font-bold text-gray-800 mb-6">
              <Image src={cerebrasLogo} alt="Cerebras Logo" width={40} height={40} />
              <span>Cerebras</span>
            </div>
          </div>
            <p className="max-w-3xl mx-auto mb-6 text-xl font-medium text-gray-700">
              Leveraging state-of-the-art intelligence from Llama, deployed seamlessly with Docker, and built to scale for complex analytics with Cerebras architecture.
            </p>
        </div>
      </div>
    </section>
  );
};

export default Sponsors;