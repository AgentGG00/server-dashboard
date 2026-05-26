<script lang="ts">
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';

    const { data, children } = $props();

    function switchServer(event: Event) {
        const id = (event.target as HTMLSelectElement).value;
        document.cookie = `last_server=${id}; path=/`;
        goto(`/dashboard/${id}`);
    }
</script>

{@render children()}