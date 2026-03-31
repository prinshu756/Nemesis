/**
 * Scanlines — CRT scanline overlay effect.
 * Lightweight CSS-based overlay that gives the UI a military CRT monitor feel.
 * Supports adjustable opacity and optional animated scan beam.
 */

import React, { useState } from 'react';

const scanlineStyles = {
  container: {
    pointerEvents: 'none',
    position: 'fixed',
    inset: 0,
    zIndex: 9999,
  },
  scanlines: {
    position: 'absolute',
    inset: 0,
    background: `repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0, 0, 0, 0.03) 2px,
      rgba(0, 0, 0, 0.03) 4px
    )`,
  },
  scanBeam: {
    position: 'absolute',
    left: 0,
    right: 0,
    height: '2px',
    background: 'linear-gradient(90deg, transparent 0%, rgba(0, 229, 255, 0.07) 20%, rgba(0, 229, 255, 0.12) 50%, rgba(0, 229, 255, 0.07) 80%, transparent 100%)',
    boxShadow: '0 0 12px rgba(0, 229, 255, 0.06), 0 0 30px rgba(0, 229, 255, 0.03)',
    animation: 'scanBeamMove 8s linear infinite',
  },
  vignetteOverlay: {
    position: 'absolute',
    inset: 0,
    background: 'radial-gradient(ellipse at center, transparent 60%, rgba(0, 0, 0, 0.25) 100%)',
  },
};

// Inject keyframes for the scan beam animation
const KEYFRAMES_ID = 'nemesis-scanline-keyframes';
function ensureKeyframes() {
  if (typeof document === 'undefined') return;
  if (document.getElementById(KEYFRAMES_ID)) return;
  const style = document.createElement('style');
  style.id = KEYFRAMES_ID;
  style.textContent = `
    @keyframes scanBeamMove {
      0% { top: -2px; }
      100% { top: 100vh; }
    }
    @keyframes flickerOpacity {
      0%, 100% { opacity: 0.4; }
      50% { opacity: 0.35; }
      75% { opacity: 0.45; }
    }
  `;
  document.head.appendChild(style);
}

/**
 * @param {Object} props
 * @param {number} [props.opacity=0.4] — Scanline opacity (0-1)
 * @param {boolean} [props.showBeam=true] — Show the animated scan beam
 * @param {boolean} [props.showVignette=true] — Show corner vignette darkening
 * @param {boolean} [props.flicker=true] — Enable subtle opacity flicker
 */
export default function Scanlines({
  opacity = 0.4,
  showBeam = true,
  showVignette = true,
  flicker = true,
}) {
  React.useEffect(() => {
    ensureKeyframes();
  }, []);

  return (
    <div
      style={{
        ...scanlineStyles.container,
        opacity,
        animation: flicker ? 'flickerOpacity 4s ease-in-out infinite' : 'none',
      }}
      aria-hidden="true"
    >
      {/* Scanline bars */}
      <div style={scanlineStyles.scanlines} />

      {/* Animated scan beam */}
      {showBeam && <div style={scanlineStyles.scanBeam} />}

      {/* Corner vignette */}
      {showVignette && <div style={scanlineStyles.vignetteOverlay} />}
    </div>
  );
}
