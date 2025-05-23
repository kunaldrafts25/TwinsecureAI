/*
 * TwinSecure - Advanced Cybersecurity Platform
 * Copyright © 2024 TwinSecure. All rights reserved.
 * 
 * This file is part of TwinSecure, a proprietary cybersecurity platform.
 * Unauthorized copying, distribution, modification, or use of this software
 * is strictly prohibited without explicit written permission.
 * 
 * For licensing inquiries: kunalsingh2514@gmail.com
 */

import React from 'react';
import { 
  AlertTriangle, 
  Calendar, 
  ExternalLink, 
  Globe, 
  Link2, 
  Server, 
  Shield, 
  User, 
  X,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import { useAlertStore } from '../../../features/alerts/store/alertStore';
import Button from '../../../components/common/Button';
import StatusIndicator from '../../../components/common/StatusIndicator';
import { formatDate } from '../../../utils/lib';

interface AlertDetailModalProps {
  onClose: () => void;
}

const AlertDetailModal: React.FC<AlertDetailModalProps> = ({ onClose }) => {
  const { selectedAlert, updateAlert } = useAlertStore();
  
  if (!selectedAlert) return null;
  
  // Update alert status
  const handleStatusChange = async (status: string) => {
    try {
      await updateAlert(selectedAlert.id, { 
        status: status as any,
        ...(status === 'resolved' ? { resolved_at: new Date().toISOString() } : {})
      });
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-background/80 backdrop-blur-sm" onClick={onClose} />
      
      <div className="relative max-h-[90vh] w-full max-w-4xl overflow-auto rounded-lg border border-border bg-card shadow-lg">
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-border bg-card p-4">
          <h2 className="text-xl font-bold">Alert Details</h2>
          <button
            onClick={onClose}
            className="rounded-full p-1 text-foreground/70 hover:bg-foreground/5 hover:text-foreground"
          >
            <X size={20} />
          </button>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            {/* Left column */}
            <div className="md:col-span-2">
              <div className="mb-6">
                <h3 className="mb-4 text-lg font-semibold">{selectedAlert.alert_type}</h3>
                <div className="flex flex-wrap gap-3">
                  <div className="rounded-md border border-border bg-card/50 px-3 py-1.5">
                    <div className="text-xs font-medium text-foreground/50">Severity</div>
                    <div className="mt-1">
                      <StatusIndicator type="severity" value={selectedAlert.severity} />
                    </div>
                  </div>
                  
                  <div className="rounded-md border border-border bg-card/50 px-3 py-1.5">
                    <div className="text-xs font-medium text-foreground/50">Status</div>
                    <div className="mt-1">
                      <StatusIndicator type="status" value={selectedAlert.status} />
                    </div>
                  </div>
                  
                  <div className="rounded-md border border-border bg-card/50 px-3 py-1.5">
                    <div className="text-xs font-medium text-foreground/50">Detected</div>
                    <div className="mt-1 text-sm">
                      {formatDate(selectedAlert.created_at)}
                    </div>
                  </div>
                  
                  <div className="rounded-md border border-border bg-card/50 px-3 py-1.5">
                    <div className="text-xs font-medium text-foreground/50">Abuse Score</div>
                    <div className="mt-1 text-sm font-medium">{selectedAlert.abuse_score}/100</div>
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                <h4 className="flex items-center gap-2 font-medium">
                  <Globe size={16} />
                  Network Information
                </h4>
                
                <div className="rounded-md border border-border bg-card/50 p-4">
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <div className="text-xs font-medium text-foreground/50">Source IP</div>
                      <div className="mt-1 flex items-center gap-2 text-sm">
                        <span>{selectedAlert.source_ip}</span>
                        {selectedAlert.ip_info?.country && (
                          <span className="rounded bg-foreground/5 px-1 py-0.5 text-xs">
                            {selectedAlert.ip_info.country}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-xs font-medium text-foreground/50">Destination IP</div>
                      <div className="mt-1 text-sm">{selectedAlert.destination_ip}</div>
                    </div>
                    
                    {selectedAlert.ip_info?.asn && (
                      <div>
                        <div className="text-xs font-medium text-foreground/50">ASN</div>
                        <div className="mt-1 text-sm">{selectedAlert.ip_info.asn}</div>
                      </div>
                    )}
                    
                    {selectedAlert.ip_info?.org && (
                      <div>
                        <div className="text-xs font-medium text-foreground/50">Organization</div>
                        <div className="mt-1 text-sm">{selectedAlert.ip_info.org}</div>
                      </div>
                    )}
                  </div>
                </div>
                
                <h4 className="flex items-center gap-2 font-medium">
                  <Shield size={16} />
                  MITRE ATT&CK Techniques
                </h4>
                
                <div className="rounded-md border border-border bg-card/50 p-4">
                  <div className="flex flex-wrap gap-2">
                    {selectedAlert.mitre_ttp_codes.map((code) => (
                      <a
                        key={code}
                        href={`https://attack.mitre.org/techniques/${code}/`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 rounded-md border border-primary/20 bg-primary/5 px-2 py-1 text-xs font-medium text-primary hover:bg-primary/10"
                      >
                        {code}
                        <ExternalLink size={12} />
                      </a>
                    ))}
                  </div>
                </div>
                
                <h4 className="flex items-center gap-2 font-medium">
                  <Server size={16} />
                  Affected Assets
                </h4>
                
                <div className="rounded-md border border-border bg-card/50 p-4">
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <div className="text-xs font-medium text-foreground/50">Digital Twin Asset</div>
                      <div className="mt-1 text-sm">{selectedAlert.digital_twin_asset_id}</div>
                    </div>
                    
                    <div>
                      <div className="text-xs font-medium text-foreground/50">Honeypot</div>
                      <div className="mt-1 text-sm">{selectedAlert.honeypot_id}</div>
                    </div>
                  </div>
                </div>
                
                <h4 className="flex items-center gap-2 font-medium">
                  <Link2 size={16} />
                  Payload Evidence
                </h4>
                
                <div className="rounded-md border border-border bg-card/50 p-4">
                  <div className="overflow-x-auto">
                    <pre className="text-xs text-foreground/90">
                      <code>{selectedAlert.payload_snippet}</code>
                    </pre>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Right column */}
            <div className="space-y-6">
              <div className="rounded-md border border-border bg-card/50 p-4">
                <h4 className="flex items-center gap-2 font-medium">
                  <User size={16} />
                  Assignment
                </h4>
                
                <div className="mt-4">
                  {selectedAlert.assigned_to_user_id ? (
                    <div className="rounded-md border border-primary/20 bg-primary/5 p-3">
                      <div className="flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-medium text-primary-foreground">
                          JD
                        </div>
                        <div>
                          <div className="font-medium">Assigned</div>
                          <div className="text-xs text-foreground/70">User #{selectedAlert.assigned_to_user_id}</div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="rounded-md border border-border bg-foreground/5 p-3 text-center text-sm text-foreground/70">
                      <p>Not assigned</p>
                      <Button
                        variant="outline"
                        size="sm"
                        className="mt-2 w-full"
                      >
                        Assign
                      </Button>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="rounded-md border border-border bg-card/50 p-4">
                <h4 className="flex items-center gap-2 font-medium">
                  <Calendar size={16} />
                  Timeline
                </h4>
                
                <div className="mt-4 space-y-4">
                  <div className="flex gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-error/10 text-sm font-medium text-error">
                      <AlertTriangle size={14} />
                    </div>
                    <div>
                      <div className="text-sm font-medium">Alert Created</div>
                      <div className="text-xs text-foreground/70">
                        {formatDate(selectedAlert.created_at)}
                      </div>
                    </div>
                  </div>
                  
                  {selectedAlert.status !== 'new' && (
                    <div className="flex gap-2">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary/10 text-sm font-medium text-secondary">
                        <CheckCircle size={14} />
                      </div>
                      <div>
                        <div className="text-sm font-medium">Status Updated</div>
                        <div className="text-xs text-foreground/70">
                          Status changed to <span className="font-medium">{selectedAlert.status.replace('_', ' ')}</span>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {selectedAlert.resolved_at && (
                    <div className="flex gap-2">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-success/10 text-sm font-medium text-success">
                        <CheckCircle size={14} />
                      </div>
                      <div>
                        <div className="text-sm font-medium">Alert Resolved</div>
                        <div className="text-xs text-foreground/70">
                          {formatDate(selectedAlert.resolved_at)}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="rounded-md border border-border bg-card/50 p-4">
                <h4 className="flex items-center gap-2 font-medium">
                  <Shield size={16} />
                  Actions
                </h4>
                
                <div className="mt-4 space-y-2">
                  {selectedAlert.status === 'new' && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start"
                      onClick={() => handleStatusChange('acknowledged')}
                    >
                      <CheckCircle size={14} className="mr-2" />
                      Acknowledge Alert
                    </Button>
                  )}
                  
                  {(selectedAlert.status === 'new' || selectedAlert.status === 'acknowledged') && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start"
                      onClick={() => handleStatusChange('in_progress')}
                    >
                      <CheckCircle size={14} className="mr-2" />
                      Mark as In Progress
                    </Button>
                  )}
                  
                  {selectedAlert.status !== 'resolved' && selectedAlert.status !== 'false_positive' && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start"
                      onClick={() => handleStatusChange('resolved')}
                    >
                      <CheckCircle size={14} className="mr-2" />
                      Mark as Resolved
                    </Button>
                  )}
                  
                  {selectedAlert.status !== 'false_positive' && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start"
                      onClick={() => handleStatusChange('false_positive')}
                    >
                      <XCircle size={14} className="mr-2" />
                      Mark as False Positive
                    </Button>
                  )}
                  
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                  >
                    <Shield size={14} className="mr-2" />
                    Trigger Response
                  </Button>
                </div>
              </div>
              
              <div className="rounded-md border border-border bg-card/50 p-4">
                <h4 className="mb-2 flex items-center gap-2 font-medium">
                  Notes
                </h4>
                
                {selectedAlert.notes ? (
                  <p className="text-sm">{selectedAlert.notes}</p>
                ) : (
                  <p className="text-sm text-foreground/50">No notes added yet.</p>
                )}
                
                <textarea
                  className="mt-3 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm placeholder:text-foreground/50 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  placeholder="Add a note..."
                  rows={3}
                ></textarea>
                
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-2"
                >
                  Add Note
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertDetailModal;