/**
 * TypeScript interfaces for PDF export functionality.
 * These match the backend Pydantic models in backend/app/models.py
 */

export interface TableFilters {
  company?: string;
  manufacturer?: string;
  category?: string;
  model?: string;
  searchQuery?: string;
}

export interface ExportConfig {
  // Report metadata
  title: string;
  description?: string;
  includeFilters: boolean;
  
  // Summary section
  includeSummary: boolean;
  summaryCards: Array<'total' | 'active' | 'pending' | 'stock'>;
  
  // Charts section
  includeCharts: boolean;
  selectedCharts: Array<'category' | 'status' | 'trends' | 'warranty'>;
  
  // Table section
  includeTable: boolean;
  tableColumns: string[];
  tableFilters?: TableFilters;
  
  // Formatting options
  pageSize: 'A4' | 'Letter';
  orientation: 'portrait' | 'landscape';
  includeTimestamp: boolean;
}

export interface ExportHistory {
  id: number;
  config_json: string;
  created_at: string;
  file_size_bytes: number;
  download_count: number;
  export_type: string;
  status: 'pending' | 'completed' | 'failed';
}

export interface ExportResponse {
  success: boolean;
  message: string;
  file_size_bytes?: number;
  export_id?: number;
}

// Chart type definitions for the UI
export const CHART_TYPES = {
  category: {
    id: 'category',
    name: 'Assets by Category',
    description: 'Bar chart showing asset distribution by category'
  },
  status: {
    id: 'status',
    name: 'Status Distribution',
    description: 'Pie chart showing asset status breakdown'
  },
  trends: {
    id: 'trends',
    name: 'Monthly Trends',
    description: 'Area chart showing asset creation trends over time'
  },
  warranty: {
    id: 'warranty',
    name: 'Warranty Expiration',
    description: 'Bar chart showing warranty expiration timeline'
  }
} as const;

// Summary card type definitions
export const SUMMARY_CARDS = {
  total: {
    id: 'total',
    name: 'Total Assets',
    description: 'Total number of assets in the system'
  },
  active: {
    id: 'active',
    name: 'Active Assets',
    description: 'Assets currently in active use'
  },
  pending: {
    id: 'pending',
    name: 'Pending Rebuild',
    description: 'Assets pending rebuild or maintenance'
  },
  stock: {
    id: 'stock',
    name: 'In Stock',
    description: 'Assets available in inventory'
  }
} as const;

// Available table columns
export const TABLE_COLUMNS = {
  asset_name: { id: 'asset_name', name: 'Asset Name', width: 'w-40' },
  asset_tag: { id: 'asset_tag', name: 'Asset Tag', width: 'w-32' },
  category: { id: 'category', name: 'Category', width: 'w-32' },
  manufacturer: { id: 'manufacturer', name: 'Manufacturer', width: 'w-36' },
  model: { id: 'model', name: 'Model', width: 'w-36' },
  serial: { id: 'serial', name: 'Serial Number', width: 'w-40' },
  status: { id: 'status', name: 'Status', width: 'w-32' },
  company: { id: 'company', name: 'Company', width: 'w-36' },
  location: { id: 'location', name: 'Location', width: 'w-36' },
  warranty_expires: { id: 'warranty_expires', name: 'Warranty Expires', width: 'w-40' },
  created_at: { id: 'created_at', name: 'Created Date', width: 'w-40' }
} as const;

// Export status types for UI feedback
export type ExportStatus = 'idle' | 'configuring' | 'generating' | 'downloading' | 'success' | 'error';

// Default export configuration
export const DEFAULT_EXPORT_CONFIG: ExportConfig = {
  title: 'Asset Management Report',
  description: '',
  includeFilters: true,
  includeSummary: true,
  summaryCards: ['total', 'active', 'pending', 'stock'],
  includeCharts: true,
  selectedCharts: ['category', 'status'],
  includeTable: true,
  tableColumns: ['asset_name', 'category', 'manufacturer', 'status'],
  tableFilters: undefined,
  pageSize: 'A4',
  orientation: 'portrait',
  includeTimestamp: true
}; 