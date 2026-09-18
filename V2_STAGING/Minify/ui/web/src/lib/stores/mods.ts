import { writable } from "svelte/store";

export interface ModItem {
  name: string;
  display_name?: string;
  enabled: boolean;
  always?: boolean;
  untickable?: boolean;
  preview?: string | null;
  group?: string;
  category?: string;
  source?: string;
  type?: "standard" | "collection" | "d2pfx" | "vpk";
  nested?: boolean;
  favorite?: boolean;
}

export const modsStore = writable<ModItem[]>([]);
