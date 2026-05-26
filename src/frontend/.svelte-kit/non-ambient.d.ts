
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	type MatcherParam<M> = M extends (param : string) => param is (infer U extends string) ? U : string;

	export interface AppTypes {
		RouteId(): "/" | "/approve" | "/approve/[token]" | "/dashboard" | "/dashboard/[server]" | "/dashboard/[server]/apache" | "/dashboard/[server]/docker" | "/dashboard/[server]/firewall" | "/dashboard/[server]/systemd" | "/login" | "/login/totp" | "/password-reset" | "/password-reset/[token]";
		RouteParams(): {
			"/approve/[token]": { token: string };
			"/dashboard/[server]": { server: string };
			"/dashboard/[server]/apache": { server: string };
			"/dashboard/[server]/docker": { server: string };
			"/dashboard/[server]/firewall": { server: string };
			"/dashboard/[server]/systemd": { server: string };
			"/password-reset/[token]": { token: string }
		};
		LayoutParams(): {
			"/": { token?: string | undefined; server?: string | undefined };
			"/approve": { token?: string | undefined };
			"/approve/[token]": { token: string };
			"/dashboard": { server?: string | undefined };
			"/dashboard/[server]": { server: string };
			"/dashboard/[server]/apache": { server: string };
			"/dashboard/[server]/docker": { server: string };
			"/dashboard/[server]/firewall": { server: string };
			"/dashboard/[server]/systemd": { server: string };
			"/login": Record<string, never>;
			"/login/totp": Record<string, never>;
			"/password-reset": { token?: string | undefined };
			"/password-reset/[token]": { token: string }
		};
		Pathname(): "/" | `/approve/${string}` & {} | "/dashboard" | `/dashboard/${string}` & {} | `/dashboard/${string}/apache` & {} | `/dashboard/${string}/docker` & {} | `/dashboard/${string}/firewall` & {} | `/dashboard/${string}/systemd` & {} | "/login" | "/login/totp" | `/password-reset/${string}` & {};
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/robots.txt" | string & {};
	}
}