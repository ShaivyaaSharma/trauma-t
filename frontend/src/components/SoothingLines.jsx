import React from 'react';

const SoothingLines = ({ className = "", opacity = 0.15 }) => {
  return (
    <svg
      className={className}
      viewBox="0 0 1200 800"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{ opacity }}
    >
      {/* Organic flowing lines inspired by brain patterns */}
      <path
        d="M-100,200 Q150,150 300,200 T600,200 T900,200 T1200,200"
        stroke="currentColor"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M-100,280 Q100,250 250,280 T550,280 T850,280 T1150,280"
        stroke="currentColor"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M50,150 Q200,120 350,150 T650,150 T950,150 T1250,150"
        stroke="currentColor"
        strokeWidth="1.5"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M-50,350 Q180,320 380,350 T680,350 T980,350 T1280,350"
        stroke="currentColor"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M100,420 Q250,400 400,420 T700,420 T1000,420 T1300,420"
        stroke="currentColor"
        strokeWidth="1.5"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M-80,500 Q120,470 280,500 T580,500 T880,500 T1180,500"
        stroke="currentColor"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M150,580 Q300,560 450,580 T750,580 T1050,580 T1350,580"
        stroke="currentColor"
        strokeWidth="1.5"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M-120,650 Q80,620 240,650 T540,650 T840,650 T1140,650"
        stroke="currentColor"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
      />
      
      {/* Smaller organic curves */}
      <path
        d="M200,100 Q280,80 360,100 T520,100"
        stroke="currentColor"
        strokeWidth="1"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M600,250 Q680,230 760,250 T920,250"
        stroke="currentColor"
        strokeWidth="1"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M300,600 Q380,580 460,600 T620,600"
        stroke="currentColor"
        strokeWidth="1"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M800,450 Q880,430 960,450 T1120,450"
        stroke="currentColor"
        strokeWidth="1"
        fill="none"
        strokeLinecap="round"
      />
    </svg>
  );
};

export default SoothingLines;
