<script lang="ts">
    import { fade, fly } from 'svelte/transition';

    let { open = $bindable(false) } = $props();

    type Section = 'test-mail' | 'devices' | 'sessions' | 'totp' | 'password' | 'agents';
    let activeSection = $state<Section>('agents');

    const sections: { key: Section; label: string }[] = [
        { key: 'agents', label: 'Agents' },
        { key: 'devices', label: 'Trusted Devices' },
        { key: 'sessions', label: 'Aktive Sessions' },
        { key: 'totp', label: 'TOTP' },
        { key: 'password', label: 'Passwort' },
        { key: 'test-mail', label: 'Test-Mail' },
    ];

    // ── State pro Sektion ────────────────────────────────────────────────────

    let testMailStatus = $state('');
    let testMailLoading = $state(false);

    let devices = $state<any[]>([]);
    let devicesLoading = $state(false);

    let sessions = $state<any[]>([]);
    let sessionsLoading = $state(false);

    let totpResetLoading = $state(false);
    let totpResetDone = $state(false);

    let passwordResetLoading = $state(false);
    let passwordResetDone = $state(false);

    let agents = $state<any[]>([]);
    let agentsLoading = $state(false);
    let draggedIndex = $state<number | null>(null);

    // ── Laden wenn Sektion aktiv wird ────────────────────────────────────────

    $effect(() => {
        if (!open) return;
        if (activeSection === 'devices') loadDevices();
        if (activeSection === 'sessions') loadSessions();
        if (activeSection === 'agents') loadAgents();
    });

    // ── Test-Mail ────────────────────────────────────────────────────────────

    async function sendTestMail() {
        testMailLoading = true;
        testMailStatus = '';
        const res = await fetch('/api/settings/test-mail', { method: 'POST' });
        testMailStatus = res.ok ? 'Mail verschickt ✓' : 'Fehler beim Versand';
        testMailLoading = false;
    }

    // ── Trusted Devices ──────────────────────────────────────────────────────

    async function loadDevices() {
        devicesLoading = true;
        const res = await fetch('/api/settings/trusted-devices');
        devices = res.ok ? await res.json() : [];
        devicesLoading = false;
    }

    async function deleteDevice(id: string) {
        await fetch(`/api/settings/trusted-devices/${id}`, { method: 'DELETE' });
        devices = devices.filter(d => d.id !== id);
    }

    // ── Sessions ─────────────────────────────────────────────────────────────

    async function loadSessions() {
        sessionsLoading = true;
        const res = await fetch('/api/settings/sessions');
        sessions = res.ok ? await res.json() : [];
        sessionsLoading = false;
    }

    async function deleteSession(id: string) {
        await fetch(`/api/settings/sessions/${id}`, { method: 'DELETE' });
        sessions = sessions.filter(s => s.id !== id);
    }

    // ── TOTP ─────────────────────────────────────────────────────────────────

    async function resetTotp() {
        totpResetLoading = true;
        const res = await fetch('/api/settings/totp/reset', { method: 'POST' });
        totpResetDone = res.ok;
        totpResetLoading = false;
    }

    // ── Passwort-Reset ───────────────────────────────────────────────────────

    async function requestPasswordReset() {
        passwordResetLoading = true;
        const res = await fetch('/api/settings/password-reset/request', { method: 'POST' });
        passwordResetDone = res.ok;
        passwordResetLoading = false;
    }

    // ── Agents ───────────────────────────────────────────────────────────────

    async function loadAgents() {
        agentsLoading = true;
        const res = await fetch('/api/settings/agents');
        agents = res.ok ? await res.json() : [];
        agentsLoading = false;
    }

    async function deleteAgent(id: string) {
        await fetch(`/api/settings/agents/${id}`, { method: 'DELETE' });
        agents = agents.filter(a => a.id !== id);
    }

    function onDragStart(index: number) {
        draggedIndex = index;
    }

    function onDragOver(e: DragEvent) {
        e.preventDefault();
    }

    async function onDrop(targetIndex: number) {
        if (draggedIndex === null || draggedIndex === targetIndex) return;

        const updated = [...agents];
        const [moved] = updated.splice(draggedIndex, 1);
        updated.splice(targetIndex, 0, moved);

        agents = updated.map((a, i) => ({ ...a, priority: i }));
        draggedIndex = null;

        await Promise.all(
            agents.map((a, i) =>
                fetch(`/api/settings/agents/${a.id}/priority`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ priority: i }),
                })
            )
        );
    }
</script>

{#if open}
    <!-- Backdrop -->
    <div
        class="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm"
        transition:fade={{ duration: 150 }}
        onclick={() => (open = false)}
        role="presentation"
    ></div>

    <!-- Modal -->
    <div
        class="fixed inset-0 z-50 flex items-center justify-center pointer-events-none"
        transition:fly={{ y: 16, duration: 200 }}
    >
        <div class="card preset-outlined-surface-300-700 w-full max-w-3xl h-[70vh] flex overflow-hidden pointer-events-auto">

            <!-- Linke Navigation -->
            <nav class="w-44 border-r border-surface-300-700 flex flex-col gap-1 p-3 shrink-0">
                {#each sections as section}
                    <button
                        onclick={() => (activeSection = section.key)}
                        class="btn {activeSection === section.key ? 'preset-filled-primary-500' : 'preset-tonal-surface'} justify-start text-sm"
                    >
                        {section.label}
                    </button>
                {/each}

                <div class="flex-1"></div>

                <button
                    onclick={() => (open = false)}
                    class="btn preset-tonal-surface justify-start text-sm"
                >
                    Schließen
                </button>
            </nav>

            <!-- Rechter Content -->
            <div class="flex-1 overflow-auto p-6 flex flex-col gap-4">

                {#if activeSection === 'test-mail'}
                    <h2 class="text-lg font-bold">Test-Mail</h2>
                    <p class="text-surface-500-400 text-sm">Sendet eine Test-Mail über den konfigurierten SMTP-Dienst.</p>
                    <button
                        onclick={sendTestMail}
                        disabled={testMailLoading}
                        class="btn preset-filled-primary-500 w-fit"
                    >
                        {testMailLoading ? 'Wird gesendet...' : 'Test-Mail senden'}
                    </button>
                    {#if testMailStatus}
                        <p class="text-sm text-surface-500-400">{testMailStatus}</p>
                    {/if}

                {:else if activeSection === 'devices'}
                    <h2 class="text-lg font-bold">Trusted Devices</h2>
                    {#if devicesLoading}
                        <p class="text-surface-500-400 text-sm">Lädt...</p>
                    {:else if devices.length === 0}
                        <p class="text-surface-500-400 text-sm">Keine Geräte vorhanden.</p>
                    {:else}
                        <div class="flex flex-col gap-2">
                            {#each devices as device}
                                <div class="card preset-tonal-surface p-3 flex items-center justify-between gap-4">
                                    <div class="flex flex-col gap-0.5 min-w-0">
                                        <p class="text-sm font-medium truncate">{device.ip}</p>
                                        <p class="text-xs text-surface-500-400 truncate">{device.user_agent}</p>
                                        <p class="text-xs text-surface-500-400">Läuft ab: {new Date(device.device_key_expires_at).toLocaleDateString('de-DE')}</p>
                                    </div>
                                    <button
                                        onclick={() => deleteDevice(device.id)}
                                        class="btn preset-tonal-error shrink-0 text-sm"
                                    >
                                        Entfernen
                                    </button>
                                </div>
                            {/each}
                        </div>
                    {/if}

                {:else if activeSection === 'sessions'}
                    <h2 class="text-lg font-bold">Aktive Sessions</h2>
                    {#if sessionsLoading}
                        <p class="text-surface-500-400 text-sm">Lädt...</p>
                    {:else if sessions.length === 0}
                        <p class="text-surface-500-400 text-sm">Keine aktiven Sessions.</p>
                    {:else}
                        <div class="flex flex-col gap-2">
                            {#each sessions as session}
                                <div class="card preset-tonal-surface p-3 flex items-center justify-between gap-4">
                                    <div class="flex flex-col gap-0.5">
                                        <p class="text-sm font-medium">Session</p>
                                        <p class="text-xs text-surface-500-400">Erstellt: {new Date(session.created_at).toLocaleString('de-DE')}</p>
                                        <p class="text-xs text-surface-500-400">Läuft ab: {new Date(session.expires_at).toLocaleString('de-DE')}</p>
                                    </div>
                                    <button
                                        onclick={() => deleteSession(session.id)}
                                        class="btn preset-tonal-error shrink-0 text-sm"
                                    >
                                        Invalidieren
                                    </button>
                                </div>
                            {/each}
                        </div>
                    {/if}

                {:else if activeSection === 'totp'}
                    <h2 class="text-lg font-bold">TOTP zurücksetzen</h2>
                    <p class="text-surface-500-400 text-sm">
                        Setzt das TOTP-Secret zurück. Danach muss unter <code class="text-xs">/auth/totp/setup</code> ein neues Secret eingerichtet werden.
                    </p>
                    {#if totpResetDone}
                        <p class="text-success-500 text-sm">TOTP zurückgesetzt – Setup erforderlich.</p>
                    {:else}
                        <button
                            onclick={resetTotp}
                            disabled={totpResetLoading}
                            class="btn preset-tonal-error w-fit"
                        >
                            {totpResetLoading ? 'Wird zurückgesetzt...' : 'TOTP zurücksetzen'}
                        </button>
                    {/if}

                {:else if activeSection === 'password'}
                    <h2 class="text-lg font-bold">Passwort zurücksetzen</h2>
                    <p class="text-surface-500-400 text-sm">
                        Schickt einen Reset-Link an deine hinterlegte Email. Der Link ist 10 Minuten gültig.
                    </p>
                    {#if passwordResetDone}
                        <p class="text-success-500 text-sm">Reset-Link verschickt – prüfe deine Email.</p>
                    {:else}
                        <button
                            onclick={requestPasswordReset}
                            disabled={passwordResetLoading}
                            class="btn preset-tonal-error w-fit"
                        >
                            {passwordResetLoading ? 'Wird gesendet...' : 'Reset-Link anfordern'}
                        </button>
                    {/if}

                {:else if activeSection === 'agents'}
                    <h2 class="text-lg font-bold">Agents</h2>
                    {#if agentsLoading}
                        <p class="text-surface-500-400 text-sm">Lädt...</p>
                    {:else if agents.length === 0}
                        <p class="text-surface-500-400 text-sm">Keine Agents registriert.</p>
                    {:else}
                        <p class="text-surface-500-400 text-xs">Ziehen zum Sortieren der Priorität.</p>
                        <div class="flex flex-col gap-2">
                            {#each agents as agent, i}
                                <div
                                    draggable="true"
                                    ondragstart={() => onDragStart(i)}
                                    ondragover={onDragOver}
                                    ondrop={() => onDrop(i)}
                                    class="card preset-tonal-surface p-3 flex items-center justify-between gap-4 cursor-grab"
                                >
                                    <div class="flex flex-col gap-0.5 min-w-0">
                                        <p class="text-sm font-medium">{agent.name}</p>
                                        <p class="text-xs text-surface-500-400">{agent.hostname} · {agent.ip}</p>
                                        <p class="text-xs text-surface-500-400">
                                            Zuletzt gesehen: {agent.last_seen ? new Date(agent.last_seen).toLocaleString('de-DE') : 'Nie'}
                                        </p>
                                    </div>
                                    <button
                                        onclick={() => deleteAgent(agent.id)}
                                        class="btn preset-tonal-error shrink-0 text-sm"
                                    >
                                        Entfernen
                                    </button>
                                </div>
                            {/each}
                        </div>
                    {/if}
                {/if}

            </div>
        </div>
    </div>
{/if}