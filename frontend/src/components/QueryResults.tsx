import { AlertCircle, Loader2, Table } from 'lucide-react';

interface QueryResultsProps {
  data: any[];
  isLoading: boolean;
  error: Error | null;
}

export function QueryResults({ data, isLoading, error }: QueryResultsProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-2 text-slate-600">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Executing query...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-2 text-red-600">
          <AlertCircle className="w-5 h-5" />
          <span>Error: {error.message}</span>
        </div>
      </div>
    );
  }

  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center text-slate-500">
          <Table className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No results to display</p>
          <p className="text-sm">Select and execute a query to see results</p>
        </div>
      </div>
    );
  }

  // Check if data contains aggregated results (count queries)
  const isAggregatedData = data.length > 0 && data[0].count !== undefined;

  if (isAggregatedData) {
    return <AggregatedResults data={data} />;
  }

  return <DetailedResults data={data} />;
}

function AggregatedResults({ data }: { data: any[] }) {
  // For count/aggregated queries, show as a simple table
  const columns = Object.keys(data[0]);
  
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-slate-200">
            {columns.map(column => (
              <th key={column} className="text-left p-3 font-medium text-slate-700 capitalize">
                {column.replace('_', ' ')}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index} className="border-b border-slate-100 hover:bg-slate-50">
              {columns.map(column => (
                <td key={column} className="p-3 text-slate-600">
                  {row[column] || 'N/A'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function DetailedResults({ data }: { data: any[] }) {
  // For detailed asset queries, show key asset information
  const keyColumns = ['asset_name', 'asset_tag', 'category', 'manufacturer', 'model', 'status', 'warranty_expires'];
  
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-slate-200">
            {keyColumns.map(column => (
              <th key={column} className="text-left p-3 font-medium text-slate-700">
                {formatColumnHeader(column)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index} className="border-b border-slate-100 hover:bg-slate-50">
              {keyColumns.map(column => (
                <td key={column} className="p-3 text-slate-600">
                  {formatCellValue(column, row[column])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatColumnHeader(column: string): string {
  return column
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase());
}

function formatCellValue(column: string, value: any): string {
  if (value === null || value === undefined) {
    return 'N/A';
  }
  
  if (column === 'warranty_expires' && value) {
    try {
      return new Date(value).toLocaleDateString();
    } catch {
      return value;
    }
  }
  
  return String(value);
}