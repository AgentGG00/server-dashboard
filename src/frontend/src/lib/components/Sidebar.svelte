<script lang="ts">
    import { page } from '$app/stores';

    const { currentServer, onSettingsOpen } = $props();

    const navItems = [
        { label: 'Overview', path: '' },
        { label: 'Systemd', path: 'systemd' },
        { label: 'Firewall', path: 'firewall' },
        { label: 'Apache', path: 'apache' },
        { label: 'Docker', path: 'docker' },
    ];
</script>

<nav class="w-48 border-r border-surface-300-700 flex flex-col gap-1 p-3 h-full">
    <div class="flex flex-col gap-1 flex-1">
        {#each navItems as item}
            <a
                href="/dashboard/{currentServer}/{item.path}"
                class="btn {$page.url.pathname.endsWith(item.path || currentServer) ? 'preset-filled-primary-500' : 'preset-tonal-surface'} justify-start"
            >
                {item.label}
            </a>
        {/each}
    </div>

    <div class="flex flex-col gap-1 border-t border-surface-300-700 pt-3">
        <button
            onclick={onSettingsOpen}
            class="btn preset-tonal-surface justify-start"
        >
            Einstellungen
        </button>
    </div>
</nav>