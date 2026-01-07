import { useMemo } from 'react';

interface GaugeChartProps {
  value: number;
  min: number;
  max: number;
  label: string;
  unit: string;
  thresholds?: {
    warning: number;
    danger: number;
  };
  size?: 'sm' | 'md' | 'lg';
}

export const GaugeChart = ({
  value,
  min,
  max,
  label,
  unit,
  thresholds,
  size = 'md',
}: GaugeChartProps) => {
  const dimensions = {
    sm: { width: 100, height: 60, strokeWidth: 8, fontSize: 16, needleLength: 35 },
    md: { width: 140, height: 85, strokeWidth: 10, fontSize: 24, needleLength: 45 },
    lg: { width: 180, height: 110, strokeWidth: 12, fontSize: 32, needleLength: 60 },
  };

  const { width, height, strokeWidth, fontSize, needleLength } = dimensions[size];
  const centerX = width / 2;
  const centerY = height;
  const radius = width / 2 - strokeWidth;
  const circumference = Math.PI * radius;

  const percentage = useMemo(() => {
    const clamped = Math.max(min, Math.min(max, value));
    return ((clamped - min) / (max - min)) * 100;
  }, [value, min, max]);

  // Calculate needle angle: 0% = -90deg (left), 100% = 90deg (right)
  // This maps percentage 0-100 to angle -90 to 90 degrees
  const needleAngle = useMemo(() => {
    return -90 + (percentage * 180) / 100;
  }, [percentage]);

  // Calculate needle end point using trigonometry
  const needleEndX = useMemo(() => {
    const angleRad = (needleAngle * Math.PI) / 180;
    return centerX + needleLength * Math.sin(angleRad);
  }, [needleAngle, centerX, needleLength]);

  const needleEndY = useMemo(() => {
    const angleRad = (needleAngle * Math.PI) / 180;
    return centerY - needleLength * Math.cos(angleRad);
  }, [needleAngle, centerY, needleLength]);

  const getColor = () => {
    if (!thresholds) return 'rgb(59 130 246)'; // blue
    if (value >= thresholds.danger) return 'rgb(220 38 38)'; // red
    if (value >= thresholds.warning) return 'rgb(249 115 22)'; // orange
    return 'rgb(34 197 94)'; // green
  };

  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-2">
      <svg
        width={width}
        height={height + 20}
        viewBox={`0 0 ${width} ${height + 20}`}
        className="overflow-visible drop-shadow-lg"
        style={{ maxWidth: '100%', height: 'auto' }}
      >
        {/* Background arc */}
        <path
          d={`M ${strokeWidth} ${height} A ${radius} ${radius} 0 0 1 ${width - strokeWidth} ${height}`}
          fill="none"
          stroke="hsl(220 15% 25%)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Danger zone indicator */}
        {thresholds && (
          <>
            <path
              d={`M ${strokeWidth} ${height} A ${radius} ${radius} 0 0 1 ${width - strokeWidth} ${height}`}
              fill="none"
              stroke="rgb(220 38 38 / 0.3)"
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              strokeDasharray={`${circumference * 0.15} ${circumference}`}
              strokeDashoffset={-circumference * 0.85}
            />
            <path
              d={`M ${strokeWidth} ${height} A ${radius} ${radius} 0 0 1 ${width - strokeWidth} ${height}`}
              fill="none"
              stroke="rgb(249 115 22 / 0.3)"
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              strokeDasharray={`${circumference * 0.2} ${circumference}`}
              strokeDashoffset={-circumference * 0.65}
            />
          </>
        )}

        {/* Value arc */}
        <path
          d={`M ${strokeWidth} ${height} A ${radius} ${radius} 0 0 1 ${width - strokeWidth} ${height}`}
          fill="none"
          stroke={getColor()}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{
            transition: 'stroke-dashoffset 0.5s ease-out, stroke 0.3s ease',
            filter: `drop-shadow(0 0 6px ${getColor()})`,
          }}
        />

        {/* Needle - using calculated coordinates for accuracy */}
        <line
          x1={centerX}
          y1={centerY}
          x2={needleEndX}
          y2={needleEndY}
          stroke="rgb(240 246 252)"
          strokeWidth="3"
          strokeLinecap="round"
          style={{
            transition: 'x2 0.5s ease-out, y2 0.5s ease-out',
          }}
        />
        
        {/* Needle center pivot */}
        <circle 
          cx={centerX} 
          cy={centerY} 
          r="5" 
          fill="rgb(240 246 252)" 
        />

        {/* Value text */}
        <text
          x={centerX}
          y={height + 18}
          textAnchor="middle"
          dominantBaseline="middle"
          fill="rgb(240 246 252)"
          fontWeight="bold"
          fontSize={fontSize}
          fontFamily="Space Grotesk, sans-serif"
        >
          {typeof value === 'number' ? value.toLocaleString(undefined, { maximumFractionDigits: 1 }) : value}
        </text>
      </svg>
      {unit && (
        <div className="text-xs text-muted-foreground mt-1">{unit}</div>
      )}
    </div>
  );
};
