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

import React, { useState } from 'react';
import { X, Save, Server, Shield, Globe, Database, Cpu } from 'lucide-react';
import Button from '../../../components/common/Button';
import DetailModal from '../../../components/dashboard/DetailModal';

interface DigitalTwinConfigureModalProps {
  isOpen: boolean;
  onClose: () => void;
  twinId: number;
  twinName: string;
  twinType: string;
  twinIp: string;
}

const DigitalTwinConfigureModal: React.FC<DigitalTwinConfigureModalProps> = ({
  isOpen,
  onClose,
  twinId,
  twinName,
  twinType,
  twinIp,
}) => {
  // State for form fields
  const [name, setName] = useState(twinName);
  const [description, setDescription] = useState('A virtual replica of a production server');
  const [services, setServices] = useState(['HTTP', 'HTTPS']);
  const [exposedPorts, setExposedPorts] = useState('80, 443');
  const [vulnerabilityLevel, setVulnerabilityLevel] = useState('medium');
  const [isLoading, setIsLoading] = useState(false);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      onClose();
      // Show success notification (would be implemented in a real app)
      alert('Digital Twin configuration updated successfully!');
    }, 1000);
  };

  // Add/remove service
  const toggleService = (service: string) => {
    if (services.includes(service)) {
      setServices(services.filter(s => s !== service));
    } else {
      setServices([...services, service]);
    }
  };

  return (
    <DetailModal
      title={`Configure Digital Twin: ${twinName}`}
      isOpen={isOpen}
      onClose={onClose}
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Basic Information</h3>
          
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="name" className="block text-sm font-medium">
                Name
              </label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="mt-1 block w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              />
            </div>
            
            <div>
              <label htmlFor="type" className="block text-sm font-medium">
                Type
              </label>
              <select
                id="type"
                defaultValue={twinType}
                className="mt-1 block w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                <option value="web-server">Web Server</option>
                <option value="database">Database Server</option>
                <option value="file-server">File Server</option>
                <option value="mail-server">Mail Server</option>
              </select>
            </div>
          </div>
          
          <div>
            <label htmlFor="description" className="block text-sm font-medium">
              Description
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="mt-1 block w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            />
          </div>
        </div>
        
        {/* Network Configuration */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Network Configuration</h3>
          
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="ip" className="block text-sm font-medium">
                IP Address
              </label>
              <input
                type="text"
                id="ip"
                defaultValue={twinIp}
                className="mt-1 block w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              />
            </div>
            
            <div>
              <label htmlFor="ports" className="block text-sm font-medium">
                Exposed Ports
              </label>
              <input
                type="text"
                id="ports"
                value={exposedPorts}
                onChange={(e) => setExposedPorts(e.target.value)}
                className="mt-1 block w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                placeholder="80, 443, 22"
              />
            </div>
          </div>
        </div>
        
        {/* Services */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Services</h3>
          
          <div className="flex flex-wrap gap-2">
            {['HTTP', 'HTTPS', 'SSH', 'FTP', 'SMTP', 'DNS'].map((service) => (
              <button
                key={service}
                type="button"
                onClick={() => toggleService(service)}
                className={`rounded-full px-3 py-1 text-xs font-medium ${
                  services.includes(service)
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary text-secondary-foreground'
                }`}
              >
                {service}
              </button>
            ))}
          </div>
        </div>
        
        {/* Security Settings */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Security Settings</h3>
          
          <div>
            <label htmlFor="vulnerability" className="block text-sm font-medium">
              Vulnerability Level
            </label>
            <select
              id="vulnerability"
              value={vulnerabilityLevel}
              onChange={(e) => setVulnerabilityLevel(e.target.value)}
              className="mt-1 block w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="none">None - Fully Patched</option>
              <option value="low">Low - Minor Vulnerabilities</option>
              <option value="medium">Medium - Common Vulnerabilities</option>
              <option value="high">High - Critical Vulnerabilities</option>
            </select>
          </div>
        </div>
        
        {/* Form Actions */}
        <div className="flex justify-end gap-2">
          <Button
            variant="outline"
            type="button"
            onClick={onClose}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            type="submit"
            leftIcon={<Save size={14} />}
            isLoading={isLoading}
          >
            Save Changes
          </Button>
        </div>
      </form>
    </DetailModal>
  );
};

export default DigitalTwinConfigureModal;
