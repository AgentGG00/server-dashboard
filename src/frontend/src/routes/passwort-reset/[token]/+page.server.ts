import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
    const res = await fetch(`/api/settings/password-reset/${params.token}/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: '', confirm_password: '' }),
    });

    // 400 ist okay – Token ist gültig, Passwort nur noch nicht gesetzt
    if (res.status !== 400 && !res.ok) {
        throw error(404, 'Link ungültig oder abgelaufen');
    }

    return { token: params.token };
};