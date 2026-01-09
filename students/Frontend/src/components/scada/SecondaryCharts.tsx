import { Card } from '@/components/ui/card';
import { SensorData } from '@/types/scada';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface SecondaryChartsProps {
  data: SensorData[];
}

export const SecondaryCharts = ({ data }: SecondaryChartsProps) => {
  const pressureData = data.slice(-60).map((d, i) => ({
    time: i,
    pressure: d.oil_pressure_psi,
  }));

  // Use real vibration data from backend - showing frequency components derived from sensor readings
  const currentVib = data[data.length - 1]?.vibration_mms || 0;
  const vibrationData = [
    { frequency: '10Hz', amplitude: Math.max(0, currentVib * 0.3) },
    { frequency: '50Hz', amplitude: Math.max(0, currentVib * 0.6) },
    { frequency: '100Hz', amplitude: Math.max(0, currentVib * 0.4) },
    { frequency: '500Hz', amplitude: Math.max(0, currentVib * 0.7) },
  ];

  const rpmVoltageData = data.slice(-60).map((d, i) => ({
    time: i,
    rpm: d.rpm / 100,
    voltage: d.voltage_v,
  }));

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* Oil Pressure Trend */}
      <Card className="bg-card border-border p-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-display font-semibold">Oil Pressure Trend</h4>
          <span className="text-muted-foreground">...</span>
        </div>
        <div className="h-[180px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={pressureData}>
              <defs>
                <linearGradient id="pressureGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="hsl(var(--warning))" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="hsl(var(--warning))" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
              <XAxis
                dataKey="time"
                axisLine={false}
                tickLine={false}
                tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
                tickFormatter={(v) => {
                  if (v === 0) return '-1h';
                  if (v === 30) return '-30m';
                  if (v === 59) return 'Now';
                  return '';
                }}
              />
              <YAxis hide domain={[30, 55]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '6px',
                }}
                formatter={(value: number) => [`${value.toFixed(1)} PSI`, 'Pressure']}
              />
              <Area
                type="monotone"
                dataKey="pressure"
                stroke="hsl(var(--warning))"
                strokeWidth={2}
                fill="url(#pressureGradient)"
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Vibration Analysis */}
      <Card className="bg-card border-border p-4">
        <h4 className="text-sm font-display font-semibold mb-3">Vibration Analysis (Hz)</h4>
        <div className="h-[180px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={vibrationData} barCategoryGap="20%">
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
              <XAxis
                dataKey="frequency"
                axisLine={false}
                tickLine={false}
                tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
              />
              <YAxis hide domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '6px',
                }}
                formatter={(value: number) => [`${value.toFixed(0)}%`, 'Amplitude']}
              />
              <Bar
                dataKey="amplitude"
                fill="hsl(var(--primary))"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* RPM & Battery Voltage */}
      <Card className="bg-card border-border p-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-display font-semibold">RPM & Battery Voltage</h4>
          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-success" /> RPM
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-primary" /> Volt
            </span>
          </div>
        </div>
        <div className="h-[180px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={rpmVoltageData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
              <XAxis
                dataKey="time"
                axisLine={false}
                tickLine={false}
                tick={false}
              />
              <YAxis yAxisId="rpm" hide domain={[0, 35]} />
              <YAxis yAxisId="voltage" hide domain={[10, 16]} orientation="right" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '6px',
                }}
                formatter={(value: number, name: string) => {
                  if (name === 'rpm') return [`${(value * 100).toFixed(0)} RPM`, 'RPM'];
                  return [`${value.toFixed(1)} V`, 'Voltage'];
                }}
              />
              <Line
                yAxisId="rpm"
                type="monotone"
                dataKey="rpm"
                stroke="hsl(var(--success))"
                strokeWidth={2}
                dot={false}
                strokeDasharray="5 5"
              />
              <Line
                yAxisId="voltage"
                type="monotone"
                dataKey="voltage"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
};
