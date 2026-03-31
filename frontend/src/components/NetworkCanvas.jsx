import React, { useRef, useEffect, useCallback } from 'react';

const STATUS_COLORS = {
  online: '#00e5ff',
  suspicious: '#ffab00',
  isolated: '#ff1744',
  offline: '#556677',
};

const RISK_COLORS = {
  low: '#00e676',
  medium: '#ffab00',
  high: '#ff5252',
  critical: '#ff1744',
};

const TYPE_SHAPES = {
  Router: 'diamond',
  Switch: 'diamond',
  Firewall: 'diamond',
  'Access Point': 'diamond',
  Server: 'square',
  Workstation: 'square',
  Laptop: 'square',
  default: 'circle',
};

export default function NetworkCanvas({ devices = [], connections = [], onNodeClick }) {
  const canvasRef = useRef(null);
  const animFrameRef = useRef(null);
  const particlesRef = useRef([]);
  const mouseRef = useRef({ x: 0, y: 0 });
  const hoveredRef = useRef(null);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);

    // Background grid
    ctx.strokeStyle = 'rgba(0, 229, 255, 0.03)';
    ctx.lineWidth = 0.5;
    const gridSize = 40;
    for (let x = 0; x < w; x += gridSize) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = 0; y < h; y += gridSize) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }

    // Build device position map
    const posMap = {};
    devices.forEach(d => {
      posMap[d.mac] = {
        x: (d.x || d.coordinates?.x || Math.random()) * w,
        y: (d.y || d.coordinates?.y || Math.random()) * h,
        ...d,
      };
    });

    // Draw connections
    connections.forEach(conn => {
      const src = posMap[conn.source];
      const tgt = posMap[conn.target];
      if (!src || !tgt) return;

      const blocked = conn.status === 'blocked';
      ctx.beginPath();
      ctx.moveTo(src.x, src.y);
      ctx.lineTo(tgt.x, tgt.y);
      ctx.strokeStyle = blocked ? 'rgba(255, 23, 68, 0.15)' : 'rgba(0, 229, 255, 0.08)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Data flow particle
      if (!blocked && Math.random() < 0.02) {
        particlesRef.current.push({
          sx: src.x, sy: src.y,
          tx: tgt.x, ty: tgt.y,
          t: 0, speed: 0.005 + Math.random() * 0.01,
          color: 'rgba(0, 229, 255, 0.6)',
        });
      }
    });

    // Update & draw particles
    particlesRef.current = particlesRef.current.filter(p => {
      p.t += p.speed;
      if (p.t > 1) return false;
      const px = p.sx + (p.tx - p.sx) * p.t;
      const py = p.sy + (p.ty - p.sy) * p.t;
      ctx.beginPath();
      ctx.arc(px, py, 2, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.fill();
      return true;
    });

    // Draw device nodes
    const now = Date.now();
    let newHovered = null;
    devices.forEach(d => {
      const pos = posMap[d.mac];
      if (!pos) return;
      const { x, y } = pos;
      const color = STATUS_COLORS[d.status] || STATUS_COLORS.online;
      const riskColor = RISK_COLORS[d.risk_level] || RISK_COLORS.low;
      const shape = TYPE_SHAPES[d.type || d.device_type] || TYPE_SHAPES.default;

      // Check hover
      const dist = Math.sqrt((mouseRef.current.x - x) ** 2 + (mouseRef.current.y - y) ** 2);
      const isHovered = dist < 18;
      if (isHovered) newHovered = d;

      const radius = isHovered ? 10 : 7;
      const pulse = Math.sin(now / 600 + x) * 0.3 + 0.7;

      // Outer glow
      const grad = ctx.createRadialGradient(x, y, 0, x, y, radius * 3);
      grad.addColorStop(0, color.replace(')', `, ${0.15 * pulse})`).replace('rgb', 'rgba'));
      grad.addColorStop(1, 'transparent');
      ctx.beginPath();
      ctx.arc(x, y, radius * 3, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.fill();

      // Node shape
      ctx.beginPath();
      if (shape === 'diamond') {
        ctx.moveTo(x, y - radius); ctx.lineTo(x + radius, y);
        ctx.lineTo(x, y + radius); ctx.lineTo(x - radius, y); ctx.closePath();
      } else if (shape === 'square') {
        const s = radius * 0.75;
        ctx.rect(x - s, y - s, s * 2, s * 2);
      } else {
        ctx.arc(x, y, radius, 0, Math.PI * 2);
      }
      ctx.fillStyle = d.status === 'isolated' ? 'rgba(255,23,68,0.3)' : `rgba(0,229,255,${0.15 * pulse})`;
      ctx.fill();
      ctx.strokeStyle = color;
      ctx.lineWidth = isHovered ? 2 : 1.2;
      ctx.stroke();

      // Isolation ring
      if (d.isolation !== 'normal' && d.isolation) {
        ctx.beginPath();
        ctx.arc(x, y, radius + 5, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(255, 23, 68, 0.4)';
        ctx.lineWidth = 1;
        ctx.setLineDash([3, 3]);
        ctx.stroke();
        ctx.setLineDash([]);
      }

      // Label
      if (isHovered || devices.length < 25) {
        ctx.font = '10px "Share Tech Mono", monospace';
        ctx.fillStyle = isHovered ? '#fff' : 'rgba(224, 230, 237, 0.7)';
        ctx.textAlign = 'center';
        const label = d.hostname || d.ip || d.mac;
        ctx.fillText(label.length > 18 ? label.substring(0, 18) : label, x, y - radius - 6);

        if (isHovered) {
          ctx.fillStyle = riskColor;
          ctx.font = '9px "Share Tech Mono", monospace';
          ctx.fillText(`${d.ip || ''} | ${d.type || d.device_type || ''}`, x, y + radius + 14);
          ctx.fillText(`RISK: ${d.risk_level?.toUpperCase() || 'N/A'} | ${d.status?.toUpperCase() || ''}`, x, y + radius + 26);
        }
      }
    });

    hoveredRef.current = newHovered;
    animFrameRef.current = requestAnimationFrame(draw);
  }, [devices, connections]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const resize = () => {
      const rect = canvas.parentElement.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
    };
    resize();
    window.addEventListener('resize', resize);

    const onMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      mouseRef.current = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    };
    const onClick = () => {
      if (hoveredRef.current && onNodeClick) onNodeClick(hoveredRef.current);
    };
    canvas.addEventListener('mousemove', onMove);
    canvas.addEventListener('click', onClick);

    animFrameRef.current = requestAnimationFrame(draw);

    return () => {
      window.removeEventListener('resize', resize);
      canvas.removeEventListener('mousemove', onMove);
      canvas.removeEventListener('click', onClick);
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [draw]);

  return <canvas ref={canvasRef} className="network-canvas" id="tactical-map-canvas" />;
}
