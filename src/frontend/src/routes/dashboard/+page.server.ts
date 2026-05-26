import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, fetch }) => {
    const lastServer = cookies.get('last_server');

    if (lastServer) {
        throw redirect(302, `/dashboard/${lastServer}`);
    }

    const res = await fetch(`${process.env.API_URL}/servers/first`);

    if (!res.ok) {
        throw redirect(302, '/login');
    }

    const { id } = await res.json();
    throw redirect(302, `/dashboard/${id}`);
};