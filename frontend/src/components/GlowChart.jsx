import React, { useRef, useEffect } from 'react';

export default function GlowChart({ data = [], maxBars = 16, height = 180, label = '', color = 'cyan' }) {
  const canvasRef = useRef(null);
  const dataRef = useRef(data);
  dataRef.current = data;

  const colors = {
    cyan: { fill: 'rgba(0, 229, 255, 0.6)', stroke: '#00e5ff', glow: 'rgba(0, 229, 255, 0.3)' },
    red: { fill: 'rgba(255, 23, 68, 0.6)', stroke: '#ff1744', glow: 'rgba(255, 23, 68, 0.3)' },
    amber: { fill: 'rgba(255, 171, 0, 0.6)', stroke: '#ffab00', glow: 'rgba(255, 171, 0, 0.3)' },
    green: { fill: 'rgba(0, 230, 118, 0.6)', stroke: '#00e676', glow: 'rgba(0, 230, 118, 0.3)' },
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const resize = () => {
      const rect = canvas.parentElement.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = height;
    };
    resize();

    let animFrame;
    const draw = () => {
      const w = canvas.width;
      const h = canvas.height;
      const d = dataRef.current;
      const c = colors[color] || colors.cyan;

      ctx.clearRect(0, 0, w, h);

      // Grid lines
      ctx.strokeStyle = 'rgba(0, 229, 255, 0.05)';
      ctx.lineWidth = 0.5;
      for (let i = 0; i < 5; i++) {
        const y = (h / 5) * i;
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
      }

      if (!d || d.length === 0) {
        animFrame = requestAnimationFrame(draw);
        return;
      }

      const barCount = Math.min(d.length, maxBars);
      const gap = 4;
      const barWidth = Math.max(4, (w - gap * (barCount + 1)) / barCount);
      const maxVal = Math.max(...d, 1);

      d.slice(-barCount).forEach((val, i) => {
        const barH = (val / maxVal) * (h - 20);
        const x = gap + i * (barWidth + gap);
        const y = h - barH - 10;

        // Glow
        ctx.shadowColor = c.glow;
        ctx.shadowBlur = 8;

        // Bar
        const grad = ctx.createLinearGradient(x, y, x, h - 10);
        grad.addColorStop(0, c.fill);
        grad.addColorStop(1, c.fill.replace('0.6', '0.2'));
        ctx.fillStyle = grad;
        ctx.fillRect(x, y, barWidth, barH);

        // Top line
        ctx.strokeStyle = c.stroke;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + barWidth, y);
        ctx.stroke();

        ctx.shadowBlur = 0;
      });

      animFrame = requestAnimationFrame(draw);
    };

    draw();
    window.addEventListener('resize', resize);
    return () => {
      window.removeEventListener('resize', resize);
      if (animFrame) cancelAnimationFrame(animFrame);
    };
  }, [data, height, color, maxBars]);

  return (
    <div className="glow-chart">
      {label && <div className="glow-chart-label">{label}</div>}
      <canvas ref={canvasRef} style={{ width: '100%', height: `${height}px` }} />
    </div>
  );
}
