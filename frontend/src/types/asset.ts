export interface Asset {
  id: number;
  model: string;
  asset_name: string;
  asset_tag: string;
  category: string;
  manufacturer: string | null;
  serial: string | null;
  warranty: string | null;
  location: string | null;
  status: string;
  model_no: string | null;
  company: string | null;
  department: string | null;
  assigned_user_id: number | null;
  created_at: string;
  warranty_expires: string;
}

