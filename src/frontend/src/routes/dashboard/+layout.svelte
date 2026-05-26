<script lang="ts">
    import Topbar from '$lib/components/Topbar.svelte';
    import Sidebar from '$lib/components/Sidebar.svelte';
    import SettingsModal from '$lib/components/SettingsModal.svelte';

    const { data, children } = $props();
    let settingsOpen = $state(false);
</script>

<SettingsModal bind:open={settingsOpen} />

<div class="flex flex-col h-screen">
    <Topbar servers={data.servers} currentServer={data.currentServer} />
    <div class="flex flex-1 overflow-hidden">
        <Sidebar currentServer={data.currentServer} onSettingsOpen={() => (settingsOpen = true)} />
        <main class="flex-1 overflow-auto p-6">
            {@render children()}
        </main>
    </div>
</div>