<script lang="ts">
    import { page } from '$app/stores';

    const { currentServer } = $props();

    const navItems = [
        { label: 'Overview', path: '' },
        { label: 'Systemd', path: 'systemd' },
        { label: 'Firewall', path: 'firewall' },
        { label: 'Apache', path: 'apache' },
        { label: 'Docker', path: 'docker' },
    ];
</script>

<nav class="w-48 border-r border-surface-300-700 flex flex-col gap-1 p-3">
    {#each navItems as item}
        
            href="/dashboard/{currentServer}/{item.path}"
            class="btn {$page.url.pathname.endsWith(item.path || currentServer) ? 'preset-filled-primary-500' : 'preset-tonal-surface'} justify-start"
        >
            {item.label}
        </a>
    {/each}
</nav>