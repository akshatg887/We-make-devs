// components/RadialBlobs.jsx

import React from 'react';
import './RadialBlobs.css'; // <-- Dedicated CSS for the blobs

const RadialBlobs = () => {
  return (
    <div className="radial-blobs-container">
      <div className="blob blob-1"></div>
      <div className="blob blob-2"></div>
      <div className="blob blob-3"></div>
      <div className="blob blob-4"></div>
      {/* Add more blobs if you want more complexity */}
    </div>
  );
};

export default RadialBlobs;