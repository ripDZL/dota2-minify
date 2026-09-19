<script lang="ts">
  import { t } from "../i18n";

  export let name: string;
  export let displayName: string = "";
  export let enabled: boolean;
  export let always: boolean = false;
  export let untickable: boolean = false;
  export let preview: string | null | undefined = undefined;
  export let favorite: boolean = false;
  export let category: string = "";
  export let source: string = "";
  export let modType: string = "standard";
  export let ontoggle: (value: boolean) => void;
  export let onFavorite: ((name: string, value: boolean) => void) | undefined = undefined;
  export let onDetails: ((name: string) => void) | undefined = undefined;

  $: effectiveName = displayName || name;
  $: typeLabel =
    modType === "d2pfx"
      ? "D2PFX"
      : modType === "vpk"
        ? "VPK"
        : modType === "collection"
          ? "Collection"
          : "Standard";
  $: metadata = Array.from(new Set([typeLabel, category, source].map((item) => item.trim()).filter(Boolean)));

  function toggle() {
    if (always || untickable) return;
    ontoggle(!enabled);
  }

  function handleCheckbox(e: Event) {
    e.stopPropagation();
    if (always || untickable) return;
    const input = e.currentTarget as HTMLInputElement;
    ontoggle(input.checked);
  }

  function handleDetails(e: MouseEvent) {
    e.stopPropagation();
    if (onDetails) onDetails(name);
  }

  function handleFavorite(e: MouseEvent) {
    e.stopPropagation();
    if (onFavorite) onFavorite(name, !favorite);
  }

  function handleRowClick() {
    if (always || untickable) {
      if (onDetails) onDetails(name);
      return;
    }
    toggle();
  }
</script>

<div
  class="mod-list-row"
  class:active={!untickable && (enabled || always)}
  class:has-preview={Boolean(preview)}
  class:locked={always || untickable}
  on:click={handleRowClick}
  role="button"
  tabindex="0"
  on:keydown={(e) => (e.key === "Enter" || e.key === " ") && handleRowClick()}
>
  <input
    class="state-checkbox"
    type="checkbox"
    checked={!untickable && (enabled || always)}
    disabled={always || untickable}
    aria-label={`Toggle ${effectiveName}`}
    on:change={handleCheckbox}
    on:click|stopPropagation
  />

  {#if preview}
    <button
      class="list-preview"
      type="button"
      title={`Open details for ${effectiveName}`}
      aria-label={`Open details for ${effectiveName}`}
      on:click={handleDetails}
    >
      <img src={preview} alt="" loading="lazy" decoding="async" />
    </button>
  {/if}

  <div class="list-copy">
    <div class="list-name" title={effectiveName}>{effectiveName}</div>
    {#if metadata.length}
      <div class="list-meta" title={metadata.join(" · ")}>{metadata.join(" · ")}</div>
    {/if}
  </div>

  <span class="state-label" class:selected={!untickable && (enabled || always)}>
    {always ? "Always" : untickable ? "Needs setup" : enabled ? "Selected" : "Off"}
  </span>

  {#if onFavorite}
    <button
      class="favorite-btn"
      class:favorite
      type="button"
      title={favorite ? "Remove from favorites" : "Add to favorites"}
      aria-label={favorite ? "Remove from favorites" : "Add to favorites"}
      on:click={handleFavorite}
    >
      {favorite ? "★" : "☆"}
    </button>
  {/if}

  {#if onDetails}
    <button class="details-btn" type="button" on:click={handleDetails}>
      {$t("button_details")}
    </button>
  {/if}
</div>

<style>
  .mod-list-row {
    min-height: 46px;
    display: grid;
    grid-template-columns: 22px minmax(0, 1fr) auto auto auto;
    align-items: center;
    gap: 7px;
    padding: 4px 7px;
    border-bottom: 1px solid var(--border-color, #000);
    background: var(--card-bg, var(--bg-primary, #fff));
    color: var(--text-primary, #000);
    cursor: pointer;
    box-sizing: border-box;
  }

  .mod-list-row.has-preview {
    grid-template-columns: 22px 64px minmax(0, 1fr) auto auto auto;
    min-height: 48px;
  }

  .mod-list-row:last-child {
    border-bottom: 0;
  }

  .mod-list-row:hover:not(.locked) {
    background: var(--btn-hover-bg, var(--bg-secondary, #f0f0f0));
  }

  .mod-list-row.active {
    box-shadow: inset 3px 0 0 var(--accent, #17bebe);
  }

  .mod-list-row.locked {
    cursor: default;
    opacity: 0.72;
  }

  .state-checkbox {
    width: 15px;
    height: 15px;
    margin: 0;
    accent-color: var(--accent, #17bebe);
    cursor: pointer;
  }

  .state-checkbox:disabled {
    cursor: not-allowed;
  }

  .list-preview {
    width: 64px;
    height: 36px;
    padding: 0;
    border: 1px solid var(--card-border, var(--border-color, #000));
    background: var(--card-preview-bg, #f0f0f0);
    overflow: hidden;
    cursor: zoom-in;
  }

  .list-preview img {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: cover;
  }

  .list-copy {
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 2px;
  }

  .list-name {
    overflow: hidden;
    color: var(--text-primary, #000);
    font-size: 12px;
    font-weight: 600;
    line-height: 15px;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .list-meta {
    overflow: hidden;
    color: var(--text-muted, #777);
    font-size: 10px;
    line-height: 12px;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .state-label {
    min-width: 54px;
    color: var(--text-muted, #777);
    font-size: 10px;
    text-align: right;
    white-space: nowrap;
  }

  .state-label.selected {
    color: var(--accent, #17bebe);
  }

  .favorite-btn,
  .details-btn {
    min-height: 26px;
    border: 1px solid var(--btn-border, var(--border-color, #000));
    background: var(--btn-bg, #fff);
    color: var(--btn-text, #000);
    cursor: pointer;
  }

  .favorite-btn {
    width: 28px;
    padding: 0;
    color: var(--text-muted, #777);
    font-size: 16px;
  }

  .favorite-btn.favorite {
    color: var(--accent, #17bebe);
  }

  .details-btn {
    min-width: 58px;
    padding: 0 7px;
    font-size: 11px;
  }

  .favorite-btn:hover,
  .details-btn:hover {
    background: var(--btn-hover-bg, #f0f0f0);
    border-color: var(--btn-hover-border, var(--border-color, #000));
  }

  @media (max-width: 960px) {
    .mod-list-row {
      gap: 5px;
      padding: 3px 5px;
    }

    .mod-list-row.has-preview {
      grid-template-columns: 20px 56px minmax(0, 1fr) auto auto;
    }

    .list-preview {
      width: 56px;
      height: 32px;
    }

    .state-label {
      display: none;
    }

    .details-btn {
      min-width: 52px;
      padding: 0 5px;
    }
  }
</style>
