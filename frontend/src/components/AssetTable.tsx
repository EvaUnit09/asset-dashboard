import { useState, useMemo } from "react";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Asset } from "@/types/asset";

interface Props {
  data: Asset[];
  selectable?: boolean;
  selectedId?: number | null;
  onSelectAsset?: (id: number | null) => void;
}

const ITEMS_PER_PAGE = 20;

/* --- styling helpers -------------------------------------------------- */
const statusColor = (s: string) => {
  switch (s.toLowerCase()) {
    case "active":   return "bg-green-100 text-green-800 hover:bg-green-200";
    case "deployed": return "bg-orange-100 text-orange-800 hover:bg-orange-200";
    case "stock":    return "bg-purple-100 text-purple-800 hover:bg-purple-200";
    default:         return "bg-red-100 text-red-800 hover:bg-red-200";
  }
};
/* ---------------------------------------------------------------------- */

export const AssetTable = ({ data, selectable, selectedId, onSelectAsset }: Props) => {
  const [page,       setPage]       = useState(1);
  const [query,      setQuery]      = useState("");



  /* 1 ─ filter by search term */
  const filtered = useMemo(() => {
    if (!query) return data;
    const q = query.toLowerCase();
    return data.filter((a) =>
      [
        a.asset_name,
        a.serial,
        a.model,
        a.category,
        a.manufacturer,
        a.company,
        a.location,
        a.status,
        a.warranty_expires
      ]
        .filter(Boolean)
        .some((field) => field!.toLowerCase().includes(q)),
    );
  }, [data, query]);

  /* 2 ─ paginate */
  const pageCount      = Math.max(1, Math.ceil(filtered.length / ITEMS_PER_PAGE));
  const currentPage    = Math.min(page, pageCount);               // safety guard
  const start          = (currentPage - 1) * ITEMS_PER_PAGE;
  const paginatedSlice = filtered.slice(start, start + ITEMS_PER_PAGE);

  /* 3 ─ handlers */
  const next  = () => setPage((p) => Math.min(p + 1, pageCount));
  const prev  = () => setPage((p) => Math.max(p - 1, 1));
  const jump  = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    setPage(1);                    // reset to first page on new search
  };

  return (
    <div className="space-y-4">
      {/* ── search input ─────────────────────────────────────────────── */}
      <input
        type="text"
        placeholder="Quick search…"
        value={query}
        onChange={jump}
        className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      {/* ── data table ──────────────────────────────────────────────── */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-50">
              {selectable && (
                <TableHead className="w-12">
                  {/* Empty header for checkbox column */}
                </TableHead>
              )}
              {[
                "Asset Name",
                "Category",
                "Manufacturer",
                "Model",
                "Serial",
                "Company",
                "Location",
                "Status",
                "Warranty Expires"
              ].map((h) => (
                <TableHead key={h} className="font-semibold">
                  {h}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>

          <TableBody>
            {paginatedSlice.map((a) => (
              <TableRow
                key={a.id}
                className="hover:bg-slate-50 transition-colors">
                  {selectable && (
                    <TableCell>
                      <input
                        type="checkbox"
                        checked={selectedId === a.id}
                        onChange={() => onSelectAsset?.(selectedId === a.id ? null : a.id)}
                        className="w-4 h-4 cursor-pointer"
                        />
                    </TableCell>
                  )}
                <TableCell className="font-medium">{a.asset_name}</TableCell>
                <TableCell>
                  <Badge variant="outline" className="capitalize">
                    {a.category}
                  </Badge>
                </TableCell>
                <TableCell>{a.manufacturer}</TableCell>
                <TableCell className="text-slate-600">{a.model}</TableCell>
                <TableCell className="text-slate-600">{a.serial}</TableCell>
                <TableCell>
                  <Badge variant="secondary" className="capitalize">
                    {a.company}
                  </Badge>
                </TableCell>
                <TableCell className="text-slate-600">{a.location}</TableCell>
                <TableCell>
                  <Badge className={`capitalize ${statusColor(a.status)}`}>
                    {a.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-slate-600">{a.warranty_expires}</TableCell>
              </TableRow>
            ))}

            {!paginatedSlice.length && (
              <TableRow>
                <TableCell colSpan={8} className="py-8 text-center text-sm">
                  No assets match your search.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* ── pagination controls ─────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <button
          onClick={prev}
          disabled={currentPage === 1}
          className="rounded-md border px-3 py-1 text-sm disabled:opacity-50"
        >
          Previous
        </button>

        <span className="text-sm">
          Page <strong>{currentPage}</strong> of {pageCount}
        </span>

        <button
          onClick={next}
          disabled={currentPage === pageCount}
          className="rounded-md border px-3 py-1 text-sm disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
};

