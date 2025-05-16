import React from 'react';
import Card from '../../components/common/Card';
import RiskScoreGauge from '../../components/common/RiskScoreGauge';
import { Shield } from 'lucide-react';

const MsspDashboardPage: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Shield className="w-8 h-8 text-blue-600" />
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">MSSP Dashboard</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card className="col-span-1">
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Overall Security Score</h3>
            <RiskScoreGauge value={85} />
          </div>
        </Card>

        <Card className="col-span-1">
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Active Clients</h3>
            <div className="text-3xl font-bold text-blue-600">24</div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">Currently monitored organizations</p>
          </div>
        </Card>

        <Card className="col-span-1">
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Open Alerts</h3>
            <div className="text-3xl font-bold text-amber-600">12</div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">Requiring attention</p>
          </div>
        </Card>

        <Card className="col-span-1 md:col-span-2 lg:col-span-3">
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Client Overview</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead>
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Client</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Risk Score</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Active Alerts</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {[
                    { name: 'Acme Corp', score: 92, alerts: 2, status: 'Healthy' },
                    { name: 'TechStart Inc', score: 78, alerts: 5, status: 'Warning' },
                    { name: 'Global Systems', score: 85, alerts: 3, status: 'Healthy' },
                    { name: 'DataFlow Ltd', score: 65, alerts: 8, status: 'Critical' },
                  ].map((client) => (
                    <tr key={client.name}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{client.name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{client.score}%</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{client.alerts}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          client.status === 'Healthy' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                          client.status === 'Warning' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                          'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        }`}>
                          {client.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default MsspDashboardPage;