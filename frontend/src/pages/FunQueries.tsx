import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { QuerySelector } from '@/components/QuerySelector';
import { QueryResults } from '@/components/QueryResults';
import { useFunQueries } from '@/hooks/useFunQueries';
import { Database, Play, Download, BarChart3 } from 'lucide-react';

export default function FunQueries() {
  const { templates, executeQuery, isLoading, data, error } = useFunQueries();
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  const handleExecuteQuery = async () => {
    if (selectedTemplate) {
      await executeQuery(selectedTemplate);
    }
  };

  const handleExportResults = () => {
    if (data?.data) {
      const csv = convertToCSV(data.data);
      downloadCSV(csv, `${selectedTemplate}_results.csv`);
    }
  };

  const convertToCSV = (jsonData: any[]): string => {
    if (!jsonData.length) return '';
    
    const headers = Object.keys(jsonData[0]);
    const csvRows = [
      headers.join(','),
      ...jsonData.map(row => 
        headers.map(header => {
          const value = row[header];
          return typeof value === 'string' && value.includes(',') 
            ? `"${value}"` 
            : value;
        }).join(',')
      )
    ];
    
    return csvRows.join('\n');
  };

  const downloadCSV = (csv: string, filename: string) => {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto p-6 space-y-8">
        {/* Header */}
        <header className="flex flex-col space-y-4">
          <div className="flex items-center gap-3">
            <span className="p-2 bg-purple-600 rounded-lg">
              <Database className="h-6 w-6 text-white" />
            </span>
            <div>
              <h1 className="text-3xl font-bold text-slate-900">
                Fun Queries
              </h1>
              <p className="text-slate-600">
                Predefined queries to analyze your asset data
              </p>
            </div>
          </div>
        </header>

        {/* Query Selection */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Select Query
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <QuerySelector
                  templates={templates}
                  selectedCategory={selectedCategory}
                  selectedTemplate={selectedTemplate}
                  onCategoryChange={setSelectedCategory}
                  onTemplateChange={setSelectedTemplate}
                />
                
                <Button 
                  onClick={handleExecuteQuery}
                  disabled={!selectedTemplate || isLoading}
                  className="w-full"
                >
                  <Play className="w-4 h-4 mr-2" />
                  {isLoading ? 'Executing...' : 'Execute Query'}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Results */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    Query Results
                    {data?.count !== undefined && (
                      <Badge variant="secondary" className="ml-2">
                        {data.count} results
                      </Badge>
                    )}
                  </CardTitle>
                  {data?.data && data.data.length > 0 && (
                    <Button
                      onClick={handleExportResults}
                      variant="outline"
                      size="sm"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Export CSV
                    </Button>
                  )}
                </div>
                {data?.template_name && (
                  <p className="text-sm text-slate-600">
                    {data.template_name}
                  </p>
                )}
              </CardHeader>
              <CardContent>
                <QueryResults 
                  data={data?.data || []} 
                  isLoading={isLoading}
                  error={error}
                />
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}