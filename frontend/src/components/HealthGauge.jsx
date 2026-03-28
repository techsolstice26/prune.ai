import React, { useEffect, useState } from 'react';

const HealthGauge = ({ score, status }) => {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    // Smooth transition to the new score
    const target = score;
    let current = animatedScore;
    const step = target > current ? 0.02 : -0.02;

    const interval = setInterval(() => {
      if (Math.abs(target - current) < 0.02) {
        setAnimatedScore(target);
        clearInterval(interval);
      } else {
        current += step;
        setAnimatedScore(current);
      }
    }, 20);

    return () => clearInterval(interval);
  }, [score]);

  // SVG Gauge calculations
  const radius = 100;
  const circumference = 2 * Math.PI * radius;
  // We'll use 75% of the circle to look like a speedometer
  const arcLength = circumference * 0.75;
  const dashOffset = arcLength - (animatedScore * arcLength);

  const getStatusColor = () => {
    if (score >= 0.8) return 'var(--accent-red)';
    if (score >= 0.6) return 'var(--accent-orange)';
    return 'var(--accent-green)';
  };

  const getStatusText = () => {
    if (status === 'calculating') return 'Calculating...';
    if (score >= 0.8) return 'CRITICAL ANOMALY';
    if (score >= 0.6) return 'WARNING';
    return 'SYSTEM HEALTHY';
  };

  return (
    <div style={{ position: 'relative', width: '280px', height: '280px', margin: '0 auto' }}>
      <svg width="280" height="280" viewBox="0 0 240 240" style={{ transform: 'rotate(135deg)' }}>
        {/* Definitions for Glow/Gradients */}
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="var(--accent-cyan)" />
            <stop offset="100%" stopColor="var(--accent-blue)" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        {/* Background Track */}
        <circle
          cx="120"
          cy="120"
          r={radius}
          fill="transparent"
          stroke="var(--glass-border)"
          strokeWidth="16"
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeLinecap="round"
        />

        {/* Dynamic Foreground Track */}
        <circle
          cx="120"
          cy="120"
          r={radius}
          fill="transparent"
          stroke={getStatusColor()}
          strokeWidth="16"
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          filter="url(#glow)"
          style={{ transition: 'stroke-dashoffset 0.1s linear, stroke 0.5s ease' }}
        />
      </svg>

      {/* Center Content */}
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        textAlign: 'center',
        width: '100%'
      }}>
        {status === 'calculating' ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
             <div className="spinner" style={{ borderColor: 'rgba(255,255,255,0.1)', borderLeftColor: 'var(--accent-blue)' }}></div>
             <p style={{ fontSize: '0.875rem', color: 'var(--accent-cyan)', letterSpacing: '1px' }}>ANALYZING</p>
          </div>
        ) : (
          <>
            <h2 style={{ fontSize: '3rem', fontWeight: '700', margin: '0', lineHeight: '1', color: getStatusColor() }}>
              {(animatedScore * 100).toFixed(0)}<span style={{ fontSize: '1.25rem', color: 'var(--text-secondary)' }}>%</span>
            </h2>
            <p style={{ 
              fontSize: '0.75rem', 
              textTransform: 'uppercase', 
              letterSpacing: '1.5px',
              marginTop: '0.5rem',
              color: 'var(--text-secondary)' 
            }}>
              Suspicion Score
            </p>
          </>
        )}
      </div>

      {/* Bottom Status Badge */}
      <div style={{
        position: 'absolute',
        bottom: '10px',
        left: '50%',
        transform: 'translateX(-50%)',
        width: '100%',
        textAlign: 'center'
      }}>
         <span className={`badge ${score >= 0.8 ? 'badge-danger' : score >= 0.6 ? 'badge-warning' : 'badge-safe'}`}>
           {getStatusText()}
         </span>
      </div>
    </div>
  );
};

export default HealthGauge;
