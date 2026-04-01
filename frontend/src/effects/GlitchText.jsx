/**
 * GlitchText — Glitch text animation component for headers and alerts.
 * Applies a cyberpunk-style glitch effect using CSS layers and clip-path.
 * Supports continuous, hover-only, and triggered glitch modes.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';

const KEYFRAMES_ID = 'nemesis-glitch-keyframes';

function ensureGlitchKeyframes() {
  if (typeof document === 'undefined') return;
  if (document.getElementById(KEYFRAMES_ID)) return;
  const style = document.createElement('style');
  style.id = KEYFRAMES_ID;
  style.textContent = `
    @keyframes glitchShift1 {
      0% { clip-path: inset(40% 0 61% 0); transform: translate(-2px, 0); }
      10% { clip-path: inset(8% 0 80% 0); transform: translate(2px, 0); }
      20% { clip-path: inset(80% 0 5% 0); transform: translate(-1px, 0); }
      30% { clip-path: inset(10% 0 85% 0); transform: translate(0px, 0); }
      40% { clip-path: inset(55% 0 35% 0); transform: translate(-2px, 0); }
      50% { clip-path: inset(25% 0 60% 0); transform: translate(1px, 0); }
      60% { clip-path: inset(75% 0 10% 0); transform: translate(2px, 0); }
      70% { clip-path: inset(50% 0 40% 0); transform: translate(-1px, 0); }
      80% { clip-path: inset(15% 0 70% 0); transform: translate(0px, 0); }
      90% { clip-path: inset(65% 0 20% 0); transform: translate(2px, 0); }
      100% { clip-path: inset(40% 0 61% 0); transform: translate(-2px, 0); }
    }
    @keyframes glitchShift2 {
      0% { clip-path: inset(25% 0 58% 0); transform: translate(2px, 0); }
      10% { clip-path: inset(78% 0 12% 0); transform: translate(-1px, 0); }
      20% { clip-path: inset(5% 0 88% 0); transform: translate(2px, 0); }
      30% { clip-path: inset(48% 0 42% 0); transform: translate(-2px, 0); }
      40% { clip-path: inset(70% 0 18% 0); transform: translate(1px, 0); }
      50% { clip-path: inset(15% 0 72% 0); transform: translate(-1px, 0); }
      60% { clip-path: inset(85% 0 5% 0); transform: translate(2px, 0); }
      70% { clip-path: inset(30% 0 55% 0); transform: translate(0px, 0); }
      80% { clip-path: inset(60% 0 28% 0); transform: translate(-2px, 0); }
      90% { clip-path: inset(10% 0 78% 0); transform: translate(1px, 0); }
      100% { clip-path: inset(25% 0 58% 0); transform: translate(2px, 0); }
    }
    @keyframes glitchFlash {
      0%, 90%, 100% { opacity: 0; }
      92% { opacity: 0.8; }
      94% { opacity: 0; }
      96% { opacity: 0.6; }
      98% { opacity: 0; }
    }
  `;
  document.head.appendChild(style);
}

/**
 * @param {Object} props
 * @param {React.ReactNode} props.children — Text content to glitch
 * @param {string} [props.as='span'] — Element tag to render (span, h1, h2, div, etc.)
 * @param {string} [props.className=''] — Additional CSS class
 * @param {Object} [props.style={}] — Additional inline styles
 * @param {'continuous'|'hover'|'interval'|'none'} [props.mode='interval'] — Glitch trigger mode
 * @param {number} [props.intervalMs=4000] — For 'interval' mode: ms between glitch bursts
 * @param {number} [props.durationMs=200] — Duration of each glitch burst in ms
 * @param {string} [props.glitchColor1='#00e5ff'] — First glitch layer color (cyan)
 * @param {string} [props.glitchColor2='#ff1744'] — Second glitch layer color (red)
 * @param {number} [props.intensity=1] — Glitch intensity multiplier (0.5-2)
 */
export default function GlitchText({
  children,
  as: Tag = 'span',
  className = '',
  style = {},
  mode = 'interval',
  intervalMs = 4000,
  durationMs = 200,
  glitchColor1 = '#00e5ff',
  glitchColor2 = '#ff1744',
  intensity = 1,
}) {
  const [isGlitching, setIsGlitching] = useState(mode === 'continuous');
  const [isHovered, setIsHovered] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    ensureGlitchKeyframes();
  }, []);

  // Interval mode: periodic glitch bursts
  useEffect(() => {
    if (mode !== 'interval') return;
    const trigger = () => {
      setIsGlitching(true);
      setTimeout(() => setIsGlitching(false), durationMs);
    };
    const id = setInterval(trigger, intervalMs + Math.random() * 1000);
    // Trigger once on mount after a small delay
    const initId = setTimeout(trigger, 500 + Math.random() * 2000);
    return () => {
      clearInterval(id);
      clearTimeout(initId);
    };
  }, [mode, intervalMs, durationMs]);

  const active = mode === 'continuous' || isGlitching || (mode === 'hover' && isHovered);

  const baseStyle = {
    position: 'relative',
    display: 'inline-block',
    ...style,
  };

  const layerBase = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    overflow: 'hidden',
    pointerEvents: 'none',
  };

  const scale = Math.max(0.5, Math.min(2, intensity));

  return (
    <Tag
      ref={containerRef}
      className={`glitch-text ${className}`}
      style={baseStyle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      data-text={typeof children === 'string' ? children : undefined}
    >
      {/* Base text */}
      {children}

      {/* Glitch layers — only rendered when active */}
      {active && (
        <>
          {/* Layer 1: Cyan shift */}
          <Tag
            aria-hidden="true"
            style={{
              ...layerBase,
              color: glitchColor1,
              textShadow: `${scale * 2}px 0 ${glitchColor1}`,
              animation: `glitchShift1 ${0.3 / scale}s steps(2, end) infinite`,
              opacity: 0.8,
            }}
          >
            {children}
          </Tag>

          {/* Layer 2: Red shift */}
          <Tag
            aria-hidden="true"
            style={{
              ...layerBase,
              color: glitchColor2,
              textShadow: `${scale * -2}px 0 ${glitchColor2}`,
              animation: `glitchShift2 ${0.25 / scale}s steps(3, end) infinite`,
              opacity: 0.8,
            }}
          >
            {children}
          </Tag>

          {/* Flash overlay */}
          <div
            aria-hidden="true"
            style={{
              ...layerBase,
              background: glitchColor1,
              animation: `glitchFlash ${0.5 / scale}s steps(1, end) infinite`,
              mixBlendMode: 'overlay',
            }}
          />
        </>
      )}
    </Tag>
  );
}
