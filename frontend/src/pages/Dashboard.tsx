import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";            
import { Building2, Laptop, Activity, TrendingUp, Laptop2, GpuIcon, PartyPopperIcon, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { AssetChart } from '../components/AssetChart';
import { StatusPieChart } from '../components/StatusPieChart';
import {TrendChart} from '../components/TrendChart';
import {AssetTable} from '../components/AssetTable';
import { useAssets } from '../hooks/useAssets';
import { LaptopExpirationChart } from '../components/LaptopExpirationChart';
import { ExportModal } from '../components/ExportModal';


// -----------------------------------------------------------------------

export default function Dashboard() {
  const {
    data: assets = [],
    isLoading,
    isError,
    error,
  } = useAssets();

  const [company,      setCompany]      = useState('all');
  const [manufacturer, setManufacturer] = useState('all');
  const [category,     setCategory]     = useState('all');
  const [model,        setModel]        = useState('all');
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);


  /* ---------- derived state ---------- */
  const filtered = useMemo(
    () =>
      assets.filter(
        a =>
          (company      === 'all' || a.company      === company) &&
          (manufacturer === 'all' || a.manufacturer === manufacturer) &&
          (category     === 'all' || a.category     === category) &&
          (model        === 'all' || a.model        === model)
      ),
    [assets, company, manufacturer, category, model]
  );

  const companies      = useMemo(() => [...new Set(assets.map(a => a.company))].filter((c): c is string => c != null),      [assets]);
  const manufacturers  = useMemo(() => [...new Set(assets.map(a => a.manufacturer))].filter((m): m is string => m != null), [assets]);
  const categories     = useMemo(() => [...new Set(assets.map(a => a.category))].filter((c): c is string => c != null),     [assets]);
  const models  = useMemo(() => [...new Set(assets.map(a => a.model))].filter((m): m is string => m != null), [assets]);

  const stats = {
    total:    filtered.length,
    active:   filtered.filter(a => a.status === 'Active').length,
    'Pending Rebuild': filtered.filter(a => a.status === 'Pending Rebuild').length,
    stock:    filtered.filter(a => a.status === 'Stock').length,
  };

  /* ---------- UI ---------- */
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {isLoading && <p>Loading Assets...</p>}
      {isError && <p className='text-red-600'>Error: {error.message}</p>}
      <div className="container mx-auto p-6 space-y-8">
        {/* Header */}
        <header className="flex flex-col space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="p-2 bg-blue-600 rounded-lg">
                <Building2 className="h-6 w-6 text-white" />
              </span>
              <div>
                <h1 className="text-3xl font-bold text-slate-900">
                  Asset Management Dashboard
                </h1>
                <p className="text-slate-600">
                  Monthly asset tracking and analytics
                </p>
              </div>
            </div>
            <Button 
              onClick={() => setIsExportModalOpen(true)} 
              className="flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export PDF
            </Button>
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-4 p-4 bg-white rounded-lg shadow-sm border">
            <FilterSelect
              label="Company"
              value={company}
              onChange={setCompany}
              options={companies}
            />
            <FilterSelect
              label="Manufacturer"
              value={manufacturer}
              onChange={setManufacturer}
              options={manufacturers}
            />
            <FilterSelect
              label="Category"
              value={category}
              onChange={setCategory}
              options={categories}
            />
            <FilterSelect
              label="Model"
              value={model}
              onChange={setModel}
              options={models}
            />
          </div>
        </header>

        {/* Summary cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <SummaryCard title="Total Assets" count={stats.total}    icon={GpuIcon} border="border-l-blue-500"   />
          <SummaryCard title="Active"        count={stats.active}   icon={Activity}  border="border-l-green-500"  />
          <SummaryCard title="Pending Rebuild"   count={stats['Pending Rebuild']} icon={TrendingUp}border="border-l-orange-500" />
          <SummaryCard title="In Stock"      count={stats.stock}    icon={Laptop}    border="border-l-purple-500"/>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartCard title="Assets by Category" icon={Laptop2}>
            <AssetChart data={filtered} />
          </ChartCard>
          <ChartCard title="Status Distribution" icon={Activity}>
            <StatusPieChart data={filtered} />
          </ChartCard>
        </div>

        <ChartCard title="Monthly Asset Trends: (newly added devices by initial status)" icon={TrendingUp}>
          <TrendChart data={filtered} />
        </ChartCard>

        <ChartCard title="Warranty Expiration Trends" icon={PartyPopperIcon}>
          <LaptopExpirationChart data={filtered} />
        </ChartCard>

        {/* Table */}
        <ChartCard title="Asset Details" icon={Laptop}>
          <AssetTable data={filtered} />
        </ChartCard>
      </div>

      {/* Export Modal */}
      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        assets={filtered}
        currentFilters={{
          company: company !== 'all' ? company : undefined,
          manufacturer: manufacturer !== 'all' ? manufacturer : undefined,
          category: category !== 'all' ? category : undefined,
          model: model !== 'all' ? model : undefined,
        }}
      />
    </div>
  );
}

/* ----- tiny helpers -------------------------------------------------- */
function FilterSelect({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: string[];
}) {
  return (
    <div className="flex items-center gap-2">
      <label className="text-sm font-medium text-slate-700">{label}:</label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger className="w-32">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All</SelectItem>
          {options.map(opt => (
            <SelectItem key={opt} value={opt}>
              {opt}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

function SummaryCard({
  title,
  count,
  icon: Icon,
  border,
}: {
  title: string;
  count: number;
  icon: typeof GpuIcon;
  border: string;
}) {
  return (
    <Card className={`border-l-4 ${border} hover:shadow-lg transition-shadow`}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-slate-600">{title}</CardTitle>
        <Icon className="h-4 w-4" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-slate-900">{count}</div>
      </CardContent>
    </Card>
  );
}

function ChartCard({
  title,
  icon: Icon,
  children,
}: {
  title: string;
  icon: typeof Building2;
  children: React.ReactNode;
}) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="p-1 bg-slate-100 rounded">
            <Icon className="h-4 w-4" />
          </span>
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}