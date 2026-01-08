import React, { useEffect, useRef } from 'react';
import { LogEntry } from '../types';
import { Terminal } from 'lucide-react';

interface ProcessingLogProps {
  logs: LogEntry[];
}

export const ProcessingLog: React.FC<ProcessingLogProps> = ({ logs }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="bg-slate-900 rounded-lg shadow-lg overflow-hidden flex flex-col h-full border border-slate-700">
      <div className="px-4 py-2 bg-slate-800 border-b border-slate-700 flex items-center gap-2">
        <Terminal size={16} className="text-green-400" />
        <span className="text-xs font-mono text-slate-300 font-semibold tracking-wide">SYSTEM LOGS / KNOWLEDGE RULES</span>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-2 scrollbar-hide font-mono text-xs">
        {logs.length === 0 && (
          <div className="text-slate-500 italic">Waiting for system events...</div>
        )}
        {logs.map((log, idx) => (
          <div key={idx} className="flex gap-2 animate-in fade-in slide-in-from-bottom-1 duration-300">
            <span className="text-slate-500 shrink-0">[{log.timestamp}]</span>
            <span className={`shrink-0 font-bold w-24
              ${log.status === 'success' ? 'text-green-400' : 
                log.status === 'warning' ? 'text-yellow-400' : 
                log.status === 'error' ? 'text-red-400' : 'text-blue-400'}
            `}>
              {log.step}
            </span>
            <span className="text-slate-300 break-words">{log.message}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};
