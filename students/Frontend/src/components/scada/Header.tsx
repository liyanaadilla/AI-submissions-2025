import { Settings, Bell, User } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface HeaderProps {
  isOnline: boolean;
  tickCount: number;
  uptime: string;
  isSimulated?: boolean;
}

export const Header = ({ isOnline, tickCount, uptime, isSimulated = false }: HeaderProps) => {
  return (
    <header className="flex items-center justify-between border-b border-border bg-card px-6 py-3 sticky top-0 z-50">
      <div className="flex items-center gap-4">
        <div className="text-primary">
          <svg className="w-8 h-8" fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M13.8261 17.4264C16.7203 18.1174 20.2244 18.5217 24 18.5217C27.7756 18.5217 31.2797 18.1174 34.1739 17.4264C36.9144 16.7722 39.9967 15.2331 41.3563 14.1648L24.8486 40.6391C24.4571 41.267 23.5429 41.267 23.1514 40.6391L6.64374 14.1648C8.00331 15.2331 11.0856 16.7722 13.8261 17.4264Z"
              fill="currentColor"
            />
            <path
              d="M8.51294 6.00549C8.76076 5.62239 9.18128 5.39062 9.63296 5.39062H38.367C38.8187 5.39062 39.2392 5.62239 39.4871 6.00549L44.5874 13.9045C45.0461 14.6156 44.5362 15.5486 43.6974 15.5486H4.30258C3.46379 15.5486 2.9539 14.6156 3.41265 13.9045L8.51294 6.00549Z"
              fill="currentColor"
            />
          </svg>
        </div>
        <div>
          <h1 className="text-xl font-display font-semibold tracking-tight">YSMAI SCADA Control</h1>
          <p className="text-xs text-muted-foreground">Engine ID: TNV-88-X</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden md:flex items-center gap-6 text-xs text-muted-foreground font-mono mr-4">
          <span>Uptime: {uptime}</span>
          <span>Ticks: {tickCount}</span>
        </div>
        
        <div
          className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium ${
            isOnline
              ? 'bg-success/20 text-success glow-success'
              : 'bg-destructive/20 text-destructive'
          }`}
        >
          <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-success live-pulse' : 'bg-destructive'}`} />
          {isSimulated ? 'SIMULATION' : 'System'}: {isOnline ? 'ONLINE' : 'OFFLINE'}
        </div>

        <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
          <Settings className="w-5 h-5" />
        </Button>

        <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-warning rounded-full" />
        </Button>

        <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
          <User className="w-5 h-5" />
        </Button>
      </div>
    </header>
  );
};
