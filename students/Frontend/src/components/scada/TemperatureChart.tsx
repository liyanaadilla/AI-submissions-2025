import { Card } from '@/components/ui/card';
import { SensorData } from '@/types/scada';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface TemperatureChartProps {
  data: SensorData[];
  currentTemp: number;
}

export const TemperatureChart = ({ data, currentTemp }: TemperatureChartProps) => {
  const chartData = data.map((d, index) => ({
    time: new Date(d.timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    }),
    temperature: d.temperature,
    index,
  }));

  const formatTime = (time: string, index: number) => {
    if (index % Math.max(1, Math.floor(chartData.length / 5)) === 0) {
      return time;
    }
    return '';
  };

  return (
    <Card className="bg-card border-border p-4 col-span-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-display font-semibold">Real-time Coolant Temperature</h3>
          <p className="text-xs text-muted-foreground">Last 1 Hour Monitoring Interval</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-success live-pulse" />
            <span className="text-xs text-success font-medium">LIVE UPDATE</span>
          </div>
          <div className="text-right">
            <span className="text-4xl font-display font-bold">{currentTemp.toFixed(0)}°F</span>
          </div>
        </div>
      </div>

      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity={0.4} />
                <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="hsl(var(--border))"
              vertical={false}
            />
            <XAxis
              dataKey="time"
              axisLine={false}
              tickLine={false}
              tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
              tickFormatter={formatTime}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[40, 120]}
              axisLine={false}
              tickLine={false}
              tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
              tickFormatter={(v) => `${v}°`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
              }}
              labelStyle={{ color: 'hsl(var(--muted-foreground))' }}
              itemStyle={{ color: 'hsl(var(--primary))' }}
              formatter={(value: number) => [`${value.toFixed(1)}°F`, 'Temperature']}
            />
            <ReferenceLine
              y={95}
              stroke="hsl(var(--destructive))"
              strokeDasharray="5 5"
              strokeOpacity={0.7}
            />
            <ReferenceLine
              y={50}
              stroke="hsl(var(--primary))"
              strokeDasharray="5 5"
              strokeOpacity={0.7}
            />
            <Area
              type="monotone"
              dataKey="temperature"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              fill="url(#tempGradient)"
              dot={false}
              activeDot={{
                r: 6,
                fill: 'hsl(var(--primary))',
                stroke: 'hsl(var(--background))',
                strokeWidth: 2,
              }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
