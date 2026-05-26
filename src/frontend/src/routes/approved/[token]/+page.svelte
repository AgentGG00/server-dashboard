<script lang="ts">
    import type { PageData } from './$types';
    import { page } from '$app/stores';

    let { data }: { data: PageData } = $props();

    let step = $derived(($page.url.searchParams.get('step') ?? 'oauth') as 'oauth' | 'totp' | 'otp');
    let loading = $state(false);
    let error = $state('');
    let totpCode = $state('');
    let otpCode = $state('');

    function startOAuth() {
        loading = true;
        window.location.href = `/api/auth/google?approve_token=${data.token}`;
    }

    async function submitTotp() {
        if (totpCode.length !== 6) return;
        loading = true;
        error = '';

        const res = await fetch(`/api/auth/totp/verify-approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: totpCode, approve_token: data.token }),
        });

        if (res.ok) {
            window.location.href = `/approve/${data.token}?step=otp`;
        } else {
            const body = await res.json();
            error = body.detail ?? 'Ungültiger Code';
            loading = false;
        }
    }

    async function submitOtp() {
        if (otpCode.length !== 6) return;
        loading = true;
        error = '';

        const res = await fetch(`/api/auth/approve/${data.token}/confirm`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ otp_code: otpCode }),
        });

        if (res.ok) {
            window.location.href = '/login?approved=true';
        } else {
            const body = await res.json();
            error = body.detail ?? 'Ungültiger Code';
            loading = false;
        }
    }
</script>

<div class="min-h-screen flex items-center justify-center bg-surface-50-950">
    <div class="card preset-outlined-surface-300-700 p-10 w-full max-w-sm flex flex-col gap-6">

        <div class="flex flex-col gap-1 text-center">
            <h1 class="text-2xl font-bold">Neues Gerät bestätigen</h1>
            <p class="text-surface-500-400 text-sm">
                {#if step === 'oauth'}
                    Schritt 1 von 3 – Google-Konto bestätigen
                {:else if step === 'totp'}
                    Schritt 2 von 3 – Authenticator-Code eingeben
                {:else}
                    Schritt 3 von 3 – Einmalpasswort eingeben
                {/if}
            </p>
        </div>

        {#if step === 'oauth'}
            <button
                onclick={startOAuth}
                disabled={loading}
                class="btn preset-filled-primary-500 w-full"
            >
                {#if loading}
                    Wird weitergeleitet...
                {:else}
                    Mit Google authentifizieren
                {/if}
            </button>

        {:else if step === 'totp'}
            <input
                type="text"
                inputmode="numeric"
                maxlength="6"
                placeholder="000000"
                bind:value={totpCode}
                onkeydown={(e) => e.key === 'Enter' && submitTotp()}
                class="input text-center text-2xl tracking-widest"
            />
            <button
                onclick={submitTotp}
                disabled={loading || totpCode.length !== 6}
                class="btn preset-filled-primary-500 w-full"
            >
                {#if loading}
                    Wird geprüft...
                {:else}
                    Bestätigen
                {/if}
            </button>

        {:else if step === 'otp'}
            <p class="text-surface-500-400 text-sm text-center">
                Ein Einmalpasswort wurde an deine Email geschickt
            </p>
            <input
                type="text"
                inputmode="numeric"
                maxlength="6"
                placeholder="000000"
                bind:value={otpCode}
                onkeydown={(e) => e.key === 'Enter' && submitOtp()}
                class="input text-center text-2xl tracking-widest"
            />
            <button
                onclick={submitOtp}
                disabled={loading || otpCode.length !== 6}
                class="btn preset-filled-primary-500 w-full"
            >
                {#if loading}
                    Wird geprüft...
                {:else}
                    Bestätigen
                {/if}
            </button>
        {/if}

        {#if error}
            <p class="text-error-500 text-sm text-center">{error}</p>
        {/if}

    </div>
</div>