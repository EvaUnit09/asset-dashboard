import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';

interface QueryTemplate {
  name: string;
  description: string;
}

interface QueryCategory {
  title: string;
  description: string;
  queries: Record<string, QueryTemplate>;
}

interface QuerySelectorProps {
  templates: Record<string, QueryCategory> | null;
  selectedCategory: string;
  selectedTemplate: string;
  onCategoryChange: (category: string) => void;
  onTemplateChange: (template: string) => void;
}

export function QuerySelector({ 
  templates, 
  selectedCategory, 
  selectedTemplate, 
  onCategoryChange, 
  onTemplateChange 
}: QuerySelectorProps) {
  if (!templates) {
    return <div className="text-center text-slate-500">Loading templates...</div>;
  }

  const categories = Object.keys(templates);
  const selectedCategoryData = selectedCategory ? templates[selectedCategory] : null;

  return (
    <div className="space-y-4">
      {/* Category Selection */}
      <div>
        <label className="text-sm font-medium text-slate-700 mb-2 block">
          Query Category
        </label>
        <Select value={selectedCategory} onValueChange={onCategoryChange}>
          <SelectTrigger>
            <SelectValue placeholder="Select a category" />
          </SelectTrigger>
          <SelectContent>
            {categories.map(categoryKey => (
              <SelectItem key={categoryKey} value={categoryKey}>
                {templates[categoryKey].title}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {selectedCategoryData && (
          <p className="text-xs text-slate-500 mt-1">
            {selectedCategoryData.description}
          </p>
        )}
      </div>

      {/* Template Selection */}
      {selectedCategory && selectedCategoryData && selectedCategoryData.queries && (
        <div>
          <label className="text-sm font-medium text-slate-700 mb-2 block">
            Query Template
          </label>
          <Select value={selectedTemplate} onValueChange={onTemplateChange}>
            <SelectTrigger>
              <SelectValue placeholder="Select a query" />
            </SelectTrigger>
                                <SelectContent>
            {Object.entries(selectedCategoryData.queries || {}).map(([templateKey, template]) => {
              // Defensive check to ensure template exists and has required properties
              if (!template || !template.name) {
                console.warn(`Invalid template for key: ${templateKey}`, template);
                return null;
              }
              return (
                <SelectItem key={templateKey} value={templateKey}>
                  {template.name}
                </SelectItem>
              );
            }).filter(Boolean)}
          </SelectContent>
          </Select>
          {selectedTemplate && selectedCategoryData.queries[selectedTemplate] && (
            <p className="text-xs text-slate-500 mt-1">
              {selectedCategoryData.queries[selectedTemplate].description}
            </p>
          )}
        </div>
      )}

      {/* Query Info */}
      {selectedTemplate && selectedCategoryData && selectedCategoryData.queries && selectedCategoryData.queries[selectedTemplate] && (
        <div className="p-3 bg-slate-50 rounded-lg">
          <div className="flex items-start gap-2">
            <Badge variant="secondary" className="text-xs">
              {selectedCategoryData.title}
            </Badge>
          </div>
          <h4 className="font-medium text-slate-800 mt-2">
            {selectedCategoryData.queries[selectedTemplate].name}
          </h4>
          <p className="text-sm text-slate-600 mt-1">
            {selectedCategoryData.queries[selectedTemplate].description}
          </p>
        </div>
      )}
    </div>
  );
}