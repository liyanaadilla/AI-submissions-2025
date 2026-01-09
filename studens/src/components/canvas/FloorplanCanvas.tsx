'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Stage, Layer, Rect, Text, Group, Arc, Arrow } from 'react-konva';
import { KonvaEventObject } from 'konva/lib/Node';
import { runRTCCC } from '@/lib/ai-agent/inference-engine';
import { Room, Door, Fixture, Path } from '@/lib/ai-agent/types';

interface FloorplanCanvasProps {
  rooms: Room[]; setRooms: React.Dispatch<React.SetStateAction<Room[]>>;
  doors: Door[]; setDoors: React.Dispatch<React.SetStateAction<Door[]>>;
  fixtures: Fixture[]; setFixtures: React.Dispatch<React.SetStateAction<Fixture[]>>;
  paths: Path[]; setPaths: React.Dispatch<React.SetStateAction<Path[]>>;
  selectedId: string | null; setSelectedId: React.Dispatch<React.SetStateAction<string | null>>;
  projectWidth: number; projectHeight: number; scale: number;
}

export default function FloorplanCanvas({ 
  rooms, setRooms, doors, setDoors, fixtures, setFixtures, paths, setPaths, 
  selectedId, setSelectedId, projectWidth, projectHeight, scale 
}: FloorplanCanvasProps) {
  
  const [stageSize, setStageSize] = useState({ width: 0, height: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const updateSize = () => {
      if (containerRef.current) {
        setStageSize({ width: containerRef.current.offsetWidth, height: containerRef.current.offsetHeight });
      }
    };
    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, []);

  const [violations, setViolations] = useState<any[]>([]);
  
  // 1 Meter = 50 Pixels
  const PX_PER_MM = 0.05; 

  useEffect(() => {
    const currentData = { rooms, doors, fixtures, paths };
    const foundViolations = runRTCCC(currentData);
    setViolations(foundViolations);
  }, [rooms, doors, fixtures, paths]);

  // FIX: Convert Pixel Drag Position back to Millimeters for State
  const handleDrag = (id: string, type: string, e: KonvaEventObject<DragEvent>) => {
    const newX_MM = e.target.x() / PX_PER_MM;
    const newY_MM = e.target.y() / PX_PER_MM;

    if (type === 'room') setRooms(prev => prev.map(r => r.id === id ? { ...r, x: newX_MM, y: newY_MM } : r));
    if (type === 'door') setDoors(prev => prev.map(d => d.id === id ? { ...d, x: newX_MM, y: newY_MM } : d));
    if (type === 'fixture') setFixtures(prev => prev.map(f => f.id === id ? { ...f, x: newX_MM, y: newY_MM } : f));
    if (type === 'path') setPaths(prev => prev.map(p => p.id === id ? { ...p, x: newX_MM, y: newY_MM } : p));
  };

  if (stageSize.width === 0) return <div ref={containerRef} className="w-full h-full bg-slate-200" />;

  const paperWidth = projectWidth * PX_PER_MM;
  const paperHeight = projectHeight * PX_PER_MM;

  return (
    <div ref={containerRef} className="w-full h-full bg-slate-300 overflow-hidden relative">
      <Stage width={stageSize.width} height={stageSize.height} scaleX={scale} scaleY={scale} draggable>
        <Layer>
          {/* PAPER BACKGROUND */}
          <Group>
             <Rect width={paperWidth} height={paperHeight} fill="white" shadowBlur={20} shadowOpacity={0.2} />
             {/* Optional Grid Lines could go here */}
          </Group>

          {/* DIMENSION INDICATORS (Restored) */}
          <Group name="dimensions">
            {/* Top Width Ruler */}
            <Arrow 
                points={[0, -20, paperWidth, -20]} 
                pointerLength={10} pointerWidth={10} 
                fill="#64748b" stroke="#64748b" strokeWidth={2} 
                pointerAtBeginning 
            />
            <Text 
                x={paperWidth / 2 - 50} y={-40} 
                text={`${projectWidth} mm`} 
                fontSize={14} fill="#475569" fontStyle="bold"
            />
            
            {/* Left Height Ruler */}
            <Arrow 
                points={[-20, 0, -20, paperHeight]} 
                pointerLength={10} pointerWidth={10} 
                fill="#64748b" stroke="#64748b" strokeWidth={2} 
                pointerAtBeginning 
            />
            <Text 
                x={-40} y={paperHeight / 2} 
                text={`${projectHeight} mm`} 
                fontSize={14} fill="#475569" fontStyle="bold" rotation={-90}
            />
          </Group>

          {/* ROOMS */}
          {rooms.map((room) => {
            const isViolating = violations.some(v => v.id === room.id);
            return (
              <Group 
                key={room.id} 
                x={room.x * PX_PER_MM} // FIX: Convert MM to Pixels
                y={room.y * PX_PER_MM} 
                draggable
                onDragEnd={(e) => handleDrag(room.id, 'room', e)} 
                onClick={() => setSelectedId(room.id)}
              >
                <Rect
                  width={room.width * PX_PER_MM} 
                  height={room.height * PX_PER_MM}
                  fill={isViolating ? "rgba(239, 68, 68, 0.1)" : selectedId === room.id ? "#f0f9ff" : "#f8fafc"}
                  stroke={isViolating ? "#ef4444" : selectedId === room.id ? "#0ea5e9" : "#cbd5e1"} strokeWidth={2}
                />
                <Text x={5} y={5} text={`${room.roomType}\n${room.area}m²`} fontSize={11} fill="#64748b" />
              </Group>
            );
          })}

          {/* PATHS */}
          {paths.map((path) => (
            <Group 
              key={path.id} 
              x={path.x * PX_PER_MM} 
              y={path.y * PX_PER_MM} 
              draggable
              onDragEnd={(e) => handleDrag(path.id, 'path', e)} 
              onClick={() => setSelectedId(path.id)}
            >
              <Rect
                width={path.width * PX_PER_MM} 
                height={path.height * PX_PER_MM}
                fill="rgba(59, 130, 246, 0.1)" stroke="#3b82f6" dash={[5, 5]}
              />
              <Text x={5} y={5} text="Egress" fontSize={10} fill="#3b82f6" />
            </Group>
          ))}

          {/* DOORS */}
          {doors.map((door) => {
            const isViolating = violations.some(v => v.id === door.id);
            const doorW = door.width * PX_PER_MM; 
            
            return (
              <Group 
                key={door.id} 
                x={door.x * PX_PER_MM} 
                y={door.y * PX_PER_MM}
                rotation={door.rotation || 0}
                draggable
                onDragEnd={(e) => handleDrag(door.id, 'door', e)} 
                onClick={() => setSelectedId(door.id)}
              >
                <Rect width={doorW} height={4} fill={isViolating ? "#ef4444" : "#1e293b"} stroke={selectedId === door.id ? "#0ea5e9" : "none"} />
                <Arc
                  x={door.swingDirection === 'LH' ? 0 : doorW} y={0}
                  innerRadius={doorW} outerRadius={doorW} angle={90}
                  rotation={door.swingDirection === 'LH' ? 0 : 90}
                  stroke={isViolating ? "#ef4444" : "#94a3b8"} dash={[4, 4]}
                />
                <Text x={0} y={-15} text={`${door.width}mm`} fontSize={10} fill="#64748b"/>
              </Group>
            );
          })}

          {/* FIXTURES */}
          {fixtures.map((fixture) => {
            const isViolating = violations.some(v => v.id === fixture.id);
            const w = fixture.width * PX_PER_MM;
            const h = fixture.height * PX_PER_MM;
            const clW = fixture.clearanceWidth * PX_PER_MM;
            const clD = fixture.clearanceDepth * PX_PER_MM;

            return (
              <Group 
                key={fixture.id} 
                x={fixture.x * PX_PER_MM} 
                y={fixture.y * PX_PER_MM} 
                draggable
                onDragEnd={(e) => handleDrag(fixture.id, 'fixture', e)} 
                onClick={() => setSelectedId(fixture.id)}
              >
                <Rect x={-(clW - w)/2} y={-(clD - h)/2} width={clW} height={clD}
                  fill={isViolating ? "rgba(239, 68, 68, 0.1)" : "rgba(34, 197, 94, 0.05)"}
                  stroke={isViolating ? "#ef4444" : "#22c55e"} dash={[2, 2]}
                />
                <Rect width={w} height={h} fill="#64748b" cornerRadius={2} />
                <Text x={0} y={h + 5} text={fixture.name} fontSize={10} />
              </Group>
            );
          })}
        </Layer>
      </Stage>
    </div>
  );
}