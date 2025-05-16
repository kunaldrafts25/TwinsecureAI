import React, { useEffect, useState } from 'react';
import { AlertTriangle, BarChart2, Clock, Shield } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { AttackVector, Alert } from '../../types';
import Card from '../common/Card';
import { mockAlerts } from '../../services/mockData';

interface AttackVectorDetailsProps {
  vectorName: string;
}

const AttackVectorDetails: React.FC<AttackVectorDetailsProps> = ({ vectorName }) => {
  const [vector, setVector] = useState<AttackVector | null>(null);
  const [vectorAlerts, setVectorAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Trend data for the chart
  const [trendData, setTrendData] = useState<{ date: string; count: number }[]>([]);
  
  // Severity distribution
  const [severityData, setSeverityData] = useState<{ name: string; value: number; color: string }[]>([]);
  
  const SEVERITY_COLORS = {
    critical: '#EF4444',
    high: '#F59E0B',
    medium: '#FBBF24',
    low: '#10B981',
    info: '#3B82F6',
  };
  
  useEffect(() => {
    // In a real app, this would fetch data from the API
    const fetchVectorDetails = async () => {
      setIsLoading(true);
      
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Mock vector data
        const mockVector: AttackVector = {
          name: vectorName,
          count: 42,
          percentage: 32.8,
        };
        
        // Filter alerts for this vector
        const alerts = mockAlerts.filter(alert => alert.alert_type.includes(vectorName));
        
        // Generate trend data
        const dates = new Set<string>();
        const now = new Date();
        for (let i = 30; i >= 0; i--) {
          const date = new Date(now);
          date.setDate(date.getDate() - i);
          dates.add(date.toISOString().split('T')[0]);
        }
        
        const trend = Array.from(dates).map(date => {
          const count = Math.floor(Math.random() * 5);
          return { date, count };
        });
        
        // Generate severity distribution
        const severityCounts: Record<string, number> = {
          critical: 0,
          high: 0,
          medium: 0,
          low: 0,
          info: 0,
        };
        
        alerts.forEach(alert => {
          severityCounts[alert.severity] = (severityCounts[alert.severity] || 0) + 1;
        });
        
        const severityDistribution = Object.entries(severityCounts).map(([name, value]) => ({
          name,
          value,
          color: SEVERITY_COLORS[name as keyof typeof SEVERITY_COLORS],
        }));
        
        setVector(mockVector);
        setVectorAlerts(alerts);
        setTrendData(trend);
        setSeverityData(severityDistribution);
      } catch (error) {
        console.error('Error fetching vector details:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchVectorDetails();
  }, [vectorName]);
  
  if (isLoading) {
    return <div className="p-4">Loading attack vector details...</div>;
  }
  
  if (!vector) {
    return <div className="p-4">Attack vector not found</div>;
  }
  
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="col-span-1">
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">Attack Vector Information</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-blue-500" />
                  <span>Vector Type</span>
                </div>
                <span className="font-bold">{vector.name}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-blue-500" />
                  <span>Total Alerts</span>
                </div>
                <span className="font-bold">{vector.count}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <BarChart2 className="h-5 w-5 text-blue-500" />
                  <span>Percentage</span>
                </div>
                <span className="font-bold">{vector.percentage}%</span>
              </div>
            </div>
          </div>
        </Card>
        
        <Card className="col-span-1 md:col-span-2">
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">Trend (Last 30 Days)</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={trendData}
                  margin={{ top: 10, right: 30, left: 0, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(value) => value.split('-')[2]} 
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(label) => `Date: ${label}`}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="count" 
                    stroke="#3B82F6" 
                    name="Alerts" 
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Card>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="col-span-1">
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">Severity Distribution</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                    labelLine={false}
                  >
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => [`${value} alerts`, '']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Card>
        
        <Card className="col-span-1 md:col-span-2">
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">Recent Alerts</h3>
            <div className="space-y-3">
              {vectorAlerts.length > 0 ? (
                vectorAlerts.slice(0, 5).map((alert) => (
                  <div key={alert.id} className="flex items-center justify-between border-b border-border pb-2">
                    <div>
                      <div className="font-medium">{alert.source_ip}</div>
                      <div className="text-sm text-muted-foreground">
                        {new Date(alert.created_at).toLocaleString()}
                      </div>
                    </div>
                    <div className="flex items-center">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        alert.severity === 'critical' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' :
                        alert.severity === 'high' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400' :
                        alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' :
                        'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                      }`}>
                        {alert.severity}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-muted-foreground">
                  No alerts found for this attack vector
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default AttackVectorDetails;
