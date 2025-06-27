export interface Asset {
  id: number;
  model: string;
  asset_name: string;
  asset_tag: string;
  category: string;
  manufacturer: string | null;
  serial: string | null;
  eol: string | null;
  warranty: string | null;
  location: string | null;
  status: string;
  model_no: string | null;
  company: string | null;
  purchase_date: string;
  created_at: string;
}

