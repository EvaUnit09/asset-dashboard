// src/hooks/useAssets.ts
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import type { Asset } from "@/types/asset"

export const useAssets = () =>
  useQuery<Asset[], Error>({
    queryKey: ["assets"],
    queryFn: async () => (await api.get<Asset[]>("/assets")).data,
    staleTime: 5 * 60 * 1000,        // cache 5 min
  });
