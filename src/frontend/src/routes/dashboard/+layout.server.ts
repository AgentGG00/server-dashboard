import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies, fetch, params }) => {
    const token = cookies.get('session_token');

    if (!token) {
        throw redirect(302, '/login');
    }

    const res = await fetch(`${process.env.API_URL}/auth/verify`, {
        headers: { Authorization: `Bearer ${token}` }
    });

    if (!res.ok) {
        cookies.delete('session_token', { path: '/' });
        throw redirect(302, '/login');
    }

    const user = await res.json();

    const serversRes = await fetch(`${process.env.API_URL}/servers`, {
        headers: { Authorization: `Bearer ${token}` }
    });

    const servers = serversRes.ok ? await serversRes.json() : [];

    const currentServer = params.server ?? cookies.get('last_server') ?? servers[0]?.id ?? null;

    return { user, servers, currentServer };
};