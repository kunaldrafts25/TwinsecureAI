import React, { useEffect, useState } from 'react';
import { AlertTriangle, Clock, Globe, Server, Shield } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Attacker, Alert } from '../../types';
import Card from '../common/Card';
import { mockAlerts } from '../../services/mockData';
import { formatDate } from '../../utils/lib';

interface AttackerDetailsProps {
  ip: string;
}

const AttackerDetails: React.FC<AttackerDetailsProps> = ({ ip }) => {
  const [attacker, setAttacker] = useState<Attacker | null>(null);
  const [attackerAlerts, setAttackerAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Activity data for the chart
  const [activityData, setActivityData] = useState<{ date: string; count: number }[]>([]);

  useEffect(() => {
    // In a real app, this would fetch data from the API
    const fetchAttackerDetails = async () => {
      setIsLoading(true);

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Find attacker in mock data
        const mockAttacker: Attacker = {
          ip,
          country: 'US',
          count: 35,
          last_seen: new Date().toISOString(),
        };

        // Filter alerts for this attacker
        const alerts = mockAlerts.filter(alert => alert.source_ip === ip);

        // Generate activity data
        const dates = new Set<string>();
        const now = new Date();
        for (let i = 14; i >= 0; i--) {
          const date = new Date(now);
          date.setDate(date.getDate() - i);
          dates.add(date.toISOString().split('T')[0]);
        }

        const activity = Array.from(dates).map(date => {
          const count = Math.floor(Math.random() * 10);
          return { date, count };
        });

        setAttacker(mockAttacker);
        setAttackerAlerts(alerts);
        setActivityData(activity);
      } catch (error) {
        console.error('Error fetching attacker details:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAttackerDetails();
  }, [ip]);

  if (isLoading) {
    return <div className="p-4">Loading attacker details...</div>;
  }

  if (!attacker) {
    return <div className="p-4">Attacker not found</div>;
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="col-span-1">
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">Attacker Information</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Server className="h-5 w-5 text-blue-500" />
                  <span>IP Address</span>
                </div>
                <span className="font-bold">{attacker.ip}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Globe className="h-5 w-5 text-blue-500" />
                  <span>Country</span>
                </div>
                <span className="font-bold">{attacker.country}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-blue-500" />
                  <span>Total Attacks</span>
                </div>
                <span className="font-bold">{attacker.count}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-blue-500" />
                  <span>Last Seen</span>
                </div>
                <span className="font-bold">
                  {formatDate(attacker.last_seen)}
                </span>
              </div>
            </div>
          </div>
        </Card>

        <Card className="col-span-1 md:col-span-2">
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">Attack Activity (Last 14 Days)</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={activityData}
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
                  <Bar dataKey="count" fill="#3B82F6" name="Attacks" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4">Recent Alerts</h3>
          <div className="space-y-3">
            {attackerAlerts.length > 0 ? (
              attackerAlerts.slice(0, 5).map((alert) => (
                <div key={alert.id} className="flex items-center justify-between border-b border-border pb-2">
                  <div>
                    <div className="font-medium">{alert.alert_type}</div>
                    <div className="text-sm text-muted-foreground">
                      {formatDate(alert.created_at)}
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
                No alerts found for this attacker
              </div>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default AttackerDetails;
