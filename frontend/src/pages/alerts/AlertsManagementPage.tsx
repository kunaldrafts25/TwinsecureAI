import React, { useEffect, useState } from 'react';
import { 
  AlertTriangle, 
  Check, 
  ChevronDown, 
  Eye, 
  Filter,
  Plus,
  RefreshCw,
  Search,
  X,
} from 'lucide-react';
import { useAlertStore } from '../../features/alerts/store/alertStore';
import { Alert, AlertFilters, AlertSeverity, AlertStatus } from '../../types';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import Input from '../../components/common/Input';
import Select, { SelectOption } from '../../components/common/Select';
import StatusIndicator from '../../components/common/StatusIndicator';
import { formatDate } from '../../utils/lib';
import AlertDetailModal from './components/AlertDetailModal';

// Alert severity options
const severityOptions: SelectOption[] = [
  { value: '', label: 'All Severities' },
  { value: 'critical', label: 'Critical' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
  { value: 'info', label: 'Info' },
];

// Alert status options
const statusOptions: SelectOption[] = [
  { value: '', label: 'All Statuses' },
  { value: 'new', label: 'New' },
  { value: 'acknowledged', label: 'Acknowledged' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'false_positive', label: 'False Positive' },
];

const AlertsManagementPage: React.FC = () => {
  const { alerts, totalAlerts, getAlerts, isLoading, filters, setFilters, clearFilters, setSelectedAlert } = useAlertStore();
  
  // Local state for filter form
  const [localFilters, setLocalFilters] = useState<AlertFilters>({});
  const [showFilterPanel, setShowFilterPanel] = useState(false);
  const [selectedAlertId, setSelectedAlertId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  
  useEffect(() => {
    getAlerts();
  }, [getAlerts]);
  
  // Handle filter changes
  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setLocalFilters({ ...localFilters, [name]: value });
  };
  
  // Apply filters
  const applyFilters = () => {
    setFilters(localFilters);
    getAlerts(localFilters);
    setShowFilterPanel(false);
  };
  
  // Reset filters
  const resetFilters = () => {
    setLocalFilters({});
    clearFilters();
    getAlerts({});
    setShowFilterPanel(false);
  };
  
  // Toggle filter panel
  const toggleFilterPanel = () => {
    setShowFilterPanel(!showFilterPanel);
    if (!showFilterPanel) {
      setLocalFilters(filters);
    }
  };
  
  // Open alert detail modal
  const openAlertDetail = (alert: Alert) => {
    setSelectedAlert(alert);
    setSelectedAlertId(alert.id);
  };
  
  // Close alert detail modal
  const closeAlertDetail = () => {
    setSelectedAlert(null);
    setSelectedAlertId(null);
  };
  
  // Handle search
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };
  
  // Filter alerts based on search term
  const filteredAlerts = alerts.filter((alert) => {
    if (!searchTerm) return true;
    
    const searchLower = searchTerm.toLowerCase();
    return (
      alert.alert_type.toLowerCase().includes(searchLower) ||
      alert.source_ip.toLowerCase().includes(searchLower) ||
      alert.destination_ip.toLowerCase().includes(searchLower) ||
      alert.severity.toLowerCase().includes(searchLower) ||
      alert.status.toLowerCase().includes(searchLower)
    );
  });
  
  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Alerts Management</h1>
          <p className="text-foreground/70">View and manage security alerts</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            leftIcon={<RefreshCw size={14} />}
            onClick={() => getAlerts()}
            isLoading={isLoading}
          >
            Refresh
          </Button>
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Plus size={14} />}
          >
            Create Alert
          </Button>
        </div>
      </div>
      
      <Card>
        <div className="space-y-4">
          {/* Search and filter bar */}
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="relative w-full sm:max-w-md">
              <Input
                placeholder="Search alerts..."
                value={searchTerm}
                onChange={handleSearch}
                leftIcon={<Search size={16} />}
                rightIcon={
                  searchTerm ? (
                    <button
                      type="button"
                      onClick={() => setSearchTerm('')}
                      className="text-foreground/50 hover:text-foreground"
                    >
                      <X size={16} />
                    </button>
                  ) : undefined
                }
              />
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant={showFilterPanel ? 'secondary' : 'outline'}
                size="sm"
                leftIcon={<Filter size={14} />}
                rightIcon={<ChevronDown size={14} />}
                onClick={toggleFilterPanel}
              >
                Filter
              </Button>
              
              {Object.keys(filters).length > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  leftIcon={<X size={14} />}
                  onClick={resetFilters}
                >
                  Clear
                </Button>
              )}
            </div>
          </div>
          
          {/* Filter panel */}
          {showFilterPanel && (
            <div className="rounded-md border border-border bg-card/50 p-4">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
                <Select
                  name="severity"
                  label="Severity"
                  options={severityOptions}
                  value={localFilters.severity || ''}
                  onChange={handleFilterChange}
                />
                
                <Select
                  name="status"
                  label="Status"
                  options={statusOptions}
                  value={localFilters.status || ''}
                  onChange={handleFilterChange}
                />
                
                <Input
                  name="source_ip"
                  label="Source IP"
                  placeholder="Filter by IP..."
                  value={localFilters.source_ip || ''}
                  onChange={handleFilterChange}
                />
                
                <Input
                  name="date_from"
                  label="From Date"
                  type="date"
                  value={localFilters.date_from || ''}
                  onChange={handleFilterChange}
                />
              </div>
              
              <div className="mt-4 flex justify-end gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFilterPanel(false)}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  leftIcon={<Check size={14} />}
                  onClick={applyFilters}
                >
                  Apply Filters
                </Button>
              </div>
            </div>
          )}
          
          {/* Alerts table */}
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-border">
                  <th className="whitespace-nowrap py-3 text-left text-sm font-medium text-foreground/70">Severity</th>
                  <th className="whitespace-nowrap py-3 text-left text-sm font-medium text-foreground/70">Type</th>
                  <th className="whitespace-nowrap py-3 text-left text-sm font-medium text-foreground/70">Source IP</th>
                  <th className="whitespace-nowrap py-3 text-left text-sm font-medium text-foreground/70">Destination</th>
                  <th className="whitespace-nowrap py-3 text-left text-sm font-medium text-foreground/70">Status</th>
                  <th className="whitespace-nowrap py-3 text-left text-sm font-medium text-foreground/70">Time</th>
                  <th className="whitespace-nowrap py-3 text-left text-sm font-medium text-foreground/70">Actions</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  Array.from({ length: 5 }).map((_, index) => (
                    <tr key={index} className="animate-pulse border-b border-border">
                      <td className="py-4">
                        <div className="h-4 w-20 rounded bg-border"></div>
                      </td>
                      <td className="py-4">
                        <div className="h-4 w-32 rounded bg-border"></div>
                      </td>
                      <td className="py-4">
                        <div className="h-4 w-24 rounded bg-border"></div>
                      </td>
                      <td className="py-4">
                        <div className="h-4 w-24 rounded bg-border"></div>
                      </td>
                      <td className="py-4">
                        <div className="h-4 w-20 rounded bg-border"></div>
                      </td>
                      <td className="py-4">
                        <div className="h-4 w-32 rounded bg-border"></div>
                      </td>
                      <td className="py-4">
                        <div className="h-8 w-8 rounded bg-border"></div>
                      </td>
                    </tr>
                  ))
                ) : filteredAlerts.length > 0 ? (
                  filteredAlerts.map((alert) => (
                    <tr 
                      key={alert.id} 
                      className="border-b border-border hover:bg-foreground/5"
                    >
                      <td className="py-4">
                        <StatusIndicator type="severity" value={alert.severity} />
                      </td>
                      <td className="py-4 text-sm">{alert.alert_type}</td>
                      <td className="py-4 text-sm">
                        <div className="flex items-center gap-2">
                          <span>{alert.source_ip}</span>
                          {alert.ip_info?.country && (
                            <span className="rounded bg-foreground/5 px-1 py-0.5 text-xs">
                              {alert.ip_info.country}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-4 text-sm">{alert.destination_ip}</td>
                      <td className="py-4">
                        <StatusIndicator type="status" value={alert.status} />
                      </td>
                      <td className="py-4 text-sm">
                        {formatDate(alert.created_at)}
                      </td>
                      <td className="py-4">
                        <Button
                          variant="ghost"
                          size="sm"
                          leftIcon={<Eye size={16} />}
                          onClick={() => openAlertDetail(alert)}
                          aria-label="View alert details"
                        />
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-foreground/50">
                      <div className="flex flex-col items-center justify-center gap-2">
                        <AlertTriangle className="h-6 w-6" />
                        <p>No alerts found</p>
                        {Object.keys(filters).length > 0 && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={resetFilters}
                          >
                            Clear filters
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          
          {/* Pagination and stats */}
          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <div className="text-sm text-foreground/70">
              Showing <span className="font-medium">{filteredAlerts.length}</span> of{' '}
              <span className="font-medium">{totalAlerts}</span> alerts
            </div>
            
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" disabled>
                Previous
              </Button>
              <Button variant="outline" size="sm" disabled>
                Next
              </Button>
            </div>
          </div>
        </div>
      </Card>
      
      {/* Alert detail modal */}
      {selectedAlertId && <AlertDetailModal onClose={closeAlertDetail} />}
    </div>
  );
};

export default AlertsManagementPage;