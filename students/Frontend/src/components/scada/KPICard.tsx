import { ReactNode } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface KPICardProps {
  title: string;
  children: ReactNode;
  badge?: {
    text: string;
    variant: 'success' | 'warning' | 'danger' | 'info';
  };
}

export const KPICard = ({ title, children, badge }: KPICardProps) => {
  const badgeStyles = {
    success: 'bg-success/20 text-success border-success/30',
    warning: 'bg-warning/20 text-warning border-warning/30',
    danger: 'bg-destructive/20 text-destructive border-destructive/30',
    info: 'bg-primary/20 text-primary border-primary/30',
  };

  return (
    <Card className="bg-card border-border p-4 relative overflow-hidden">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
          {title}
        </span>
        {badge && (
          <Badge 
            variant="outline" 
            className={`text-[10px] px-2 py-0.5 ${badgeStyles[badge.variant]}`}
          >
            {badge.text}
          </Badge>
        )}
      </div>
      <div className="flex items-center justify-center">{children}</div>
    </Card>
  );
};
