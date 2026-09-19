<script lang="ts">
  import { onMount } from "svelte";
  import { modsStore } from "../stores/mods";
  import { localeStore } from "../stores/locale";
  import { t } from "../i18n";
  import { refreshMods } from "../api";
  import ModCard from "./ModCard.svelte";
  import ModDetailsModal from "./ModDetailsModal.svelte";

  export let onSaveMods: ((data: Record<string, boolean>) => void) | undefined = undefined;

  type ProfileItem = { name: string; state_count: number };

  let searchQuery = "";
  let typeFilter = "all";
  let categoryFilter = "all";
  let selectedModForDetails: string | null = null;
  let isRefreshing = false;
  let profiles: ProfileItem[] = [];
  let selectedProfile = "";
  let profileName = "";
  let profileBusy = false;
  let profileStatus = "";

  async function handleRefresh() {
    if (isRefreshing) return;
    isRefreshing = true;
    try {
      await refreshMods();
      await refreshProfiles();
    } finally {
      setTimeout(() => {
        isRefreshing = false;
      }, 300);
    }
  }

  async function refreshProfiles() {
    try {
      const api = window.pywebview?.api;
      if (!api?.get_profiles) return;
      const result = await api.get_profiles();
      profiles = Array.isArray(result) ? result : [];
      if (selectedProfile && !profiles.some((profile) => profile.name === selectedProfile)) {
        selectedProfile = "";
      }
    } catch (err) {
      console.error("Failed to refresh profiles:", err);
    }
  }

  onMount(() => {
    refreshProfiles();
  });

  $: mods = $modsStore;
  $: categories = Array.from(
    new Set(mods.map((mod) => (mod.category || mod.group || "").trim()).filter(Boolean)),
  ).sort((a, b) => a.localeCompare(b));

  function typeMatches(mod: (typeof mods)[number]) {
    if (typeFilter === "all") return true;
    if (typeFilter === "favorites") return Boolean(mod.favorite);
    return (mod.type || "standard") === typeFilter;
  }

  $: filteredMods = mods.filter((mod) => {
    const q = searchQuery.toLowerCase().trim();
    const display = (mod.display_name || mod.name).toLowerCase();
    const category = (mod.category || mod.group || "").trim();
    const searchMatches =
      !q ||
      display.includes(q) ||
      mod.name.toLowerCase().includes(q) ||
      category.toLowerCase().includes(q) ||
      (mod.source || "").toLowerCase().includes(q);
    const categoryMatches = categoryFilter === "all" || category === categoryFilter;
    return searchMatches && categoryMatches && typeMatches(mod);
  });

  async function toggleMod(modName: string, enabled: boolean) {
    const updated = mods.map((m) => (m.name === modName ? { ...m, enabled } : m));
    modsStore.set(updated);

    const payload: Record<string, boolean> = {};
    updated.forEach((m) => (payload[m.name] = m.enabled));
    if (onSaveMods) {
      onSaveMods(payload);
    } else if (window.pywebview?.api?.set_mods) {
      try {
        await window.pywebview.api.set_mods(payload);
      } catch (err) {
        console.error("Failed to save mods:", err);
      }
    }
  }

  async function toggleFavorite(modName: string, value: boolean) {
    const previous = mods;
    modsStore.set(mods.map((mod) => (mod.name === modName ? { ...mod, favorite: value } : mod)));
    try {
      const result = await window.pywebview?.api?.set_mod_favorite?.(modName, value);
      if (!result?.success) {
        modsStore.set(previous);
      }
    } catch (err) {
      modsStore.set(previous);
      console.error("Failed to update favorite:", err);
    }
  }

  async function saveCurrentProfile() {
    const name = profileName.trim();
    if (!name || profileBusy) return;
    profileBusy = true;
    try {
      const result = await window.pywebview?.api?.save_profile?.(name);
      if (result?.success) {
        selectedProfile = result.name || name;
        profileName = "";
        await refreshProfiles();
      }
    } finally {
      profileBusy = false;
    }
  }

  async function applySelectedProfile() {
    if (!selectedProfile || profileBusy) return;
    profileBusy = true;
    try {
      const result = await window.pywebview?.api?.apply_profile?.(selectedProfile);
      if (result?.success) await refreshMods();
    } finally {
      profileBusy = false;
    }
  }

  async function updateSelectedProfile() {
    if (!selectedProfile || profileBusy) return;
    profileBusy = true;
    profileStatus = "";
    try {
      const result = await window.pywebview?.api?.update_profile?.(selectedProfile);
      if (result?.success) {
        profileStatus = `Updated ${selectedProfile}.`;
        await refreshProfiles();
      } else {
        profileStatus = result?.error || "Profile update failed.";
      }
    } finally {
      profileBusy = false;
    }
  }

  async function exportProfiles() {
    if (profileBusy) return;
    profileBusy = true;
    profileStatus = "";
    try {
      const result = await window.pywebview?.api?.export_profiles?.();
      if (result?.success) {
        profileStatus = `Exported ${result.count ?? profiles.length} profile(s).`;
      } else if (!result?.cancelled) {
        profileStatus = result?.error || "Profile export failed.";
      }
    } finally {
      profileBusy = false;
    }
  }

  async function importProfiles() {
    if (profileBusy) return;
    profileBusy = true;
    profileStatus = "";
    try {
      const result = await window.pywebview?.api?.import_profiles?.();
      if (result?.success) {
        selectedProfile = result.applied_name || "";
        const detail = [
          `${result.added ?? 0} imported`,
          result.duplicates ? `${result.duplicates} duplicate(s)` : "",
          result.renamed ? `${result.renamed} renamed` : "",
          result.remapped ? `${result.remapped} mod ID(s) remapped` : "",
        ]
          .filter(Boolean)
          .join(", ");
        profileStatus = detail;
        await Promise.all([refreshProfiles(), refreshMods()]);
      } else if (!result?.cancelled) {
        profileStatus = result?.error || "Profile import failed.";
      }
    } finally {
      profileBusy = false;
    }
  }

  async function duplicateSelectedProfile() {
    if (!selectedProfile || profileBusy) return;
    profileBusy = true;
    try {
      const result = await window.pywebview?.api?.duplicate_profile?.(selectedProfile);
      if (result?.success) {
        selectedProfile = result.name || "";
        await refreshProfiles();
      }
    } finally {
      profileBusy = false;
    }
  }

  async function deleteSelectedProfile() {
    if (!selectedProfile || profileBusy) return;
    profileBusy = true;
    try {
      const result = await window.pywebview?.api?.delete_profile?.(selectedProfile);
      if (result?.success) {
        selectedProfile = "";
        await refreshProfiles();
      }
    } finally {
      profileBusy = false;
    }
  }

  function openDetails(modName: string) {
    selectedModForDetails = modName;
  }

  function closeDetails() {
    selectedModForDetails = null;
  }
</script>

<div class="mod-grid-container">
  <div class="grid-toolbar">
    <div class="toolbar-title">
      <h3>{$t("title_mods")}</h3>
      <span class="result-count">{filteredMods.length}/{mods.length}</span>
    </div>
    <div class="toolbar-controls">
      <button class="refresh-btn" class:refreshing={isRefreshing} on:click={handleRefresh} title={$t("button_refresh")}>
        <span class="refresh-icon" class:spin={isRefreshing}>↻</span>
        {$t("button_refresh")}
      </button>
      <div class="search-box">
        <input type="text" placeholder={$t("placeholder_search_mods")} bind:value={searchQuery} />
        {#if searchQuery}
          <button on:click={() => (searchQuery = "")}>
            {$t("button_clear")}
          </button>
        {/if}
      </div>
    </div>
  </div>

  <div class="library-toolbar">
    <select bind:value={typeFilter} aria-label="Mod source filter">
      <option value="all">All mods</option>
      <option value="standard">Standard</option>
      <option value="collection">Collections</option>
      <option value="d2pfx">D2PFX</option>
      <option value="vpk">VPK</option>
      <option value="favorites">Favorites</option>
    </select>

    <select bind:value={categoryFilter} aria-label="Mod category filter">
      <option value="all">All categories</option>
      {#each categories as category}
        <option value={category}>{category}</option>
      {/each}
    </select>

    <div class="profile-tools">
      <select bind:value={selectedProfile} aria-label="Saved profile">
        <option value="">Profiles…</option>
        {#each profiles as profile}
          <option value={profile.name}>{profile.name} ({profile.state_count})</option>
        {/each}
      </select>
      <button type="button" disabled={!selectedProfile || profileBusy} on:click={applySelectedProfile}>Apply</button>
      <button type="button" disabled={!selectedProfile || profileBusy} on:click={updateSelectedProfile}>Update</button>
      <button type="button" disabled={!selectedProfile || profileBusy} on:click={duplicateSelectedProfile}>Copy</button>
      <button type="button" disabled={!selectedProfile || profileBusy} on:click={deleteSelectedProfile}>Delete</button>
      <button type="button" disabled={profileBusy} on:click={importProfiles}>Import</button>
      <button type="button" disabled={profileBusy} on:click={exportProfiles}>Export</button>
      <input bind:value={profileName} maxlength="128" placeholder="Save current as…" aria-label="New profile name" />
      <button type="button" disabled={!profileName.trim() || profileBusy} on:click={saveCurrentProfile}>Save</button>
      {#if profileStatus}
        <span class="profile-status" title={profileStatus}>{profileStatus}</span>
      {/if}
    </div>
  </div>

  <div class="mod-grid">
    {#each filteredMods as mod (mod.name)}
      <ModCard
        name={mod.name}
        displayName={mod.display_name}
        enabled={mod.enabled}
        always={mod.always}
        untickable={mod.untickable}
        preview={mod.preview}
        favorite={Boolean(mod.favorite)}
        ontoggle={(value) => toggleMod(mod.name, value)}
        onFavorite={toggleFavorite}
        onDetails={openDetails}
      />
    {/each}
    {#if filteredMods.length === 0}
      <div class="empty-state">No mods match the current filters.</div>
    {/if}
  </div>

  <ModDetailsModal modName={selectedModForDetails} onClose={closeDetails} />
</div>

<style>
  .mod-grid-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-width: 0;
    overflow: hidden;
  }

  .grid-toolbar,
  .library-toolbar {
    display: flex;
    align-items: center;
    gap: 8px;
    min-height: 38px;
    padding: 6px 8px;
    border-bottom: 1px solid var(--border-color, #000);
    font-size: 13px;
    box-sizing: border-box;
  }

  .grid-toolbar {
    justify-content: space-between;
  }

  .library-toolbar {
    min-height: 40px;
    flex-wrap: wrap;
    background: var(--bg-secondary, #f4f4f4);
  }

  .toolbar-title {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .toolbar-title h3 {
    margin: 0;
    font-size: 15px;
    font-weight: bold;
    line-height: 1;
  }

  .result-count {
    color: var(--text-muted, #777);
    font-size: 11px;
  }

  .toolbar-controls,
  .search-box,
  .profile-tools {
    display: flex;
    gap: 6px;
    align-items: center;
    min-width: 0;
  }

  .profile-tools {
    flex: 1;
    justify-content: flex-end;
    flex-wrap: wrap;
  }

  .profile-status {
    max-width: 220px;
    overflow: hidden;
    color: var(--text-muted, #777);
    font-size: 10px;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  button,
  select,
  input {
    min-height: 26px;
    border: 1px solid var(--btn-border, var(--border-color, #000));
    background: var(--input-bg, var(--btn-bg, #fff));
    color: var(--input-text, var(--text-primary, #000));
    font-size: 12px;
    box-sizing: border-box;
  }

  button {
    padding: 0 8px;
    cursor: pointer;
  }

  button:disabled {
    cursor: default;
    opacity: 0.5;
  }

  select {
    max-width: 170px;
    padding: 0 5px;
  }

  input {
    padding: 0 7px;
  }

  .profile-tools input {
    width: 150px;
    min-width: 110px;
  }

  .refresh-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    line-height: 1;
  }

  button:hover:not(:disabled) {
    background: var(--btn-hover-bg, #f0f0f0);
    border-color: var(--btn-hover-border, var(--border-color, #000));
  }

  button:active:not(:disabled) {
    background: var(--btn-active-bg, #000);
    color: var(--btn-active-text, #fff);
  }

  .refresh-icon {
    display: inline-block;
    font-size: 14px;
    line-height: 1;
  }

  .refresh-icon.spin {
    animation: spin 0.6s linear infinite;
  }

  @keyframes spin {
    100% {
      transform: rotate(360deg);
    }
  }

  .search-box input {
    width: min(300px, 32vw);
    min-width: 160px;
  }

  .mod-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
    align-content: start;
    gap: 8px;
    padding: 8px;
    overflow-y: auto;
    flex: 1;
    min-height: 0;
  }

  .empty-state {
    grid-column: 1 / -1;
    padding: 24px 12px;
    color: var(--text-muted, #777);
    text-align: center;
  }

  @media (max-width: 960px) {
    .library-toolbar {
      align-items: stretch;
    }

    .profile-tools {
      flex-basis: 100%;
      justify-content: flex-start;
    }

    .profile-tools input {
      flex: 1;
    }
  }
</style>
