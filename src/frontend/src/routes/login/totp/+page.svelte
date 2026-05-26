<script lang="ts">
    let code = $state('');
    let loading = $state(false);
    let error = $state('');

    async function handleSubmit() {
        if (code.length !== 6) return;
        loading = true;
        error = '';

        const res = await fetch('/api/auth/totp/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code }),
        });

        if (res.ok) {
            window.location.href = '/dashboard';
        } else {
            const data = await res.json();
            error = data.detail ?? 'Ungültiger Code';
            loading = false;
        }
    }
</script>

<div class="min-h-screen flex items-center justify-center bg-surface-50-950">
    <div class="card preset-outlined-surface-300-700 p-10 w-full max-w-sm flex flex-col gap-6">
        <div class="flex flex-col gap-1 text-center">
            <h1 class="text-2xl font-bold">Zwei-Faktor-Authentifizierung</h1>
            <p class="text-surface-500-400 text-sm">Code aus der Authenticator-App eingeben</p>
        </div>

        <input
            type="text"
            inputmode="numeric"
            maxlength="6"
            placeholder="000000"
            bind:value={code}
            onkeydown={(e) => e.key === 'Enter' && handleSubmit()}
            class="input text-center text-2xl tracking-widest"
        />

        {#if error}
            <p class="text-error-500 text-sm text-center">{error}</p>
        {/if}

        <button
            onclick={handleSubmit}
            disabled={loading || code.length !== 6}
            class="btn preset-filled-primary-500 w-full"
        >
            {#if loading}
                Wird geprüft...
            {:else}
                Bestätigen
            {/if}
        </button>
    </div>
</div>