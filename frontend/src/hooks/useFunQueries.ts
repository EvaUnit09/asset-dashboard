import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

interface QueryTemplate {
  name: string;
  description: string;
}

interface QueryCategory {
  title: string;
  description: string;
  queries: Record<string, QueryTemplate>;
}

interface QueryResult {
  success: boolean;
  template_id: string;
  template_name: string;
  data: any[];
  count: number;
}

export function useFunQueries() {
  const [templates, setTemplates] = useState<Record<string, QueryCategory> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [data, setData] = useState<QueryResult | null>(null);
  const [error, setError] = useState<Error | null>(null);

  // Load templates on mount
  useEffect(() => {
    const loadTemplates = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/fun-queries/templates`);
        setTemplates(response.data);
      } catch (err) {
        console.error('Failed to load query templates:', err);
      }
    };

    loadTemplates();
  }, []);

  const executeQuery = async (templateId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_BASE_URL}/fun-queries/execute/${templateId}`);
      setData(response.data);
    } catch (err: any) {
      setError(new Error(err.response?.data?.detail || 'Failed to execute query'));
      setData(null);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    templates,
    executeQuery,
    isLoading,
    data,
    error
  };
}