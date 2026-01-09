'use client';

import { useRef } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Square, DoorOpen, Bath, MoveRight, 
  PlayCircle, FolderOpen, Save, 
  ZoomIn, ZoomOut, Maximize, UploadCloud 
} from "lucide-react";

interface ToolbarProps {
  onAddRoom: () => void;
  onAddDoor: () => void;
  onAddFixture: () => void;
  onAddPath: () => void;
  onRunSimulation: () => void;
  onSave: () => void;
  onLoad: () => void;
  
  // NEW: Import Handler
  onImportPlan: (file: File) => void;
  isAnalyzing: boolean;

  canvasWidth: number;
  setCanvasWidth: (w: number) => void;
  canvasHeight: number;
  setCanvasHeight: (h: number) => void;

  scale: number;
  setScale: (s: number) => void;
}

export function Toolbar({ 
  onAddRoom, onAddDoor, onAddFixture, onAddPath, 
  onRunSimulation, onSave, onLoad, onImportPlan, isAnalyzing,
  canvasWidth, setCanvasWidth, canvasHeight, setCanvasHeight,
  scale, setScale
}: ToolbarProps) {
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleZoomIn = () => setScale(Math.min(3, scale + 0.1));
  const handleZoomOut = () => setScale(Math.max(0.5, scale - 0.1));
  const handleResetZoom = () => setScale(1);

  return (
    <div className="flex gap-4 p-4 bg-white border-b shadow-md z-10 items-center justify-between overflow-x-auto h-20">
      <div className="flex items-center gap-4">
        {/* 1. Creation Tools */}
        <div className="flex gap-2 border-r pr-4 mr-2">
          <Button variant="outline" className="h-10 px-4" onClick={onAddRoom} title="Add Room">
            <Square className="w-5 h-5 mr-2" /> <span className="hidden lg:inline text-sm font-medium">Room</span>
          </Button>
          <Button variant="outline" className="h-10 px-4" onClick={onAddDoor} title="Add Door">
            <DoorOpen className="w-5 h-5 mr-2" /> <span className="hidden lg:inline text-sm font-medium">Door</span>
          </Button>
          <Button variant="outline" className="h-10 px-4" onClick={onAddFixture} title="Add Fixture">
            <Bath className="w-5 h-5 mr-2" /> <span className="hidden lg:inline text-sm font-medium">Fixture</span>
          </Button>
          <Button variant="outline" className="h-10 px-4" onClick={onAddPath} title="Add Path">
            <MoveRight className="w-5 h-5 mr-2" /> <span className="hidden lg:inline text-sm font-medium">Path</span>
          </Button>
        </div>

        {/* 2. Zoom & View Controls */}
        <div className="flex gap-1 border-r pr-4 mr-2 items-center">
          <Button variant="ghost" size="icon" onClick={handleZoomOut}><ZoomOut className="w-5 h-5" /></Button>
          <span className="text-sm font-mono font-bold w-14 text-center">{Math.round(scale * 100)}%</span>
          <Button variant="ghost" size="icon" onClick={handleZoomIn}><ZoomIn className="w-5 h-5" /></Button>
          <Button variant="ghost" size="icon" onClick={handleResetZoom}><Maximize className="w-5 h-5" /></Button>
        </div>

        {/* 3. Canvas Resizer */}
        <div className="flex items-center gap-3 text-sm text-slate-600 bg-slate-100 p-2 rounded-md border hidden xl:flex">
          <span className="font-bold px-1">Stage (mm):</span>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold">W:</span>
            <Input type="number" className="h-8 w-20 text-sm px-2 bg-white" value={canvasWidth} onChange={(e) => setCanvasWidth(Number(e.target.value))} />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold">H:</span>
            <Input type="number" className="h-8 w-20 text-sm px-2 bg-white" value={canvasHeight} onChange={(e) => setCanvasHeight(Number(e.target.value))} />
          </div>
        </div>
      </div>

      {/* 4. AI & File Ops */}
      <div className="flex gap-3">
        {/* HIDDEN INPUT FOR UPLOAD */}
        <input 
          type="file" 
          ref={fileInputRef} 
          className="hidden" 
          accept="image/*"
          onChange={(e) => e.target.files?.[0] && onImportPlan(e.target.files[0])}
        />
        
        <Button 
          variant="secondary" 
          className="bg-purple-100 text-purple-700 hover:bg-purple-200 border-purple-200 h-10 px-4"
          onClick={() => fileInputRef.current?.click()}
          disabled={isAnalyzing}
        >
          {isAnalyzing ? (
            <span className="animate-pulse">Analyzing...</span>
          ) : (
            <>
              <UploadCloud className="w-5 h-5 mr-2" /> AI Import
            </>
          )}
        </Button>

        <Button variant="ghost" size="sm" onClick={onRunSimulation} className="text-blue-600 bg-blue-50 hover:bg-blue-100 h-10 px-4">
          <PlayCircle className="w-5 h-5 mr-2" /> Demo
        </Button>
        <Button variant="outline" size="sm" onClick={onLoad} className="h-10 px-4">
          <FolderOpen className="w-5 h-5 mr-2" /> Load
        </Button>
        <Button variant="outline" size="sm" onClick={onSave} className="border-green-600 text-green-600 hover:bg-green-50 h-10 px-4">
          <Save className="w-5 h-5 mr-2" /> Save
        </Button>
      </div>
    </div>
  );
}