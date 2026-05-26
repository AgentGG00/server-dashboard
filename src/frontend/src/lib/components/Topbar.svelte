<script lang="ts">
    import { goto } from '$app/navigation';

    const { servers, currentServer } = $props();

    function switchServer(event: Event) {
        const id = (event.target as HTMLSelectElement).value;
        document.cookie = `last_server=${id}; path=/; max-age=${60 * 60 * 24 * 90}`;
        goto(`/dashboard/${id}`);
    }
</script>

<header class="border-b border-surface-300-700 flex items-center justify-between px-4 py-2">
    <select
        onchange={switchServer}
        value={currentServer}
        class="select preset-outlined-surface-300-700"
    >
        {#each servers as server}
            <option value={server.id}>{server.name}</option>
        {/each}
    </select>

    <span class="font-semibold text-lg">Dashboard</span>

    <div class="flex items-center gap-3">
        <span class="text-sm text-surface-500-400">
            {currentServer?.ip_v4 ?? '—'}<br />
            {currentServer?.ip_v6 ?? '—'}
        </span>
        <button class="btn preset-filled-error-500 btn-sm">Shutdown</button>
        <button class="btn preset-tonal-warning btn-sm">Reboot</button>
        <a href="/dashboard/{currentServer}/settings" class="btn preset-tonal-surface btn-sm">Settings</a>
    </div>
</header>