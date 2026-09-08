/**
 * The factory spine.
 *
 * Every product OMNEX Factory sells is a MODULE: a route group plus an entry in
 * this registry. The dashboard launcher, the pricing page and the navigation are
 * all GENERATED from this list — so shipping a new product is "add a manifest +
 * add a route group", not "build a new app".
 *
 * All modules share one login, one user table, one credit balance and one AI
 * infrastructure. That shared balance is what makes each new module increase the
 * value of the previous ones: a customer's credits work everywhere.
 */

export interface ModuleManifest {
  /** Stable id — also the `module_id` recorded in usage_events / credit_ledger. */
  id: string
  /** Display name shown in the launcher and on pricing. */
  name: string
  /** One line the customer understands in seconds. */
  blurb: string
  /** Route the launcher links to (under the authenticated app group). */
  route: string
  /** Lucide icon name, rendered by the launcher. */
  icon: string
  /** Credits consumed per successful unit of work (0 = free/utility module). */
  creditCost: number
  /** Live modules appear in the launcher; false = built but hidden. */
  enabled: boolean
  /** Roadmap position — kept so the launcher can show "coming next". */
  order: number
}

/**
 * Module #1 is the only enabled one by design: the factory's own rule is that
 * module #2 does not start until module #1 has taken a real payment. The rest
 * are listed as the roadmap the customer can see, not as vapourware promises —
 * `enabled: false` means "not built yet" and the UI must say exactly that.
 */
export const MODULES: ModuleManifest[] = [
  {
    id: 'studio',
    name: 'AI Ad Studio',
    blurb: 'Upload your product → get premium advertising visuals → download.',
    route: '/studio',
    icon: 'Sparkles',
    creditCost: 10,
    enabled: true,
    order: 1,
  },
  // BUILT, and deliberately not enabled. The rule above is that module #2 does
  // not open until module #1 has taken a real payment, and shipping this one
  // early because it happens to be finished is exactly how that rule dies.
  //
  // Metered rather than fixed-price: a streamed run has no price until it ends,
  // so `creditCost` is the FLOOR a completed run bills and the real charge is
  // proportional to measured provider spend (lib/core/agents/metering.ts). It is
  // listed rather than omitted because a module with no manifest entry has no
  // price, no tile and no way to be found — which is how finished work goes
  // unsold.
  { id: 'copilot',  name: 'AI Copilot',         blurb: 'Ask anything; watch every step and what it costs, live.', route: '/copilot', icon: 'MessageSquare', creditCost: 1, enabled: false, order: 2 },
  { id: 'landing',  name: 'AI Landing Pages',   blurb: 'Turn one product into a converting landing page.', route: '/landing',  icon: 'LayoutTemplate', creditCost: 15, enabled: false, order: 3 },
  { id: 'product',  name: 'AI Product Pages',   blurb: 'Full product pages with copy, specs and imagery.',  route: '/product',  icon: 'Package',        creditCost: 15, enabled: false, order: 4 },
  { id: 'sales',    name: 'AI Sales Assets',    blurb: 'Proposals, one-pagers and pitch decks that close.', route: '/sales',    icon: 'FileText',       creditCost: 12, enabled: false, order: 5 },
  { id: 'email',    name: 'AI Email Campaigns', blurb: 'Sequences written from your real product data.',    route: '/email',    icon: 'Mail',           creditCost: 8,  enabled: false, order: 6 },
  { id: 'video',    name: 'AI Video Ads',       blurb: 'Short-form video ads generated from your product.', route: '/video',    icon: 'Video',          creditCost: 40, enabled: false, order: 7 },
  { id: 'brand',    name: 'AI Brand Kit',       blurb: 'Logo, palette, type and voice as one system.',      route: '/brand',    icon: 'Palette',        creditCost: 20, enabled: false, order: 8 },
  { id: 'marketing',name: 'AI Marketing Agent', blurb: 'An agent that plans and runs your campaigns.',      route: '/marketing',icon: 'Megaphone',      creditCost: 25, enabled: false, order: 9 },
  { id: 'growth',   name: 'AI Growth Agent',    blurb: 'Finds channels, tests them, reports what works.',   route: '/growth',   icon: 'TrendingUp',     creditCost: 25, enabled: false, order: 10 },
]

/** Modules a customer can actually use right now. */
export function liveModules(): ModuleManifest[] {
  return MODULES.filter((m) => m.enabled).sort((a, b) => a.order - b.order)
}

/** Modules on the public roadmap (built order), for honest "coming next" UI. */
export function upcomingModules(): ModuleManifest[] {
  return MODULES.filter((m) => !m.enabled).sort((a, b) => a.order - b.order)
}

export function getModule(id: string): ModuleManifest | undefined {
  return MODULES.find((m) => m.id === id)
}

/** Credit cost for a module, 0 when unknown (never throws in a request path). */
export function creditCostOf(id: string): number {
  return getModule(id)?.creditCost ?? 0
}
