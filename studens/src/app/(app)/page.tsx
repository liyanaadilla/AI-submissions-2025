'use client';

import React, { useState, useEffect } from 'react';
import FloorplanCanvas from '@/components/canvas/FloorplanCanvas';
import { InspectorSidebar } from '@/components/canvas/InspectorSidebar';
import { Toolbar } from '@/components/canvas/Toolbar';
import { ComplianceReport } from '@/components/canvas/ComplianceReport';
import { Room, Door, Fixture, Path } from '@/lib/ai-agent/types';
import { runRTCCC } from '@/lib/ai-agent/inference-engine';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function RTCCCApp() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [doors, setDoors] = useState<Door[]>([]);
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [paths, setPaths] = useState<Path[]>([]);
  
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [allViolations, setAllViolations] = useState<any[]>([]);
  
  const [isLoadSheetOpen, setIsLoadSheetOpen] = useState(false);
  const [savedProjects, setSavedProjects] = useState<any[]>([]);

  // AI Loading State
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Default: 10m x 8m
  const [canvasWidth, setCanvasWidth] = useState<number>(10000); 
  const [canvasHeight, setCanvasHeight] = useState<number>(8000);
  const [scale, setScale] = useState<number>(1);

  useEffect(() => {
    const currentData = { rooms, doors, fixtures, paths };
    const results = runRTCCC(currentData);
    setAllViolations(results);
  }, [rooms, doors, fixtures, paths]);

  // --- ACTIONS ---
  const addRoom = () => {
    const newRoom: Room = { id: `room-${Date.now()}`, type: 'room', roomType: 'Habitable', x: 1000, y: 1000, width: 3000, height: 3000, area: 9, ceilingHeight: 2500 };
    setRooms([...rooms, newRoom]);
  };
  const addDoor = () => {
    const newDoor: Door = { id: `door-${Date.now()}`, type: 'door', x: 3500, y: 1500, width: 915, height: 40, rotation: 0, isRequiredExit: true, swingDirection: 'LH' };
    setDoors([...doors, newDoor]);
  };
  const addFixture = () => {
    const newFixture: Fixture = { id: `fix-${Date.now()}`, type: 'fixture', name: 'Sink', x: 1500, y: 1500, width: 500, height: 500, isAccessible: true, clearanceWidth: 800, clearanceDepth: 1200 };
    setFixtures([...fixtures, newFixture]);
  };
  const addPath = () => {
    const newPath: Path = { id: `path-${Date.now()}`, type: 'path', x: 500, y: 4000, width: 5000, height: 1200, pathWidth: 1200 };
    setPaths([...paths, newPath]);
  };

  const deleteObject = (id: string, type: string) => {
    if (type === 'room') setRooms(rooms.filter(r => r.id !== id));
    if (type === 'door') setDoors(doors.filter(d => d.id !== id));
    if (type === 'fixture') setFixtures(fixtures.filter(f => f.id !== id));
    if (type === 'path') setPaths(paths.filter(p => p.id !== id));
    setSelectedId(null);
  };

  const handleUpdate = (updatedObj: any) => {
    if (updatedObj.type === 'room') setRooms(rooms.map(r => r.id === updatedObj.id ? updatedObj : r));
    if (updatedObj.type === 'door') setDoors(doors.map(d => d.id === updatedObj.id ? updatedObj : d));
    if (updatedObj.type === 'fixture') setFixtures(fixtures.map(f => f.id === updatedObj.id ? updatedObj : f));
    if (updatedObj.type === 'path') setPaths(paths.map(p => p.id === updatedObj.id ? updatedObj : p));
  };

  const loadDemoScenario = () => {
    setRooms([{ id: 'demo-room-1', type: 'room', roomType: 'Office', x: 500, y: 500, width: 3000, height: 3000, area: 9, ceilingHeight: 2400 }]);
    setDoors([{ id: 'demo-door-1', type: 'door', x: 3600, y: 2000, width: 915, height: 40, rotation: 0, isRequiredExit: true, swingDirection: 'LH' }]);
    setFixtures([]); setPaths([]);
  };

  // --- NEW: AI IMPORT HANDLER ---
  const handleImportPlan = async (file: File) => {
    setIsAnalyzing(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/analyze-plan', { method: 'POST', body: formData });
      if (!res.ok) throw new Error("AI Analysis Failed");
      
      const data = await res.json();
      
      // 1. Resize Stage
      if (data.width && data.height) {
        setCanvasWidth(data.width);
        setCanvasHeight(data.height);
      }

      // 2. Populate Objects
      setRooms(data.rooms || []);
      setDoors(data.doors || []);
      setFixtures(data.fixtures || []);
      setPaths(data.paths || []);

      alert("✅ AI Analysis Complete! Plan replicated.");
    } catch (e: any) {
      alert(`❌ Error: ${e.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // --- API Handlers ---
  const saveToPayload = async () => {
    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: `Design ${new Date().toLocaleString()}`,
          floorplanData: { rooms, doors, fixtures, paths },
          status: allViolations.length > 0 ? 'non-compliant' : 'compliant',
        }),
      });
      if (response.ok) alert("✅ Design saved!");
      else { const e = await response.json(); alert(`❌ Error: ${e.message}`); }
    } catch (e: any) { alert(`❌ Network Error: ${e.message}`); }
  };

  const fetchProjects = async () => {
    try {
      const res = await fetch('/api/projects');
      if (!res.ok) throw new Error("API not found");
      const data = await res.json();
      if (data.docs) { setSavedProjects(data.docs); setIsLoadSheetOpen(true); }
    } catch (e: any) { alert(`❌ Load Error: ${e.message}`); }
  };

  const loadProject = (project: any) => {
    if (project.floorplanData) {
      setRooms(project.floorplanData.rooms || []);
      setDoors(project.floorplanData.doors || []);
      setFixtures(project.floorplanData.fixtures || []);
      setPaths(project.floorplanData.paths || []);
      setIsLoadSheetOpen(false); 
    }
  };

  const selectedObject = rooms.find(r => r.id === selectedId) || doors.find(d => d.id === selectedId) || fixtures.find(f => f.id === selectedId) || paths.find(p => p.id === selectedId) || null;

  return (
    <main className="flex h-screen w-full bg-slate-50 overflow-hidden font-sans">
      <div className="flex-1 flex flex-col relative">
        <header className="p-4 border-b bg-white flex justify-between items-center shadow-sm">
          <div>
            <h1 className="text-xl font-bold text-slate-800">RTCCC System</h1>
            <p className="text-xs text-slate-500 font-medium tracking-tight">Real-Time Code Compliance Checker</p>
          </div>
          <div className="flex gap-2">
            <div className={`text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-widest border ${
              allViolations.length > 0 ? "bg-red-50 text-red-600 border-red-200" : "bg-green-50 text-green-600 border-green-200"
            }`}>
              {allViolations.length > 0 ? `${allViolations.length} Violations` : "Compliant"}
            </div>
          </div>
        </header>

        <Toolbar 
          onAddRoom={addRoom} onAddDoor={addDoor} onAddFixture={addFixture} onAddPath={addPath} 
          onRunSimulation={loadDemoScenario} onSave={saveToPayload} onLoad={fetchProjects} 
          
          // NEW PROPS
          onImportPlan={handleImportPlan}
          isAnalyzing={isAnalyzing}

          canvasWidth={canvasWidth} setCanvasWidth={setCanvasWidth} canvasHeight={canvasHeight} setCanvasHeight={setCanvasHeight}
          scale={scale} setScale={setScale}
        />
        
        <div className="flex-1 relative flex flex-col overflow-hidden">
          <div className="flex-1 bg-slate-200 relative overflow-hidden">
            <FloorplanCanvas 
              rooms={rooms} setRooms={setRooms} 
              doors={doors} setDoors={setDoors} 
              fixtures={fixtures} setFixtures={setFixtures} 
              paths={paths} setPaths={setPaths} 
              setSelectedId={setSelectedId} selectedId={selectedId}
              projectWidth={canvasWidth} projectHeight={canvasHeight} scale={scale}
            />
          </div>
          <ComplianceReport violations={allViolations} />
        </div>
      </div>

      <InspectorSidebar selectedObject={selectedObject} onUpdate={handleUpdate} onDelete={deleteObject} />

      <Sheet open={isLoadSheetOpen} onOpenChange={setIsLoadSheetOpen}>
        <SheetContent side="left">
          <SheetHeader><SheetTitle>Saved Designs</SheetTitle><SheetDescription>Select a past project.</SheetDescription></SheetHeader>
          <div className="mt-4 space-y-3 overflow-y-auto max-h-[80vh]">
            {savedProjects.map((proj: any) => (
              <Card key={proj.id} className="p-3 cursor-pointer hover:bg-slate-50 transition-colors" onClick={() => loadProject(proj)}>
                <span className="font-bold text-sm truncate">{proj.title}</span>
                <div className="text-xs text-slate-400">{new Date(proj.createdAt).toLocaleDateString()}</div>
              </Card>
            ))}
          </div>
        </SheetContent>
      </Sheet>
    </main>
  );
}