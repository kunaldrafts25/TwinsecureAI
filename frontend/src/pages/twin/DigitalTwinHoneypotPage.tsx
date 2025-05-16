import React, { useState } from 'react';
import {
  Shield,
  Server,
  Plus,
  RefreshCw,
  Settings,
  Activity,
  Eye,
  Power,
  Trash2
} from 'lucide-react';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import StatusIndicator from '../../components/common/StatusIndicator';
import { mockHoneypots } from '../../services/mockData';
import DigitalTwinConfigureModal from './components/DigitalTwinConfigureModal';
import DigitalTwinMonitorModal from './components/DigitalTwinMonitorModal';

const DigitalTwinHoneypotPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'twins' | 'honeypots'>('twins');
  const [selectedTwin, setSelectedTwin] = useState<number | null>(null);
  const [isConfigureModalOpen, setIsConfigureModalOpen] = useState(false);
  const [isMonitorModalOpen, setIsMonitorModalOpen] = useState(false);

  // Handle configure button click
  const handleConfigureClick = (twinId: number) => {
    setSelectedTwin(twinId);
    setIsConfigureModalOpen(true);
  };

  // Handle monitor button click
  const handleMonitorClick = (twinId: number) => {
    setSelectedTwin(twinId);
    setIsMonitorModalOpen(true);
  };

  // Close modals
  const handleCloseConfigureModal = () => {
    setIsConfigureModalOpen(false);
  };

  const handleCloseMonitorModal = () => {
    setIsMonitorModalOpen(false);
  };
  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Digital Twin & Honeypot Management</h1>
          <p className="text-foreground/70">Configure and monitor your digital twins and honeypots</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            leftIcon={<RefreshCw size={14} />}
          >
            Refresh
          </Button>
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Plus size={14} />}
          >
            Create New
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-border">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            onClick={() => setActiveTab('twins')}
            className={`border-b-2 py-4 px-1 text-sm font-medium ${
              activeTab === 'twins'
                ? 'border-primary text-primary'
                : 'border-transparent text-foreground/60 hover:border-foreground/30 hover:text-foreground/80'
            }`}
          >
            Digital Twins
          </button>
          <button
            onClick={() => setActiveTab('honeypots')}
            className={`border-b-2 py-4 px-1 text-sm font-medium ${
              activeTab === 'honeypots'
                ? 'border-primary text-primary'
                : 'border-transparent text-foreground/60 hover:border-foreground/30 hover:text-foreground/80'
            }`}
          >
            Honeypots
          </button>
        </nav>
      </div>

      {/* Digital Twins Section */}
      {activeTab === 'twins' && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <Card key={index}>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                      <Server className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-medium">Web Server {index + 1}</h3>
                      <p className="text-sm text-foreground/70">10.0.0.{index + 1}</p>
                    </div>
                  </div>
                  <StatusIndicator type="status" value="active" />
                </div>

                <div className="mt-4 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-foreground/70">Type:</span>
                    <span>Apache Server</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-foreground/70">Services:</span>
                    <span>HTTP, HTTPS</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-foreground/70">Last Activity:</span>
                    <span>2 mins ago</span>
                  </div>
                </div>

                <div className="mt-6 flex justify-end gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={<Settings size={14} />}
                    onClick={() => handleConfigureClick(index + 1)}
                  >
                    Configure
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={<Activity size={14} />}
                    onClick={() => handleMonitorClick(index + 1)}
                  >
                    Monitor
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Honeypots Section */}
      {activeTab === 'honeypots' && (
        <div className="space-y-6">
          <div className="overflow-x-auto rounded-lg border border-border">
            <table className="min-w-full divide-y divide-border">
              <thead className="bg-card/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">Last Activity</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">Engagements</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-foreground/70 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-card divide-y divide-border">
                {mockHoneypots.map((honeypot) => (
                  <tr key={honeypot.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <Shield className="h-5 w-5 text-primary" />
                        <div>
                          <div className="font-medium">{honeypot.name}</div>
                          <div className="text-sm text-foreground/70">{honeypot.id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
                        {honeypot.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusIndicator
                        type="status"
                        value={honeypot.status === 'engaged' ? 'in_progress' : honeypot.status}
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {new Date(honeypot.last_activity).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {honeypot.total_engagements}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          leftIcon={<Eye size={14} />}
                          aria-label="View details"
                        />
                        <Button
                          variant="ghost"
                          size="sm"
                          leftIcon={<Power size={14} />}
                          aria-label="Toggle power"
                        />
                        <Button
                          variant="ghost"
                          size="sm"
                          leftIcon={<Trash2 size={14} />}
                          aria-label="Delete"
                        />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modals */}
      {selectedTwin !== null && (
        <>
          <DigitalTwinConfigureModal
            isOpen={isConfigureModalOpen}
            onClose={handleCloseConfigureModal}
            twinId={selectedTwin}
            twinName={`Web Server ${selectedTwin}`}
            twinType="web-server"
            twinIp={`10.0.0.${selectedTwin}`}
          />

          <DigitalTwinMonitorModal
            isOpen={isMonitorModalOpen}
            onClose={handleCloseMonitorModal}
            twinId={selectedTwin}
            twinName={`Web Server ${selectedTwin}`}
            twinType="web-server"
            twinIp={`10.0.0.${selectedTwin}`}
          />
        </>
      )}
    </div>
  );
};

export default DigitalTwinHoneypotPage;