import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer } from "recharts";
import { TrendingUp } from "lucide-react";

export default function WinProbabilityChart() {
  const [chartData, setChartData] = useState<any[]>([]);

  useEffect(() => {
    // Generate mock live probability progression
    const generateData = () => {
      const data = [];
      let baseProb = 64.2;
      
      for (let over = 0; over <= 20; over++) {
        const variation = Math.sin(over * 0.3) * 10 + (Math.random() * 5 - 2.5);
        const prob = Math.max(20, Math.min(80, baseProb + variation));
        data.push({
          over,
          probability: Math.round(prob * 10) / 10
        });
        baseProb = prob;
      }
      
      return data;
    };

    setChartData(generateData());
  }, []);

  return (
    <Card data-testid="win-probability-chart">
      <CardContent className="p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
          <TrendingUp className="text-primary mr-2" />
          Win Probability Progression
          <span className="ml-auto text-sm text-muted-foreground font-normal">Simulated Match Flow</span>
        </h3>
        
        {/* Chart Container */}
        <div className="chart-container rounded-lg p-4 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <XAxis 
                dataKey="over" 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: 'hsl(215.4, 16.3%, 46.9%)' }}
              />
              <YAxis 
                domain={[0, 100]}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: 'hsl(215.4, 16.3%, 46.9%)' }}
                tickFormatter={(value) => `${value}%`}
              />
              <Line 
                type="monotone" 
                dataKey="probability" 
                stroke="hsl(142, 76%, 36%)" 
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 4, fill: 'hsl(142, 76%, 36%)' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        <p className="text-center text-sm text-muted-foreground mt-2">Overs →</p>
      </CardContent>
    </Card>
  );
}
