import { AlertCircle, X } from 'lucide-react';
import { useState, useEffect } from 'react';

interface ErrorNotificationProps {
  message: string | null;
  onDismiss?: () => void;
}

export const ErrorNotification = ({ message, onDismiss }: ErrorNotificationProps) => {
  const [isVisible, setIsVisible] = useState(!!message);

  useEffect(() => {
    setIsVisible(!!message);
    if (message) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        onDismiss?.();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [message, onDismiss]);

  if (!isVisible || !message) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-sm animate-in slide-in-from-right-4">
      <div className="bg-destructive text-destructive-foreground rounded-lg shadow-lg border border-destructive/50 p-4 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="text-sm font-medium">Error</p>
          <p className="text-sm opacity-90 mt-1">{message}</p>
        </div>
        <button
          onClick={() => {
            setIsVisible(false);
            onDismiss?.();
          }}
          className="flex-shrink-0 text-destructive-foreground/70 hover:text-destructive-foreground transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
