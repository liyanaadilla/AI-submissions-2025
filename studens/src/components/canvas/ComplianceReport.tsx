'use client';

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, CheckCircle2 } from "lucide-react";

interface ComplianceReportProps {
  violations: any[];
}

export function ComplianceReport({ violations }: ComplianceReportProps) {
  return (
    <div className="flex flex-col gap-3 p-4 bg-white border-t h-64 overflow-y-auto shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)]">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-bold flex items-center gap-2">
          Agent Reasoning Log
          <Badge variant={violations.length > 0 ? "destructive" : "outline"}>
            {violations.length} Issues Found
          </Badge>
        </h3>
        {violations.length === 0 && (
          <div className="text-green-600 flex items-center gap-1 text-sm font-medium">
            <CheckCircle2 className="w-4 h-4" /> Environment Compliant
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {violations.map((v, i) => {
          // 1. Determine Object Name for Title (Clean "door_01" to "Door")
          let objectName = "Object";
          const rawId = v.details?.elementId || v.elementId || "";
          
          if (rawId) {
             const parts = rawId.split(/[_-]/); // Split by _ or - to remove numbers
             if (parts.length > 0) {
                 objectName = parts[0].charAt(0).toUpperCase() + parts[0].slice(1);
             }
          } else {
             // Fallback: Infer object from message if ID is missing
             const msgLower = v.message.toLowerCase();
             if (msgLower.includes("door")) objectName = "Door";
             else if (msgLower.includes("room")) objectName = "Room";
             else if (msgLower.includes("ceiling")) objectName = "Ceiling";
             else if (msgLower.includes("sink") || msgLower.includes("toilet") || msgLower.includes("fixture")) objectName = "Fixture";
             else if (msgLower.includes("path") || msgLower.includes("egress")) objectName = "Path";
          }

          // 2. Determine KR Prefix for Description
          let krPrefix = "";
          const vid = v.id || "";
          const vmsg = v.message.toLowerCase();

          // KR 1: Door Width
          if (vid.includes("egress_width") || vmsg.includes("door width")) {
             krPrefix = "KR 1 Violation";
          }
          // KR 2: Room Area
          else if (vid.includes("room_area") || vmsg.includes("minimum area") || vmsg.includes("sqm")) {
             krPrefix = "KR 2 Violation";
          }
          // KR 3: Accessibility (Clear Space)
          else if (vid.includes("clear_space") || vmsg.includes("clearance") || vmsg.includes("overlap")) {
             krPrefix = "KR 3 Violation";
          }
          // KR 4: Ceiling Height
          else if (vid.includes("ceiling_height") || vmsg.includes("ceiling")) {
             krPrefix = "KR 4 Violation";
          }
          // KR 5: Path Obstruction
          else if (vid.includes("egress_path") || vmsg.includes("path") || vmsg.includes("obstruct")) {
             krPrefix = "KR 5 Violation";
          }

          // Avoid double labeling if the message already starts with "KR"
          const descriptionText = v.message.startsWith("KR") 
            ? v.message 
            : (krPrefix ? `${krPrefix}: ${v.message}` : v.message);

          return (
            <Alert key={i} variant="destructive" className="bg-red-50">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle className="text-xs uppercase tracking-wider font-bold">
                Logic Violation: {objectName}
              </AlertTitle>
              <AlertDescription className="text-sm">
                {descriptionText}
              </AlertDescription>
            </Alert>
          );
        })}
      </div>
    </div>
  );
}