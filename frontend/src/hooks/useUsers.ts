import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import type { User } from "@/types/user";

export const useUsers = () =>
    useQuery<User[], Error>({
        queryKey: ["users"],
        queryFn: async () => (await api.get<User[]>("/users")).data,
        staleTime: 5 * 60 * 1000,        // cache 5 min
    });
    