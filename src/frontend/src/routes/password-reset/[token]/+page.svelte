<script lang="ts">
    import type { PageData } from './$types';

    let { data }: { data: PageData } = $props();

    let password = $state('');
    let confirmPassword = $state('');
    let loading = $state(false);
    let error = $state('');
    let done = $state(false);

    async function handleSubmit() {
        if (password !== confirmPassword) {
            error = 'Passwörter stimmen nicht überein';
            return;
        }
        if (password.length < 12) {
            error = 'Passwort muss mindestens 12 Zeichen haben';
            return;
        }

        loading = true;
        error = '';

        const res = await fetch(`/api/settings/password-reset/${data.token}/confirm`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password, confirm_password: confirmPassword }),
        });

        if (res.ok) {
            done = true;
        } else {
            const body = await res.json();
            error = body.detail ?? 'Fehler beim Zurücksetzen';
            loading = false;
        }
    }
</script>

<div class="min-h-screen flex items-center justify-center bg-surface-50-950">
    <div class="card preset-outlined-surface-300-700 p-10 w-full max-w-sm flex flex-col gap-6">

        {#if done}
            <div class="flex flex-col gap-1 text-center">
                <h1 class="text-2xl font-bold">Passwort gesetzt</h1>
                <p class="text-surface-500-400 text-sm">Du kannst dich jetzt anmelden.</p>
            </div>
            <a href="/login" class="btn preset-filled-primary-500 w-full text-center">
                Zum Login
            </a>

        {:else}
            <div class="flex flex-col gap-1 text-center">
                <h1 class="text-2xl font-bold">Neues Passwort</h1>
                <p class="text-surface-500-400 text-sm">Mindestens 12 Zeichen.</p>
            </div>

            <input
                type="password"
                placeholder="Neues Passwort"
                bind:value={password}
                class="input"
            />
            <input
                type="password"
                placeholder="Passwort bestätigen"
                bind:value={confirmPassword}
                onkeydown={(e) => e.key === 'Enter' && handleSubmit()}
                class="input"
            />

            {#if error}
                <p class="text-error-500 text-sm text-center">{error}</p>
            {/if}

            <button
                onclick={handleSubmit}
                disabled={loading || !password || !confirmPassword}
                class="btn preset-filled-primary-500 w-full"
            >
                {#if loading}
                    Wird gesetzt...
                {:else}
                    Passwort setzen
                {/if}
            </button>
        {/if}

    </div>
</div>