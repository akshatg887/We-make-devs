// src/components/External/Blob.jsx
'use client'
import React, { useState, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';

// A soft, continuous animation for the blob
const moveBlob = keyframes`
  0% {
    transform: scale(1) translate(10px, -20px);
  }
  50% {
    transform: scale(2) translate(-30px, 25px);
  }
  100% {
    transform: scale(2.5) translate(10px, -20px);
  }
`;

const BlobWrapper = styled.div`
  position: absolute;
  z-index: 0; // Ensures it's in the background
  width: 350px;
  height: 350px;
  border-radius: 50%;
  
  // The radial gradient creates the soft blob effect
  background: radial-gradient(circle at center, ${({ color }) => color} 0%, rgba(0,0,0,0) 70%);
  
  filter: blur(80px); // This is key for the soft, ethereal look
  opacity: 0.3;
  
  // Apply random position and animation
  top: ${({ top }) => top};
  left: ${({ left }) => left};
  animation: ${moveBlob} 15s ease-in-out forwards;
  transition: all 1s ease-in-out;
`;

const Blob = ({ color = '#8A2BE2' }) => { // Default color is a nice purple
  const [position, setPosition] = useState({ top: '-50%', left: '-50%' });

  // Set a random position once the component mounts
  useEffect(() => {
    const top = `${Math.random() * 100}%`;
    const left = `${Math.random() * 100}%`;
    setPosition({ top, left });
  }, []);

  return <BlobWrapper color={color} top={position.top} left={position.left} />;
};

export default Blob;