// @ts-nocheck
import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load = async ({ cookies, fetch, params }: Parameters<LayoutServerLoad>[0]) => {
    const token = cookies.get('session_token');

    if (!token) {
        throw redirect(302, '/login');
    }

    const res = await fetch(`${import.meta.env.VITE_API_URL}/auth/verify`, {
        credentials: 'include',
    });

    if (!res.ok) {
        cookies.delete('session_token', { path: '/' });
        throw redirect(302, '/login');
    }

    const user = await res.json();

    const serversRes = await fetch(`${import.meta.env.VITE_API_URL}/servers`, {
        credentials: 'include',
    });

    const servers = serversRes.ok ? await serversRes.json() : [];
    const currentServer = params.server ?? cookies.get('last_server') ?? servers[0]?.id ?? null;

    return { user, servers, currentServer };
};