<script lang="ts">
  export let isOpen = false;
  export let points: Array<{
    id: string;
    created: string;
    completed: string;
    status: string;
    reason: string;
    selected_mod_count: number;
  }> = [];
  export let busy = false;
  export let onRestore: (id: string) => void;
  export let onCancel: () => void;

  let selected = "";
  $: if (isOpen && !points.some((point) => point.id === selected)) {
    selected = points[0]?.id || "";
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Escape" && !busy) onCancel();
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isOpen}
  <div class="overlay" role="presentation">
    <section class="dialog" role="dialog" aria-modal="true" aria-label="Restore points">
      <header>
        <div>
          <h2>Restore points</h2>
          <p>Restore Minify-managed output and the saved mod selection.</p>
        </div>
        <button type="button" class="close" on:click={onCancel} disabled={busy} aria-label="Close">×</button>
      </header>

      <div class="body">
        {#if points.length}
          <label for="restore-point">Saved restore point</label>
          <select id="restore-point" bind:value={selected} disabled={busy}>
            {#each points as point}
              <option value={point.id}>{point.created || point.id} — {point.status || "created"}</option>
            {/each}
          </select>

          {#each points.filter((point) => point.id === selected) as point}
            <div class="details">
              <div><strong>Status:</strong> {point.status || "created"}</div>
              <div><strong>Reason:</strong> {point.reason || "pre-patch"}</div>
              <div><strong>Selected mods:</strong> {point.selected_mod_count}</div>
              {#if point.completed}<div><strong>Completed:</strong> {point.completed}</div>{/if}
            </div>
          {/each}
        {:else}
          <p class="muted">No restore points are available yet.</p>
        {/if}
      </div>

      <footer>
        <button type="button" on:click={onCancel} disabled={busy}>Close</button>
        <button
          type="button"
          class="primary"
          on:click={() => selected && onRestore(selected)}
          disabled={!selected || busy}
        >
          {busy ? "Restoring…" : "Restore selected"}
        </button>
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
    width: min(620px, calc(100vw - 36px));
    max-height: min(480px, calc(100vh - 36px));
    display: flex;
    flex-direction: column;
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
  p {
    margin: 0;
  }

  header p,
  .muted {
    color: var(--text-muted, #777);
  }

  .body {
    min-height: 120px;
    overflow-y: auto;
    padding: 12px;
  }

  label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
  }

  select {
    width: 100%;
    min-height: 28px;
    border: 1px solid var(--input-border, #000);
    background: var(--input-bg, #fff);
    color: var(--input-text, #000);
  }

  .details {
    display: grid;
    gap: 5px;
    margin-top: 12px;
    padding: 9px;
    border: 1px solid var(--card-border, var(--border-color, #000));
    background: var(--bg-secondary, #f4f4f4);
  }

  button {
    min-height: 27px;
    padding: 0 10px;
    border: 1px solid var(--btn-border, #000);
    background: var(--btn-bg, #fff);
    color: var(--btn-text, #000);
    cursor: pointer;
  }

  .close {
    width: 28px;
    min-width: 28px;
    padding: 0;
    font-size: 19px;
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

  @media (max-width: 700px) {
    .overlay {
      padding: 8px;
    }

    .dialog {
      width: calc(100vw - 16px);
      max-height: calc(100vh - 16px);
    }
  }
</style>
