<script lang="ts">
  import { onMount } from "svelte";
  import { modsStore } from "../stores/mods";
  import { localeStore } from "../stores/locale";
  import { t } from "../i18n";
  import { refreshMods } from "../api";
  import ModCard from "./ModCard.svelte";
  import ModListRow from "./ModListRow.svelte";
  import ModDetailsModal from "./ModDetailsModal.svelte";

  export let onSaveMods: ((data: Record<string, boolean>) => void) | undefined = undefined;

  type ProfileItem = { name: string; state_count: number };
  type ViewMode = "list" | "cards";

  const MOD_VIEW_KEY = "minify.mod-library.view-mode";

  let viewMode: ViewMode = "list";
  let collapsedGroups: Record<string, boolean> = {};
  let searchQuery = "";
  let typeFilter = "all";
  let categoryFilter = "all";
  let stateFilter = "all";
  let sortMode = "name-asc";
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
    try {
      const saved = window.localStorage.getItem(MOD_VIEW_KEY);
      if (saved === "list" || saved === "cards") {
        viewMode = saved;
      }
    } catch (err) {
      console.debug("Mod Library view preference is unavailable:", err);
    }
    refreshProfiles();
  });

  function setViewMode(mode: ViewMode) {
    viewMode = mode;
    try {
      window.localStorage.setItem(MOD_VIEW_KEY, mode);
    } catch (err) {
      console.debug("Could not persist Mod Library view preference:", err);
    }
  }

  function listGroupKey(mod: any): string {
    const type = String(mod?.type || "standard").trim().toLowerCase();
    if (type === "collection") {
      const group = String(mod?.group || mod?.category || "Collections").trim() || "Collections";
      return `collection::${group}`;
    }
    return type || "standard";
  }

  function listGroupLabel(key: string): string {
    if (key === "standard") return "Standard Mods";
    if (key === "d2pfx") return "D2PFX Mods";
    if (key === "vpk") return "VPK Mods";
    if (key.startsWith("collection::")) return key.slice("collection::".length) || "Collections";
    return key ? `${key.charAt(0).toUpperCase()}${key.slice(1)} Mods` : "Other Mods";
  }

  function listGroupRank(key: string): number {
    if (key === "standard") return 0;
    if (key.startsWith("collection::")) return 1;
    if (key === "d2pfx") return 2;
    if (key === "vpk") return 3;
    return 4;
  }

  function modsInListGroup(key: string) {
    return filteredMods.filter((mod) => listGroupKey(mod) === key);
  }

  function selectedInListGroup(key: string): number {
    return modsInListGroup(key).filter((mod) => mod.enabled).length;
  }

  function toggleListGroup(key: string) {
    collapsedGroups = { ...collapsedGroups, [key]: !collapsedGroups[key] };
  }

  $: mods = $modsStore;
  $: categories = Array.from(
    new Set(mods.map((mod) => (mod.category || mod.group || "").trim()).filter(Boolean)),
  ).sort((a, b) => a.localeCompare(b));

  function typeMatches(mod: (typeof mods)[number]) {
    if (typeFilter === "all") return true;
    if (typeFilter === "favorites") return Boolean(mod.favorite);
    return (mod.type || "standard") === typeFilter;
  }

  function stateMatches(mod: (typeof mods)[number]) {
    if (stateFilter === "selected") return Boolean(mod.enabled);
    if (stateFilter === "unselected") return !mod.enabled;
    return true;
  }

  function sortMods(items: typeof mods) {
    const originalOrder = new Map(mods.map((mod, index) => [mod.name, index]));
    return [...items].sort((a, b) => {
      const aName = (a.display_name || a.name).toLowerCase();
      const bName = (b.display_name || b.name).toLowerCase();
      const aCategory = (a.category || a.group || "").toLowerCase();
      const bCategory = (b.category || b.group || "").toLowerCase();
      const aSource = (a.source || "").toLowerCase();
      const bSource = (b.source || "").toLowerCase();

      if (sortMode === "name-desc") return bName.localeCompare(aName);
      if (sortMode === "category") return aCategory.localeCompare(bCategory) || aName.localeCompare(bName);
      if (sortMode === "enabled-first")
        return Number(Boolean(b.enabled)) - Number(Boolean(a.enabled)) || aName.localeCompare(bName);
      if (sortMode === "disabled-first")
        return Number(Boolean(a.enabled)) - Number(Boolean(b.enabled)) || aName.localeCompare(bName);
      if (sortMode === "source") return aSource.localeCompare(bSource) || aName.localeCompare(bName);
      if (sortMode === "file-priority")
        return (originalOrder.get(a.name) ?? 999999) - (originalOrder.get(b.name) ?? 999999);
      return aName.localeCompare(bName);
    });
  }

  $: filteredMods = sortMods(
    mods.filter((mod) => {
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
      return searchMatches && categoryMatches && typeMatches(mod) && stateMatches(mod);
    }),
  );
  $: selectedCount = mods.filter((mod) => mod.enabled).length;
  $: listGroupKeys = Array.from(new Set(filteredMods.map(listGroupKey))).sort(
    (a, b) => listGroupRank(a) - listGroupRank(b) || listGroupLabel(a).localeCompare(listGroupLabel(b)),
  );

  async function persistModStates(updated: typeof mods) {
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

  async function toggleMod(modName: string, enabled: boolean) {
    const updated = mods.map((m) => (m.name === modName ? { ...m, enabled } : m));
    await persistModStates(updated);
  }

  async function setAllSelectable(value: boolean) {
    const updated = mods.map((mod) =>
      mod.always || mod.untickable ? mod : { ...mod, enabled: value },
    );
    await persistModStates(updated);
  }

  async function invertSelectable() {
    const updated = mods.map((mod) =>
      mod.always || mod.untickable ? mod : { ...mod, enabled: !mod.enabled },
    );
    await persistModStates(updated);
  }

  function expandAllGroups() {
    collapsedGroups = Object.fromEntries(listGroupKeys.map((key) => [key, false]));
  }

  function collapseAllGroups() {
    collapsedGroups = Object.fromEntries(listGroupKeys.map((key) => [key, true]));
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
      <span class="result-count">{selectedCount} selected · {filteredMods.length}/{mods.length} shown</span>
    </div>
    <div class="toolbar-controls">
      <div class="view-toggle" role="group" aria-label="Mod Library view">
        <button
          type="button"
          class:active={viewMode === "list"}
          aria-pressed={viewMode === "list"}
          on:click={() => setViewMode("list")}
          title="Compact legacy-style list view"
        >
          List
        </button>
        <button
          type="button"
          class:active={viewMode === "cards"}
          aria-pressed={viewMode === "cards"}
          on:click={() => setViewMode("cards")}
          title="Preview card view"
        >
          Cards
        </button>
      </div>
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

    <select bind:value={stateFilter} aria-label="Mod state filter">
      <option value="all">All states</option>
      <option value="selected">Selected</option>
      <option value="unselected">Unselected</option>
    </select>

    <select bind:value={sortMode} aria-label="Mod sort order">
      <option value="name-asc">Name A–Z</option>
      <option value="name-desc">Name Z–A</option>
      <option value="category">Category</option>
      <option value="enabled-first">Enabled first</option>
      <option value="disabled-first">Disabled first</option>
      <option value="source">Source</option>
      <option value="file-priority">File priority</option>
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

  {#if viewMode === "cards"}
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
  {:else}
    <div class="selection-tools" aria-label="Mod selection controls">
      <span class="selection-label">Selection</span>
      <button type="button" on:click={() => setAllSelectable(true)}>Select all</button>
      <button type="button" on:click={() => setAllSelectable(false)}>Clear</button>
      <button type="button" on:click={invertSelectable}>Invert</button>
      <span class="selection-separator"></span>
      <button type="button" on:click={expandAllGroups}>Expand all</button>
      <button type="button" on:click={collapseAllGroups}>Collapse all</button>
    </div>

    <div class="mod-list">
      {#each listGroupKeys as groupKey}
        {@const groupMods = modsInListGroup(groupKey)}
        <section class="list-group">
          <button
            type="button"
            class="list-group-header"
            aria-expanded={!collapsedGroups[groupKey]}
            on:click={() => toggleListGroup(groupKey)}
          >
            <span class="group-disclosure">{collapsedGroups[groupKey] ? "▶" : "▼"}</span>
            <span class="group-name">{listGroupLabel(groupKey)}</span>
            <span class="group-count">{selectedInListGroup(groupKey)}/{groupMods.length} selected</span>
          </button>

          {#if !collapsedGroups[groupKey]}
            <div class="list-group-rows">
              {#each groupMods as mod (mod.name)}
                <ModListRow
                  name={mod.name}
                  displayName={mod.display_name}
                  enabled={mod.enabled}
                  always={mod.always}
                  untickable={mod.untickable}
                  preview={mod.preview}
                  favorite={Boolean(mod.favorite)}
                  category={mod.category || mod.group || ""}
                  source={mod.source || ""}
                  modType={mod.type || "standard"}
                  ontoggle={(value) => toggleMod(mod.name, value)}
                  onFavorite={toggleFavorite}
                  onDetails={openDetails}
                />
              {/each}
            </div>
          {/if}
        </section>
      {/each}

      {#if filteredMods.length === 0}
        <div class="empty-state">No mods match the current filters.</div>
      {/if}
    </div>
  {/if}

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
  .profile-tools,
  .view-toggle {
    display: flex;
    gap: 6px;
    align-items: center;
    min-width: 0;
  }

  .view-toggle {
    gap: 0;
  }

  .view-toggle button {
    min-width: 52px;
    border-right-width: 0;
  }

  .view-toggle button:last-child {
    border-right-width: 1px;
  }

  .view-toggle button.active {
    background: var(--accent, #17bebe);
    border-color: var(--accent, #17bebe);
    color: var(--accent-text, #000);
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

  .selection-tools {
    min-height: 34px;
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 4px 8px;
    border-bottom: 1px solid var(--border-color, #000);
    background: var(--bg-secondary, #f4f4f4);
  }

  .selection-label {
    margin-right: 3px;
    color: var(--text-muted, #777);
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
  }

  .selection-tools button {
    min-height: 24px;
    padding: 0 8px;
    font-size: 11px;
  }

  .selection-separator {
    width: 1px;
    height: 18px;
    margin: 0 2px;
    background: var(--border-color, #000);
  }

  .mod-list {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding: 6px 8px 10px;
  }

  .list-group {
    margin-bottom: 6px;
    border: 1px solid var(--border-color, #000);
    background: var(--card-bg, var(--bg-primary, #fff));
  }

  .list-group-header {
    width: 100%;
    min-height: 28px;
    display: grid;
    grid-template-columns: 18px minmax(0, 1fr) auto;
    align-items: center;
    gap: 5px;
    padding: 3px 7px;
    border: 0;
    border-bottom: 1px solid var(--border-color, #000);
    background: var(--bg-tertiary, var(--bg-secondary, #ececec));
    color: var(--text-primary, #000);
    text-align: left;
  }

  .list-group-header[aria-expanded="false"] {
    border-bottom: 0;
  }

  .group-disclosure {
    font-size: 10px;
    color: var(--accent, #17bebe);
    text-align: center;
  }

  .group-name {
    min-width: 0;
    overflow: hidden;
    font-size: 12px;
    font-weight: 700;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .group-count {
    color: var(--text-muted, #777);
    font-size: 10px;
    white-space: nowrap;
  }

  .list-group-rows {
    display: flex;
    flex-direction: column;
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

    .toolbar-controls {
      gap: 4px;
    }

    .view-toggle button {
      min-width: 46px;
      padding: 0 5px;
    }

    .selection-tools {
      flex-wrap: wrap;
      padding: 4px 5px;
    }

    .selection-label {
      display: none;
    }

    .selection-tools button {
      padding: 0 6px;
    }

    .mod-list {
      padding: 5px;
    }
  }
</style>
