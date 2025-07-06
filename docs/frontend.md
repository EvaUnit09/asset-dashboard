# Frontend Documentation

## Overview

The frontend is a modern React application built with **React 19**, **TypeScript**, and **Vite**. It provides a comprehensive dashboard for asset management with interactive charts, filtering capabilities, and responsive design.

## Technology Stack

- **React 19.1.0** - Latest React with concurrent features
- **TypeScript 5.8.3** - Type-safe JavaScript
- **Vite 6.3.5** - Fast build tool and dev server
- **Tailwind CSS 4.1.10** - Utility-first CSS framework
- **Radix UI** - Accessible component primitives
- **Recharts 3.0.0** - Composable charting library
- **TanStack Query 5.81.2** - Data fetching and caching
- **Axios 1.10.0** - HTTP client
- **Lucide React 0.523.0** - Beautiful icons

## Project Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── ui/              # Reusable UI components
│   │   │   ├── badge.tsx
│   │   │   ├── card.tsx
│   │   │   ├── select.tsx
│   │   │   └── table.tsx
│   │   ├── AssetChart.tsx   # Asset category distribution chart
│   │   ├── AssetTable.tsx   # Asset data table
│   │   ├── LaptopExpirationChart.tsx # Warranty expiration chart
│   │   ├── StatusPieChart.tsx # Status distribution chart
│   │   └── TrendChart.tsx   # Monthly trends chart
│   ├── hooks/
│   │   └── useAssets.ts     # Custom hook for asset data
│   ├── lib/
│   │   ├── api.ts           # API client configuration
│   │   └── utils.ts         # Utility functions
│   ├── types/
│   │   └── asset.ts         # TypeScript type definitions
│   ├── App.tsx              # Main application component
│   ├── App.css              # Global styles
│   ├── main.tsx             # Application entry point
│   └── index.css            # Tailwind CSS imports
├── public/                  # Static assets
├── package.json             # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
├── vite.config.ts           # Vite configuration
└── components.json          # Radix UI configuration
```

## Core Components

### Main Dashboard (`App.tsx`)

The main dashboard component provides:
- Asset filtering by company, manufacturer, category, and model
- Summary statistics cards
- Interactive charts and visualizations
- Detailed asset table

```typescript
export default function DashboardPage() {
  const { data: assets = [], isLoading, isError } = useAssets();
  
  // Filter state
  const [company, setCompany] = useState('all');
  const [manufacturer, setManufacturer] = useState('all');
  const [category, setCategory] = useState('all');
  const [model, setModel] = useState('all');
  
  // Derived state for filtering
  const filtered = useMemo(() => 
    assets.filter(a => 
      (company === 'all' || a.company === company) &&
      (manufacturer === 'all' || a.manufacturer === manufacturer) &&
      (category === 'all' || a.category === category) &&
      (model === 'all' || a.model === model)
    ), [assets, company, manufacturer, category, model]
  );
}
```

### Chart Components

#### AssetChart
Displays asset distribution by category using a bar chart.

```typescript
export function AssetChart({ data }: { data: Asset[] }) {
  const chartData = useMemo(() => {
    const categoryCount = data.reduce((acc, asset) => {
      const category = asset.category || 'Unknown';
      acc[category] = (acc[category] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    return Object.entries(categoryCount).map(([name, value]) => ({
      name,
      value
    }));
  }, [data]);
}
```

#### StatusPieChart
Shows asset status distribution using a pie chart.

#### TrendChart
Displays monthly asset trends with line charts.

#### LaptopExpirationChart
Visualizes warranty expiration trends over time.

### Data Table (`AssetTable.tsx`)

Provides a sortable and filterable table of all assets:

```typescript
export function AssetTable({ data }: { data: Asset[] }) {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Asset Name</TableHead>
            <TableHead>Asset Tag</TableHead>
            <TableHead>Company</TableHead>
            <TableHead>Category</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Warranty Expires</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((asset) => (
            <TableRow key={asset.id}>
              <TableCell>{asset.asset_name}</TableCell>
              <TableCell>{asset.asset_tag}</TableCell>
              <TableCell>{asset.company}</TableCell>
              <TableCell>{asset.category}</TableCell>
              <TableCell>
                <Badge variant={getStatusVariant(asset.status)}>
                  {asset.status}
                </Badge>
              </TableCell>
              <TableCell>{formatDate(asset.warranty_expires)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
```

## Data Management

### Custom Hooks (`useAssets.ts`)

Uses TanStack Query for efficient data fetching and caching:

```typescript
export function useAssets() {
  return useQuery({
    queryKey: ['assets'],
    queryFn: async (): Promise<Asset[]> => {
      const response = await api.get('/assets');
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  });
}
```

### API Client (`lib/api.ts`)

Configured Axios instance for API communication:

```typescript
import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

## TypeScript Types

### Asset Interface (`types/asset.ts`)

```typescript
export interface Asset {
  id?: number;
  asset_name?: string;
  asset_tag?: string;
  model_no?: string;
  model?: string;
  company?: string;
  category?: string;
  manufacturer?: string;
  serial?: string;
  warranty?: string;
  warranty_expires?: string;
  location?: string;
  department?: string;
  status?: string;
  created_at?: string;
}
```

## Styling and UI

### Tailwind CSS

The application uses Tailwind CSS 4.1 for styling:

- **Utility-first approach** for rapid development
- **Responsive design** with mobile-first approach
- **Custom color palette** for consistent branding
- **Dark mode support** (when implemented)

### Radix UI Components

Accessible component primitives:
- **Select** - Dropdown selection components
- **Card** - Content containers
- **Badge** - Status indicators
- **Table** - Data display

### Custom Components

Reusable UI components in `components/ui/`:
- Consistent styling and behavior
- TypeScript support
- Accessibility features
- Responsive design

## State Management

### Local State
- Filter states (company, manufacturer, category, model)
- UI state (loading, error states)
- Form states (when implemented)

### Server State
- Asset data via TanStack Query
- Automatic caching and background updates
- Error handling and retry logic

## Performance Optimizations

### React Optimizations
- **useMemo** for expensive calculations
- **useCallback** for stable function references
- **React.memo** for component memoization
- **Code splitting** with lazy loading

### Data Optimizations
- **TanStack Query** for intelligent caching
- **Pagination** for large datasets
- **Debounced search** for filtering
- **Virtual scrolling** for large tables (when needed)

## Development

### Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  }
}
```

### Development Server

```bash
npm run dev
# Starts development server at http://localhost:5173
```

### Building for Production

```bash
npm run build
# Creates optimized build in dist/ directory
```

## Configuration

### Vite Configuration (`vite.config.ts`)

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

### TypeScript Configuration

Strict TypeScript configuration for type safety:
- **Strict mode** enabled
- **Path mapping** for clean imports
- **ESLint integration** for code quality

## Testing

### Testing Strategy
- **Unit tests** for utility functions
- **Component tests** with React Testing Library
- **Integration tests** for API interactions
- **E2E tests** for critical user flows

### Testing Setup
```bash
# Install testing dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest

# Run tests
npm test
```

## Accessibility

### ARIA Support
- **Semantic HTML** elements
- **ARIA labels** and descriptions
- **Keyboard navigation** support
- **Screen reader** compatibility

### Color and Contrast
- **WCAG AA** compliance
- **High contrast** mode support
- **Color-blind friendly** palettes

## Browser Support

- **Modern browsers** (Chrome, Firefox, Safari, Edge)
- **ES2020** features
- **CSS Grid** and **Flexbox**
- **Progressive enhancement** approach

## Deployment

### Build Process
1. **Type checking** with TypeScript
2. **Code bundling** with Vite
3. **Asset optimization** and compression
4. **Static file generation**

### Docker Configuration
Multi-stage Dockerfile for production builds:
- **Build stage** for dependencies and compilation
- **Production stage** for optimized runtime
- **Nginx** for static file serving

### Environment Variables
```bash
VITE_API_URL=http://localhost:8000/api
VITE_APP_TITLE=Asset Management
```

## Future Enhancements

### Planned Features
- **Real-time updates** with WebSocket
- **Advanced filtering** and search
- **Export functionality** (CSV, PDF)
- **User authentication** and authorization
- **Dark mode** toggle
- **Mobile app** with React Native

### Performance Improvements
- **Service Worker** for offline support
- **Image optimization** and lazy loading
- **Bundle splitting** for faster loading
- **CDN integration** for static assets 