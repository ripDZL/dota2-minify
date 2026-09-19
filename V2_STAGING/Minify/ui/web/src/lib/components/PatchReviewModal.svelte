<script lang="ts">
  export let isOpen = false;
  export let preview:
    | {
        selected_mods: Array<{ id: string; name: string }>;
        counts: { critical: number; possible: number; expected: number; pairs: number };
        estimated_entries: number;
        compatibility_rules: Array<{ id: string; title: string; summary: string }>;
        planned_resource_actions: Array<{
          path: string;
          mod: string;
          classification: string;
          recommended_action: string;
        }>;
        conflicts: Array<{
          a_name: string;
          b_name: string;
          severity: string;
          classification: string;
          auto_fix: boolean;
          count: number;
          examples: string[];
        }>;
      }
    | null = null;
  export let onConfirm: () => void;
  export let onCancel: () => void;

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Escape") onCancel();
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isOpen}
  <div class="overlay" role="presentation">
    <section class="dialog" role="dialog" aria-modal="true" aria-label="Patch review">
      <header>
        <div>
          <h2>Patch review</h2>
          <p>Review indexed overlaps and automatic compatibility actions before patching.</p>
        </div>
        <button type="button" class="close" on:click={onCancel} aria-label="Close">×</button>
      </header>

      {#if preview}
        <div class="summary">
          <span>{preview.selected_mods.length} selected mods</span>
          <span>{preview.estimated_entries} indexed resources</span>
          <span class:critical={preview.counts.critical > 0}>{preview.counts.pairs} overlap pairs</span>
          <span class:critical={preview.counts.critical > 0}>{preview.counts.critical} critical</span>
        </div>

        <div class="body">
          {#if preview.compatibility_rules.length}
            <section class="review-section">
              <h3>Automatic compatibility</h3>
              {#each preview.compatibility_rules as rule}
                <article class="rule">
                  <strong>{rule.title}</strong>
                  <div>{rule.summary}</div>
                </article>
              {/each}
              {#each preview.planned_resource_actions as action}
                <div class="action-row">
                  <code>{action.path}</code>
                  <span>{action.recommended_action}</span>
                </div>
              {/each}
            </section>
          {/if}

          <section class="review-section">
            <h3>Resource overlaps</h3>
            {#if preview.conflicts.length === 0}
              <p class="muted">No indexed output-path overlaps were found.</p>
            {:else}
              {#each preview.conflicts as conflict}
                <article class="conflict" class:critical={conflict.severity === "critical"}>
                  <div class="conflict-title">
                    <strong>{conflict.a_name}</strong>
                    <span>↔</span>
                    <strong>{conflict.b_name}</strong>
                    <span class="badge">{conflict.count}</span>
                  </div>
                  <div class="meta">
                    {conflict.severity} · {conflict.classification}{conflict.auto_fix ? " · auto-fix" : ""}
                  </div>
                  {#each conflict.examples.slice(0, 4) as path}
                    <code class="path">{path}</code>
                  {/each}
                </article>
              {/each}
            {/if}
          </section>
        </div>
      {:else}
        <div class="body"><p class="muted">Patch preview is unavailable.</p></div>
      {/if}

      <footer>
        <button type="button" on:click={onCancel}>Cancel</button>
        <button type="button" class="primary" on:click={onConfirm} disabled={!preview}>Create restore point & patch</button>
      </footer>
    </section>
  </div>
{/if}

<style>
  .overlay {
    position: fixed;
    inset: 0;
    z-index: 12000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 18px;
    background: rgba(0, 0, 0, 0.58);
  }

  .dialog {
    display: flex;
    flex-direction: column;
    width: min(820px, calc(100vw - 36px));
    max-height: min(620px, calc(100vh - 36px));
    border: 1px solid var(--border-color, #000);
    background: var(--bg-primary, #fff);
    color: var(--text-primary, #000);
  }

  header,
  footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 10px 12px;
    border-bottom: 1px solid var(--border-color, #000);
  }

  footer {
    justify-content: flex-end;
    border-top: 1px solid var(--border-color, #000);
    border-bottom: 0;
  }

  h2,
  h3,
  p {
    margin: 0;
  }

  header p,
  .muted,
  .meta {
    color: var(--text-muted, #777);
  }

  .close {
    width: 28px;
    min-width: 28px;
    padding: 0;
    font-size: 19px;
  }

  .summary {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 14px;
    padding: 7px 12px;
    border-bottom: 1px solid var(--border-color, #000);
    background: var(--bg-secondary, #f4f4f4);
    font-size: 12px;
  }

  .critical {
    color: var(--log-error, #c00);
  }

  .body {
    min-height: 0;
    overflow-y: auto;
    padding: 10px 12px;
  }

  .review-section {
    display: flex;
    flex-direction: column;
    gap: 7px;
    margin-bottom: 14px;
  }

  .rule,
  .conflict {
    padding: 8px;
    border: 1px solid var(--card-border, var(--border-color, #000));
    background: var(--card-bg, var(--bg-primary, #fff));
  }

  .conflict.critical {
    border-color: var(--log-error, #c00);
  }

  .conflict-title {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }

  .badge {
    margin-left: auto;
    padding: 1px 5px;
    border: 1px solid var(--border-color, #000);
    font-size: 11px;
  }

  .meta {
    margin: 4px 0;
    font-size: 11px;
  }

  .action-row {
    display: grid;
    grid-template-columns: minmax(180px, 0.75fr) 1fr;
    gap: 8px;
    align-items: start;
    font-size: 11px;
  }

  code.path,
  .action-row code {
    display: block;
    overflow-wrap: anywhere;
    font-size: 11px;
  }

  button {
    min-height: 27px;
    padding: 0 10px;
    border: 1px solid var(--btn-border, #000);
    background: var(--btn-bg, #fff);
    color: var(--btn-text, #000);
    cursor: pointer;
  }

  button.primary {
    background: var(--accent, #17bebe);
    color: var(--accent-text, #000);
    border-color: var(--accent, #17bebe);
    font-weight: 600;
  }

  button:disabled {
    opacity: 0.5;
    cursor: default;
  }

  @media (max-width: 760px) {
    .overlay {
      padding: 8px;
    }

    .dialog {
      width: calc(100vw - 16px);
      max-height: calc(100vh - 16px);
    }

    .action-row {
      grid-template-columns: 1fr;
    }
  }
</style>
