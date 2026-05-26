// @ts-nocheck
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load = async ({ params, fetch }: Parameters<PageServerLoad>[0]) => {
    const res = await fetch(`/api/auth/approve/${params.token}`);

    if (!res.ok) {
        throw error(404, 'Link ungültig oder abgelaufen');
    }

    return { token: params.token };
};