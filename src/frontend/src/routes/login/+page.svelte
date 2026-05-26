<script lang="ts">
    let loading = $state(false);

    async function handleLogin() {
        loading = true;
        window.location.href = '/auth/google';
    }
</script>

<div class="min-h-screen flex items-center justify-center bg-surface-50-950">
    <div class="card preset-outlined-surface-300-700 p-10 w-full max-w-sm flex flex-col gap-6">
        <div class="flex flex-col gap-1 text-center">
            <h1 class="text-2xl font-bold">Server Dashboard</h1>
            <p class="text-surface-500-400 text-sm">Anmeldung erforderlich</p>
        </div>

        <button
            onclick={handleLogin}
            disabled={loading}
            class="btn preset-filled-primary-500 w-full"
        >
            {#if loading}
                Wird weitergeleitet...
            {:else}
                Mit Google anmelden
            {/if}
        </button>
    </div>
</div>