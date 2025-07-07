import { useState, useCallback } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import type { ExportConfig, ExportHistory, ExportStatus } from '@/types/export';

/**
 * Hook for managing PDF export functionality
 */
export const useAssetExport = () => {
  const [exportStatus, setExportStatus] = useState<ExportStatus>('idle');
  const [exportError, setExportError] = useState<string | null>(null);

  // Mutation for PDF export
  const exportMutation = useMutation({
    mutationFn: async (config: ExportConfig): Promise<Blob> => {
      setExportStatus('generating');
      setExportError(null);

      try {
        const response = await api.post('/assets/export-pdf', config, {
          responseType: 'blob',
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 60000, // 60 second timeout for PDF generation
        });

        if (response.status !== 200) {
          throw new Error(`Export failed with status: ${response.status}`);
        }

        return response.data;
      } catch (error: any) {
        setExportStatus('error');
        const errorMessage = error.response?.data?.detail || error.message || 'Export failed';
        setExportError(errorMessage);
        throw new Error(errorMessage);
      }
    },
    onSuccess: () => {
      setExportStatus('downloading');
    },
    onError: (error: Error) => {
      setExportStatus('error');
      setExportError(error.message);
    },
  });

  // Function to trigger PDF export and download
  const exportToPDF = useCallback(async (config: ExportConfig): Promise<void> => {
    try {
      setExportStatus('generating');
      const blob = await exportMutation.mutateAsync(config);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Generate filename with timestamp
      const timestamp = new Date().toISOString().slice(0, 16).replace(/[:-]/g, '');
      const filename = `${config.title.replace(/[^a-zA-Z0-9]/g, '_')}_${timestamp}.pdf`;
      link.download = filename;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Cleanup
      window.URL.revokeObjectURL(url);
      
      setExportStatus('success');
      
      // Reset status after 3 seconds
      setTimeout(() => {
        setExportStatus('idle');
        setExportError(null);
      }, 3000);
      
    } catch (error) {
      // Error is already handled in the mutation
      console.error('Export failed:', error);
    }
  }, [exportMutation]);

  // Query for export history
  const {
    data: exportHistory,
    isLoading: isLoadingHistory,
    refetch: refetchHistory
  } = useQuery<ExportHistory[]>({
    queryKey: ['export-history'],
    queryFn: async () => {
      const response = await api.get<ExportHistory[]>('/assets/export-history');
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Reset export state
  const resetExportState = useCallback(() => {
    setExportStatus('idle');
    setExportError(null);
  }, []);

  return {
    // Export functionality
    exportToPDF,
    isExporting: exportMutation.isPending,
    exportStatus,
    exportError,
    resetExportState,
    
    // Export history
    exportHistory,
    isLoadingHistory,
    refetchHistory,
    
    // Utility functions
    isIdle: exportStatus === 'idle',
    isGenerating: exportStatus === 'generating',
    isDownloading: exportStatus === 'downloading',
    isSuccess: exportStatus === 'success',
    isError: exportStatus === 'error',
  };
};

/**
 * Hook for validating export configuration
 */
export const useExportValidation = () => {
  const validateConfig = useCallback((config: ExportConfig): string[] => {
    const errors: string[] = [];

    // Validate title
    if (!config.title.trim()) {
      errors.push('Report title is required');
    }

    // Validate that at least one section is included
    if (!config.includeSummary && !config.includeCharts && !config.includeTable) {
      errors.push('At least one section (Summary, Charts, or Table) must be included');
    }

    // Validate summary cards if summary is included
    if (config.includeSummary && config.summaryCards.length === 0) {
      errors.push('At least one summary card must be selected when summary is included');
    }

    // Validate charts if charts are included
    if (config.includeCharts && config.selectedCharts.length === 0) {
      errors.push('At least one chart must be selected when charts are included');
    }

    // Validate table columns if table is included
    if (config.includeTable && config.tableColumns.length === 0) {
      errors.push('At least one table column must be selected when table is included');
    }

    return errors;
  }, []);

  return { validateConfig };
}; 