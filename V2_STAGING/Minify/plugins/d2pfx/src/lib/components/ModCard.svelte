<script lang="ts">
  import type { D2Mod } from "../types";
  import { t } from "../i18n";

  export let mod: D2Mod;
  export let installed: boolean = false;
  export let inProgress: boolean = false;
  export let enabled: boolean = false;
  export let onInstall: (mod: D2Mod) => void;
  export let onUninstall: (mod: D2Mod) => void;
  export let onToggleEnabled: ((mod: D2Mod, enabled: boolean) => void) | undefined = undefined;
  export let onPreview: ((url: string, title: string) => void) | undefined = undefined;

  let previewSrc: string | null = null;
  let lastPrimaryPreview: string | null = null;
  let fallbackAttempted = false;

  $: {
    const primary = mod.preview_url || null;
    if (primary !== lastPrimaryPreview) {
      lastPrimaryPreview = primary;
      previewSrc = primary;
      fallbackAttempted = false;
    }
  }

  function formatAuthors(author: any, sender: any): string {
    const parts: string[] = [];
    if (author) {
      if (Array.isArray(author)) parts.push(`By: ${author.join(", ")}`);
      else parts.push(`By: ${author}`);
    }
    if (sender) {
      if (Array.isArray(sender)) parts.push(`Sender: ${sender.join(", ")}`);
      else parts.push(`Sender: ${sender}`);
    }
    return parts.join(" | ");
  }

  function formatTags(tags: any): string {
    if (!tags) return "";
    if (Array.isArray(tags)) return tags.join(", ");
    if (typeof tags === "object")
      return Object.keys(tags)
        .filter((k) => tags[k])
        .join(", ");
    return String(tags);
  }

  function handleImageError() {
    if (!fallbackAttempted && mod.preview_fallback_url && mod.preview_fallback_url !== previewSrc) {
      fallbackAttempted = true;
      previewSrc = mod.preview_fallback_url;
      return;
    }
    previewSrc = null;
  }
</script>

<div class="mod-card" class:active={installed && enabled}>
  <div class="preview-box">
    {#if previewSrc}
      <button
        type="button"
        class="preview-img-btn"
        on:click|stopPropagation={() =>
          onPreview &&
          previewSrc &&
          onPreview(previewSrc, `${mod.name}${mod.label ? ` (${mod.label})` : ""}`)}
        title={$t("title_click_to_preview")}
        aria-label={`Preview image for ${mod.name}`}
      >
        <img
          src={previewSrc}
          alt={mod.name}
          loading="lazy"
          decoding="async"
          class="preview-img"
          on:error={handleImageError}
        />
      </button>
    {:else}
      <span class="no-preview">{$t("label_no_preview")}</span>
    {/if}
  </div>

  <div class="card-details">
    <div class="mod-title">
      {mod.name}{mod.label ? ` (${mod.label})` : ""}
    </div>

    {#if formatAuthors(mod.author, mod.sender)}
      <div class="mod-meta">
        {formatAuthors(mod.author, mod.sender)}
      </div>
    {/if}

    {#if mod.updated_label}
      <div class="mod-updated">
        {mod.updated_label}
      </div>
    {/if}

    {#if formatTags(mod.tags)}
      <div class="mod-tags">
        {formatTags(mod.tags)}
      </div>
    {/if}
  </div>

  <div class="card-actions">
    {#if installed}
      <label class="checkbox-container" title={enabled ? $t("label_disable_mod") : $t("label_enable_mod")}>
        <input
          type="checkbox"
          checked={enabled}
          disabled={inProgress}
          on:change={(e) => onToggleEnabled && onToggleEnabled(mod, e.currentTarget.checked)}
        />
      </label>
      <button class="install-btn installed" disabled={inProgress} on:click={() => onUninstall(mod)}>
        {inProgress ? $t("button_removing") : $t("button_remove")}
      </button>
    {:else if inProgress}
      <label class="checkbox-container" title={enabled ? $t("label_disable_mod") : $t("label_enable_mod")}>
        <input
          type="checkbox"
          checked={enabled}
          on:change={(e) => onToggleEnabled && onToggleEnabled(mod, e.currentTarget.checked)}
        />
      </label>
      <button class="install-btn" disabled>
        {$t("button_installing")}
      </button>
    {:else}
      <button class="install-btn" disabled={inProgress} on:click={() => onInstall(mod)}>
        {$t("button_install")}
      </button>
    {/if}
  </div>
</div>

<style>
  .mod-card {
    border: 1px solid var(--card-border, #000);
    padding: 8px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: var(--card-bg, #fff);
    color: var(--text-primary, #000);
    transition: border-color 0.15s ease;
  }

  .mod-card.active {
    border-color: var(--accent, #17bebe);
  }

  .preview-box {
    width: 100%;
    aspect-ratio: 3 / 2;
    min-height: 110px;
    max-height: 180px;
    border: 1px solid var(--card-border, #000);
    background: var(--card-preview-bg, #f8f8f8);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    margin-bottom: 6px;
  }

  .preview-img-btn {
    width: 100%;
    height: 100%;
    padding: 0;
    margin: 0;
    border: none;
    background: transparent;
    cursor: zoom-in;
    display: block;
  }

  .preview-img-btn:hover .preview-img {
    opacity: 0.85;
  }

  .preview-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }

  .no-preview {
    font-size: 10px;
    color: var(--text-muted, #888);
  }

  .card-details {
    flex: 1;
    margin-bottom: 6px;
  }

  .mod-title {
    font-weight: bold;
    font-size: 12px;
    margin-bottom: 2px;
    line-height: 1.2;
    color: var(--text-primary, inherit);
  }

  .mod-meta {
    font-size: 10px;
    color: var(--text-secondary, #555);
    margin-bottom: 2px;
  }

  .mod-updated {
    font-size: 10px;
    color: #c6975c;
    margin-bottom: 2px;
  }

  .mod-tags {
    font-size: 9px;
    color: var(--accent, #0055bb);
    word-break: break-word;
  }

  .card-actions {
    margin-top: 4px;
    display: flex;
    gap: 4px;
  }

  .install-btn {
    flex: 1;
    min-width: 0;
    padding: 4px;
    border: 1px solid var(--btn-border, #000);
    background: var(--btn-bg, #fff);
    color: var(--btn-text, #000);
    font-weight: bold;
    cursor: pointer;
    font-size: 11px;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .install-btn:hover {
    background: var(--btn-hover-bg, #f0f0f0);
    border-color: var(--btn-hover-border, var(--border-color, #000));
  }

  .install-btn.installed {
    background: var(--accent, #17bebe);
    color: var(--accent-text, #000);
    border-color: var(--accent, #17bebe);
  }

  .install-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .checkbox-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    border: 1px solid var(--input-border, #000);
    background: var(--input-bg, #fff);
    cursor: pointer;
    flex-shrink: 0;
  }

  .checkbox-container input[type="checkbox"] {
    cursor: pointer;
    margin: 0;
    width: 14px;
    height: 14px;
    accent-color: var(--accent, #17bebe);
  }

  .checkbox-container:has(input:disabled) {
    opacity: 0.5;
    cursor: not-allowed;
  }

  @media (max-width: 960px) {
    .mod-card {
      display: grid;
      grid-template-columns: 112px minmax(0, 1fr) 120px;
      align-items: center;
      gap: 8px;
      padding: 6px;
    }

    .preview-box {
      width: 112px;
      height: 66px;
      min-height: 66px;
      max-height: 66px;
      aspect-ratio: auto;
      margin: 0;
    }

    .card-details {
      min-width: 0;
      margin: 0;
    }

    .mod-title,
    .mod-meta,
    .mod-tags {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .card-actions {
      margin: 0;
      align-self: stretch;
      align-items: center;
    }
  }
</style>
