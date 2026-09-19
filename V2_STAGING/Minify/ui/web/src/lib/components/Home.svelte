<script lang="ts">
  import { onMount, tick } from "svelte";
  import { modsStore } from "../stores/mods";

  export let isPatching = false;
  export let logs: Array<{ text: string; type: string; timestamp?: string }> = [];
  export let patchStatusText = "Ready";
  export let onPatch: () => void;
  export let onRestore: () => void;
  export let onRescan: () => void;
  export let onOpenTerminal: () => void;

  let activityElement: HTMLElement | null = null;
  let version = "v21.4-hardening";
  let restoreCount = 0;
  let latestRestore = "";

  $: selectedCount = $modsStore.filter((mod) => mod.enabled || mod.always).length;
  $: totalCount = $modsStore.length;
  $: statusText = isPatching ? patchStatusText || "Patching…" : "Ready";
  $: recentLogs = logs.slice(-120);
  $: if (recentLogs.length) {
    scrollActivityToBottom();
  }

  async function scrollActivityToBottom() {
    await tick();
    if (activityElement) {
      activityElement.scrollTop = activityElement.scrollHeight;
    }
  }

  function cleanAnsi(text: string): string {
    if (!text) return "";
    return text.replace(/\x1b\[[0-9;]*m/g, "");
  }

  async function refreshStatus() {
    try {
      const api = window.pywebview?.api;
      const [currentVersion, points] = await Promise.all([
        api?.get_version?.(),
        api?.get_restore_points?.(),
      ]);
      if (typeof currentVersion === "string" && currentVersion.trim()) {
        version = currentVersion.trim();
      }
      if (Array.isArray(points)) {
        restoreCount = points.length;
        latestRestore = points[0]?.created || "";
      }
    } catch {
      // Dashboard status is best-effort; primary actions remain available.
    }
  }

  async function rescan() {
    await onRescan();
    await refreshStatus();
  }

  onMount(refreshStatus);
</script>

<div class="home-shell">
  <section class="home-surface" aria-label="Minify control panel">
    <div class="home-title-row">
      <div>
        <div class="eyebrow">CONTROL PANEL</div>
        <h1>Minify {version}</h1>
      </div>
      <div class="status" class:busy={isPatching}>
        <span class="status-dot"></span>
        {statusText}
      </div>
    </div>

    <div class="metrics">
      <div class="metric">
        <span class="metric-label">Selected mods</span>
        <strong>{selectedCount}</strong>
        <span class="metric-sub">of {totalCount} discovered</span>
      </div>
      <div class="metric">
        <span class="metric-label">Restore points</span>
        <strong>{restoreCount}</strong>
        <span class="metric-sub">{latestRestore ? `latest ${latestRestore}` : "none yet"}</span>
      </div>
      <div class="metric">
        <span class="metric-label">Patch state</span>
        <strong>{statusText}</strong>
        <span class="metric-sub">transactional restore enabled</span>
      </div>
    </div>

    <section class="activity-panel" aria-label="Live terminal activity">
      <div class="activity-header">
        <div>
          <strong>Live terminal</strong>
          <span>{isPatching ? "patch output" : "recent activity"}</span>
        </div>
        <button type="button" class="terminal-link" on:click={onOpenTerminal}>Open full terminal</button>
      </div>
      <div class="activity-body" bind:this={activityElement} aria-live="polite">
        {#if recentLogs.length === 0}
          <div class="activity-empty">No activity yet. Patch and maintenance output will appear here.</div>
        {:else}
          {#each recentLogs as log}
            {#if log.type === "separator"}
              <hr />
            {:else}
              <div class="activity-row {log.type || 'info'}">
                {#if log.timestamp}<span class="activity-time">{log.timestamp}</span>{/if}
                <span>{cleanAnsi(log.text)}</span>
              </div>
            {/if}
          {/each}
        {/if}
      </div>
    </section>

    <div class="action-panel">
      <div>
        <strong>Deployment</strong>
        <p>Review conflicts, create a restore point, then build the selected mod set.</p>
      </div>
      <div class="actions">
        <button type="button" on:click={onRestore} disabled={isPatching}>Restore</button>
        <button type="button" on:click={rescan} disabled={isPatching}>Rescan mods</button>
        <button type="button" class="primary" on:click={onPatch} disabled={isPatching}>
          {isPatching ? "Patching…" : "Review & Patch"}
        </button>
      </div>
    </div>
  </section>
</div>

<style>
  .home-shell {
    height: 100%;
    overflow-y: auto;
    padding: 14px;
    background: var(--workspace-bg, var(--bg-primary, #fff));
  }

  .home-surface {
    display: flex;
    min-height: 100%;
    flex-direction: column;
    gap: 12px;
    padding: 14px;
    border: 1px solid var(--border-color, #000);
    background: var(--bg-secondary, #f4f4f4);
  }

  .home-title-row,
  .action-panel,
  .actions,
  .status {
    display: flex;
    align-items: center;
  }

  .home-title-row,
  .action-panel {
    justify-content: space-between;
    gap: 14px;
  }

  .eyebrow {
    color: var(--accent-gold, var(--text-muted, #777));
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
  }

  h1 {
    margin: 2px 0 0;
    font-size: 22px;
    font-weight: 650;
  }

  .status {
    gap: 7px;
    min-width: 90px;
    justify-content: flex-end;
    font-weight: 600;
  }

  .status-dot {
    width: 9px;
    height: 9px;
    border: 1px solid var(--border-color, #000);
    background: var(--accent, #7ac143);
  }

  .status.busy .status-dot {
    background: var(--accent-gold, #ffc30f);
  }

  .metrics {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    border-top: 1px solid var(--border-color, #000);
    border-bottom: 1px solid var(--border-color, #000);
  }

  .metric {
    display: flex;
    min-width: 0;
    flex-direction: column;
    gap: 3px;
    padding: 12px;
    border-right: 1px solid var(--border-color, #000);
    background: var(--card-bg, var(--bg-primary, #fff));
  }

  .metric:last-child {
    border-right: 0;
  }

  .metric-label,
  .metric-sub,
  .action-panel p {
    color: var(--text-muted, #777);
    font-size: 11px;
  }

  .metric strong {
    overflow: hidden;
    font-size: 18px;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .activity-panel {
    display: flex;
    flex: 1;
    min-height: 190px;
    flex-direction: column;
    border: 1px solid var(--border-color, #000);
    background: var(--terminal-bg, #111);
  }

  .activity-header {
    min-height: 34px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 5px 7px;
    border-bottom: 1px solid var(--border-color, #000);
    background: var(--bg-tertiary, var(--bg-primary, #fff));
  }

  .activity-header > div {
    min-width: 0;
    display: flex;
    align-items: baseline;
    gap: 7px;
  }

  .activity-header span {
    color: var(--text-muted, #777);
    font-size: 10px;
  }

  .terminal-link {
    min-height: 24px;
    flex-shrink: 0;
    padding: 0 8px;
    font-size: 11px;
  }

  .activity-body {
    flex: 1;
    min-height: 150px;
    overflow-y: auto;
    padding: 7px;
    background: var(--terminal-bg, #111);
    color: var(--terminal-text, #eee);
    font-family: monospace;
    font-size: 11px;
    line-height: 1.35;
    user-select: text;
  }

  .activity-row {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    gap: 7px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }

  .activity-row.error {
    color: var(--log-error, #ff6b6b);
    font-weight: 700;
  }

  .activity-row.warning {
    color: var(--log-warning, #ffc30f);
  }

  .activity-row.success {
    color: #7ac143;
    font-weight: 700;
  }

  .activity-time {
    color: var(--text-muted, #888);
  }

  .activity-empty {
    color: var(--text-muted, #888);
  }

  .activity-body hr {
    border: 0;
    border-top: 1px solid var(--border-color, #555);
    margin: 4px 0;
  }

  .action-panel {
    padding-top: 12px;
    border-top: 1px solid var(--border-color, #000);
  }

  .action-panel p {
    margin: 3px 0 0;
  }

  .actions {
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 7px;
  }

  button {
    min-height: 30px;
    padding: 0 12px;
    border: 1px solid var(--btn-border, #000);
    background: var(--btn-bg, #fff);
    color: var(--btn-text, #000);
    cursor: pointer;
  }

  button.primary {
    background: var(--accent, #7ac143);
    color: var(--accent-text, #000);
    border-color: var(--accent, #7ac143);
    font-weight: 700;
  }

  button:disabled {
    opacity: 0.55;
    cursor: default;
  }

  @media (max-width: 960px) {
    .home-shell {
      padding: 8px;
    }

    .home-surface {
      gap: 8px;
      padding: 10px;
    }

    .metrics {
      grid-template-columns: 1fr;
    }

    .metric {
      display: grid;
      grid-template-columns: 120px minmax(0, 1fr) minmax(0, 1.5fr);
      align-items: center;
      padding: 7px 8px;
      border-right: 0;
      border-bottom: 1px solid var(--border-color, #000);
    }

    .metric:last-child {
      border-bottom: 0;
    }

    .metric strong {
      font-size: 14px;
    }

    .activity-panel {
      min-height: 150px;
    }

    .activity-body {
      min-height: 110px;
    }

    .action-panel {
      align-items: flex-start;
    }
  }
</style>
