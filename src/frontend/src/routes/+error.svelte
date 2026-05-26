<script lang="ts">
    import { page } from '$app/stores';

    const messages: Record<number, { title: string; description: string }> = {
        401: {
            title: 'Nicht angemeldet',
            description: 'Deine Session ist abgelaufen oder ungültig.',
        },
        403: {
            title: 'Zugriff verweigert',
            description: 'Du bist nicht berechtigt diese Seite aufzurufen.',
        },
        404: {
            title: 'Nicht gefunden',
            description: 'Die Seite oder der Link existiert nicht oder ist abgelaufen.',
        },
        408: {
            title: 'Session abgelaufen',
            description: 'Die Sitzung auf der Approve-Page ist abgelaufen. Fordere einen neuen Link an.',
        },
        410: {
            title: 'Link abgelaufen',
            description: 'Dieser Link ist nicht mehr gültig. Fordere einen neuen an.',
        },
        500: {
            title: 'Serverfehler',
            description: 'Ein interner Fehler ist aufgetreten. Versuche es später erneut.',
        },
    };

    let status = $derived($page.status);
    let content = $derived(messages[status] ?? {
        title: 'Fehler',
        description: $page.error?.message ?? 'Ein unbekannter Fehler ist aufgetreten.',
    });
</script>

<div class="min-h-screen flex items-center justify-center bg-surface-50-950">
    <div class="card preset-outlined-surface-300-700 p-10 w-full max-w-sm flex flex-col gap-6">
        <div class="flex flex-col gap-1 text-center">
            <p class="text-6xl font-bold text-primary-500">{status}</p>
            <h1 class="text-2xl font-bold">{content.title}</h1>
            <p class="text-surface-500-400 text-sm">{content.description}</p>
        </div>

        <a href="/login" class="btn preset-filled-primary-500 w-full text-center">
            Zurück zum Login
        </a>
    </div>
</div>