import { useState, useEffect } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription,
  DialogBody,
  DialogFooter 
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Download, 
  FileText, 
  BarChart3, 
  PieChart, 
  Table,
  Settings,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { useAssetExport, useExportValidation } from '@/hooks/useAssetExport';
import type { Asset } from '@/types/asset';
import type { ExportConfig } from '@/types/export';
import { 
  DEFAULT_EXPORT_CONFIG,
  CHART_TYPES,
  SUMMARY_CARDS,
  TABLE_COLUMNS
} from '@/types/export';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  assets: Asset[];
  currentFilters?: {
    company?: string;
    manufacturer?: string;
    category?: string;
    model?: string;
    department?: string;
    searchQuery?: string;
  };
}

export function ExportModal({ isOpen, onClose, assets, currentFilters }: ExportModalProps) {
  const [config, setConfig] = useState<ExportConfig>(DEFAULT_EXPORT_CONFIG);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  
  const { exportToPDF, exportStatus, exportError, isExporting } = useAssetExport();
  const { validateConfig } = useExportValidation();

  // Update table filters from current dashboard filters
  useEffect(() => {
    if (currentFilters) {
      setConfig(prev => ({
        ...prev,
        tableFilters: currentFilters
      }));
    }
  }, [currentFilters]);

  const handleConfigChange = (updates: Partial<ExportConfig>) => {
    setConfig(prev => ({ ...prev, ...updates }));
    setValidationErrors([]); // Clear validation errors when config changes
  };

  const handleExport = async () => {
    const errors = validateConfig(config);
    if (errors.length > 0) {
      setValidationErrors(errors);
      return;
    }

    try {
      await exportToPDF(config);
      // Modal will close automatically after successful export
      setTimeout(() => onClose(), 2000);
    } catch {
      // Error is handled by the hook
    }
  };

  const toggleSummaryCard = (cardType: string) => {
    setConfig(prev => ({
      ...prev,
      summaryCards: prev.summaryCards.includes(cardType as any)
        ? prev.summaryCards.filter(c => c !== cardType)
        : [...prev.summaryCards, cardType as any]
    }));
  };

  const toggleChart = (chartType: string) => {
    setConfig(prev => ({
      ...prev,
      selectedCharts: prev.selectedCharts.includes(chartType as any)
        ? prev.selectedCharts.filter(c => c !== chartType)
        : [...prev.selectedCharts, chartType as any]
    }));
  };

  const toggleTableColumn = (columnId: string) => {
    setConfig(prev => ({
      ...prev,
      tableColumns: prev.tableColumns.includes(columnId)
        ? prev.tableColumns.filter(c => c !== columnId)
        : [...prev.tableColumns, columnId]
    }));
  };

  const getExportStatusInfo = () => {
    switch (exportStatus) {
      case 'generating':
        return { icon: Loader2, text: 'Generating PDF...', color: 'text-blue-600' };
      case 'downloading':
        return { icon: Download, text: 'Downloading...', color: 'text-green-600' };
      case 'success':
        return { icon: CheckCircle, text: 'Export completed!', color: 'text-green-600' };
      case 'error':
        return { icon: AlertCircle, text: 'Export failed', color: 'text-red-600' };
      default:
        return null;
    }
  };

  const statusInfo = getExportStatusInfo();

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Export Asset Report
          </DialogTitle>
          <DialogDescription>
            Configure your PDF export with custom options for content, formatting, and data inclusion.
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          {/* Validation Errors */}
          {validationErrors.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-4 h-4 text-red-600" />
                <span className="text-sm font-medium text-red-800">Configuration Errors</span>
              </div>
              <ul className="text-sm text-red-700 space-y-1">
                {validationErrors.map((error, index) => (
                  <li key={index}>• {error}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Export Status */}
          {statusInfo && (
            <div className="bg-gray-50 border rounded-md p-4 mb-6">
              <div className="flex items-center gap-2">
                <statusInfo.icon className={`w-4 h-4 ${statusInfo.color} ${exportStatus === 'generating' ? 'animate-spin' : ''}`} />
                <span className={`text-sm font-medium ${statusInfo.color}`}>{statusInfo.text}</span>
              </div>
              {exportError && (
                <p className="text-sm text-red-600 mt-2">{exportError}</p>
              )}
            </div>
          )}

          <div className="space-y-6">
            {/* Report Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="w-4 h-4" />
                  Report Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Report Title</label>
                  <Input
                    value={config.title}
                    onChange={(e) => handleConfigChange({ title: e.target.value })}
                    placeholder="Enter report title"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Description (Optional)</label>
                  <Input
                    value={config.description || ''}
                    onChange={(e) => handleConfigChange({ description: e.target.value })}
                    placeholder="Brief description of the report"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Page Size</label>
                    <select
                      value={config.pageSize}
                      onChange={(e) => handleConfigChange({ pageSize: e.target.value as 'A4' | 'Letter' })}
                      className="w-full h-10 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="A4">A4</option>
                      <option value="Letter">Letter</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Orientation</label>
                    <select
                      value={config.orientation}
                      onChange={(e) => handleConfigChange({ orientation: e.target.value as 'portrait' | 'landscape' })}
                      className="w-full h-10 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="portrait">Portrait</option>
                      <option value="landscape">Landscape</option>
                    </select>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="includeTimestamp"
                    checked={config.includeTimestamp}
                    onChange={(e) => handleConfigChange({ includeTimestamp: e.target.checked })}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="includeTimestamp" className="text-sm">Include timestamp</label>
                </div>
              </CardContent>
            </Card>

            {/* Summary Section */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  Summary Cards
                  <input
                    type="checkbox"
                    checked={config.includeSummary}
                    onChange={(e) => handleConfigChange({ includeSummary: e.target.checked })}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 ml-auto"
                  />
                </CardTitle>
              </CardHeader>
              {config.includeSummary && (
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(SUMMARY_CARDS).map(([key, card]) => (
                      <div
                        key={key}
                        className={`p-3 border rounded-md cursor-pointer transition-colors ${
                          config.summaryCards.includes(key as any)
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => toggleSummaryCard(key)}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">{card.name}</span>
                          {config.summaryCards.includes(key as any) && (
                            <CheckCircle className="w-4 h-4 text-blue-600" />
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">{card.description}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              )}
            </Card>

            {/* Charts Section */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="w-4 h-4" />
                  Charts
                  <input
                    type="checkbox"
                    checked={config.includeCharts}
                    onChange={(e) => handleConfigChange({ includeCharts: e.target.checked })}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 ml-auto"
                  />
                </CardTitle>
              </CardHeader>
              {config.includeCharts && (
                <CardContent>
                  <div className="grid grid-cols-1 gap-3">
                    {Object.entries(CHART_TYPES).map(([key, chart]) => (
                      <div
                        key={key}
                        className={`p-3 border rounded-md cursor-pointer transition-colors ${
                          config.selectedCharts.includes(key as any)
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => toggleChart(key)}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">{chart.name}</span>
                          {config.selectedCharts.includes(key as any) && (
                            <CheckCircle className="w-4 h-4 text-blue-600" />
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">{chart.description}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              )}
            </Card>

            {/* Table Section */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Table className="w-4 h-4" />
                  Asset Table
                  <input
                    type="checkbox"
                    checked={config.includeTable}
                    onChange={(e) => handleConfigChange({ includeTable: e.target.checked })}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 ml-auto"
                  />
                </CardTitle>
              </CardHeader>
              {config.includeTable && (
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Table Columns</label>
                      <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto border border-gray-200 rounded-md p-3">
                        {Object.entries(TABLE_COLUMNS).map(([key, column]) => (
                          <div key={key} className="flex items-center gap-2">
                            <input
                              type="checkbox"
                              id={`column-${key}`}
                              checked={config.tableColumns.includes(key)}
                              onChange={() => toggleTableColumn(key)}
                              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                            />
                            <label htmlFor={`column-${key}`} className="text-sm">
                              {column.name}
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {/* Applied Filters Display */}
                    {currentFilters && Object.values(currentFilters).some(Boolean) && (
                      <div>
                        <label className="block text-sm font-medium mb-2">Applied Filters</label>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(currentFilters).map(([key, value]) => 
                            value ? (
                              <Badge key={key} variant="secondary">
                                {key}: {value}
                              </Badge>
                            ) : null
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                          Current dashboard filters will be applied to the exported table data.
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              )}
            </Card>

            {/* Data Summary */}
            <Card>
              <CardContent className="pt-6">
                <div className="text-sm text-gray-600">
                  <p><strong>Total Assets:</strong> {assets.length}</p>
                  <p><strong>Export Size:</strong> Estimated 200-300KB</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </DialogBody>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isExporting}>
            Cancel
          </Button>
          <Button 
            onClick={handleExport} 
            disabled={isExporting || exportStatus === 'success'}
            className="min-w-[120px]"
          >
            {isExporting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : exportStatus === 'success' ? (
              <>
                <CheckCircle className="w-4 h-4 mr-2" />
                Completed!
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                Generate PDF
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 