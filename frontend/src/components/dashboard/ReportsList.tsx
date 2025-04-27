import React from 'react';
import { Card } from '../ui/Card';
import { Report } from '../../types';
import { Button } from '../ui/Button';
import { Download, FileText } from 'lucide-react';

type ReportItemProps = {
  report: Report;
};

const ReportItem: React.FC<ReportItemProps> = ({ report }) => {
  const formattedDate = new Date(report.date).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
  
  return (
    <div className="flex items-start py-3 border-b border-slate-200 dark:border-slate-700/50 last:border-0">
      <div className="p-2 bg-indigo-50 dark:bg-indigo-900/30 rounded">
        <FileText size={16} className="text-indigo-600 dark:text-indigo-400" />
      </div>
      
      <div className="flex-1 min-w-0 ml-3">
        <h4 className="font-medium text-slate-900 dark:text-white text-sm">{report.title}</h4>
        <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          {formattedDate}
        </div>
        <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 line-clamp-2">
          {report.summary}
        </p>
      </div>
      
      <Button 
        variant="ghost" 
        size="sm" 
        icon={<Download size={14} />}
        iconPosition="right"
      >
        Download
      </Button>
    </div>
  );
};

type ReportsListProps = {
  reports: Report[];
};

export const ReportsList: React.FC<ReportsListProps> = ({ reports }) => {
  return (
    <Card title="Recent Reports" subtitle="Latest security analyses">
      <div className="space-y-0 -mt-3">
        {reports.map((report) => (
          <ReportItem key={report.id} report={report} />
        ))}
      </div>
    </Card>
  );
};