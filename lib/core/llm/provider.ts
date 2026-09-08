/**
 * Provider-sovereign LLM layer.
 *
 * OMNEX must never depend on a single paid vendor. `complete()` tries providers in a FREE-FIRST
 * priority order and uses the first one whose key (or local endpoint) is configured:
 *
 *   Ollama (local, €0) → Groq (free) → Google AI Studio (free) → OpenRouter (free models) → Anthropic
 *
 * All non-Anthropic providers share an OpenAI-compatible /chat/completions call; Anthropic uses its
 * native /messages API. Keys are sanitized with cleanKey() (BOM-safe). If no provider is configured,
 * `complete()` throws and callers fall back to sources-only — so the product degrades gracefully at €0.
 */
import { cleanKey } from '@/lib/core/supabase/env'
import { getCached, setCached } from './cache'

/** Read an env value, BOM/whitespace-safe (cleanKey) AND strip accidental surrounding quotes. */
function envVal(name: string): string {
  return cleanKey(process.env[name]).replace(/^["'`]+|["'`]+$/g, '').trim()
}

export interface LlmMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
  /**
   * Optional image inputs (https URLs or data:image/...;base64 URIs). When any
   * message carries images, only vision-capable providers are used — the
   * default text models on Groq/OpenRouter/Ollama can't accept image parts.
   */
  images?: string[]
}

/** Providers whose default chain models accept image input. */
const VISION_CAPABLE = new Set(['google', 'anthropic'])
export interface LlmResult {
  text: string
  provider: string
  model: string
  /**
   * Tokens the provider says it billed. Optional because not every provider
   * reports it — and absent is the honest value when one does not.
   *
   * Without this the number never leaves the provider, so nothing downstream
   * can price a call: `estimateCostEur()` in lib/core/agents/budget.ts has a
   * rate table and had nothing to feed it, and the copilot's live cost panel
   * read €0.00 on every real run. A caller that needs a figure anyway must
   * estimate from length and say that it estimated.
   */
  usage?: { promptTokens: number; completionTokens: number }
}

/** Read an OpenAI- or Anthropic-shaped usage block. Absent stays absent. */
function readUsage(raw: unknown): LlmResult['usage'] {
  if (!raw || typeof raw !== 'object') return undefined
  const u = raw as Record<string, unknown>
  const prompt = u.prompt_tokens ?? u.input_tokens
  const completion = u.completion_tokens ?? u.output_tokens
  if (typeof prompt !== 'number' || typeof completion !== 'number') return undefined
  return { promptTokens: prompt, completionTokens: completion }
}
export type TaskProfile = 'reasoning' | 'coding' | 'fast' | 'cheap'

export interface LlmOptions {
  maxTokens?: number
  temperature?: number
  /**
   * Opt-in semantic response cache (migration 016). When true, a near-identical
   * prior prompt returns the cached answer (skips the LLM call). Best for
   * deterministic prompts (temperature 0). Graceful: cache miss/error → normal call.
   */
  cache?: boolean
  /**
   * Optional task-shaped provider preference. Re-orders the configured chain so the
   * providers best suited to the task are tried first; the full fallback chain stays
   * intact behind them (an unavailable preferred provider falls through as always).
   * Omitted → the default free-first order, unchanged.
   */
  taskProfile?: TaskProfile
}

/**
 * Preferred provider order per task profile. Names not listed keep their default
 * free-first relative order after the listed ones. This is a preference, not a
 * hard requirement — whatever is actually configured still forms the full chain.
 */
const PROFILE_ORDER: Record<TaskProfile, string[]> = {
  reasoning: ['anthropic', 'google', 'groq', 'openrouter', 'ollama'],
  coding: ['anthropic', 'groq', 'google', 'openrouter', 'ollama'],
  fast: ['groq', 'google', 'ollama', 'openrouter', 'anthropic'],
  cheap: ['ollama', 'groq', 'google', 'openrouter', 'anthropic'],
}

/**
 * Pure ordering helper (exported for tests): stable-sorts provider names by the
 * profile's preference list; unknown names keep their existing relative order at the end.
 */
export function orderForProfile(names: string[], profile?: TaskProfile): string[] {
  if (!profile) return [...names]
  const pref = PROFILE_ORDER[profile]
  return [...names].sort((a, b) => {
    const ia = pref.indexOf(a)
    const ib = pref.indexOf(b)
    return (ia === -1 ? pref.length : ia) - (ib === -1 ? pref.length : ib)
  })
}

interface ProviderCfg {
  name: string
  baseURL: string
  model: string
  key: string
  kind: 'openai' | 'anthropic'
}

/** Build the ordered list of configured providers (free-first). */
function providers(): ProviderCfg[] {
  const list: ProviderCfg[] = []

  const ollama = envVal('OLLAMA_URL')
  if (ollama) {
    list.push({
      name: 'ollama',
      baseURL: ollama.replace(/\/$/, ''),
      model: cleanKey(process.env.OLLAMA_MODEL) || 'llama3.1',
      key: 'ollama',
      kind: 'openai',
    })
  }
  const groq = envVal('GROQ_API_KEY')
  if (groq) {
    list.push({
      name: 'groq',
      baseURL: 'https://api.groq.com/openai/v1',
      model: cleanKey(process.env.GROQ_MODEL) || 'llama-3.3-70b-versatile',
      key: groq,
      kind: 'openai',
    })
  }
  const google = envVal('GOOGLE_AI_API_KEY')
  if (google) {
    list.push({
      name: 'google',
      baseURL: 'https://generativelanguage.googleapis.com/v1beta/openai',
      model: cleanKey(process.env.GOOGLE_MODEL) || 'gemini-2.0-flash',
      key: google,
      kind: 'openai',
    })
  }
  const openrouter = envVal('OPENROUTER_API_KEY')
  if (openrouter) {
    list.push({
      name: 'openrouter',
      baseURL: 'https://openrouter.ai/api/v1',
      model: cleanKey(process.env.OPENROUTER_MODEL) || 'meta-llama/llama-3.3-70b-instruct:free',
      key: openrouter,
      kind: 'openai',
    })
  }
  // Hugging Face Inference Providers — OpenAI-compatible chat endpoint. Reuses the
  // same HF_TOKEN as embeddings; adds more free/cheap models to the chain.
  const hf = envVal('HF_TOKEN')
  if (hf) {
    list.push({
      name: 'huggingface',
      baseURL: 'https://router.huggingface.co/v1',
      model: cleanKey(process.env.HF_LLM_MODEL) || 'meta-llama/Llama-3.3-70B-Instruct',
      key: hf,
      kind: 'openai',
    })
  }
  const anthropic = envVal('ANTHROPIC_API_KEY')
  if (anthropic) {
    list.push({
      name: 'anthropic',
      baseURL: 'https://api.anthropic.com/v1',
      model: cleanKey(process.env.ANTHROPIC_MODEL) || 'claude-haiku-4-5-20251001',
      key: anthropic,
      kind: 'anthropic',
    })
  }
  return list
}

export function hasProvider(): boolean {
  return providers().length > 0
}

export function providerNames(): string[] {
  return providers().map((p) => p.name)
}

async function callOpenAICompat(p: ProviderCfg, messages: LlmMessage[], opts: LlmOptions): Promise<LlmResult> {
  // Messages with images use the OpenAI vision content-parts format; text-only
  // messages stay plain strings (maximum compatibility with all providers).
  const wireMessages = messages.map((m) =>
    m.images?.length
      ? {
          role: m.role,
          content: [
            { type: 'text', text: m.content },
            ...m.images.map((url) => ({ type: 'image_url', image_url: { url } })),
          ],
        }
      : { role: m.role, content: m.content }
  )
  const res = await fetch(`${p.baseURL}/chat/completions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${p.key}` },
    body: JSON.stringify({
      model: p.model,
      messages: wireMessages,
      max_tokens: opts.maxTokens ?? 1024,
      temperature: opts.temperature ?? 0.6,
    }),
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`${p.name} ${res.status}: ${body.slice(0, 200)}`)
  }
  const data = (await res.json()) as {
    choices?: Array<{ message?: { content?: string } }>
    usage?: unknown
  }
  const text = data.choices?.[0]?.message?.content
  if (!text) throw new Error(`${p.name}: empty response`)
  const usage = readUsage(data.usage)
  return { text, provider: p.name, model: p.model, ...(usage ? { usage } : {}) }
}

/** Convert an image reference (https URL or data URI) to an Anthropic source block. */
function anthropicImageSource(url: string): Record<string, unknown> {
  const dataMatch = url.match(/^data:(image\/[a-z+]+);base64,(.+)$/i)
  if (dataMatch) {
    return { type: 'image', source: { type: 'base64', media_type: dataMatch[1], data: dataMatch[2] } }
  }
  return { type: 'image', source: { type: 'url', url } }
}

async function callAnthropic(p: ProviderCfg, messages: LlmMessage[], opts: LlmOptions): Promise<LlmResult> {
  const system = messages.filter((m) => m.role === 'system').map((m) => m.content).join('\n\n')
  const rest = messages
    .filter((m) => m.role !== 'system')
    .map((m) =>
      m.images?.length
        ? {
            role: m.role,
            content: [...m.images.map(anthropicImageSource), { type: 'text', text: m.content }],
          }
        : { role: m.role, content: m.content }
    )
  const res = await fetch(`${p.baseURL}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': p.key,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: p.model,
      max_tokens: opts.maxTokens ?? 1024,
      ...(system ? { system } : {}),
      messages: rest,
    }),
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`anthropic ${res.status}: ${body.slice(0, 200)}`)
  }
  const data = (await res.json()) as {
    content?: Array<{ type?: string; text?: string }>
    usage?: unknown
  }
  const first = data.content?.[0]
  const text = first && first.type === 'text' ? first.text : undefined
  if (!text) throw new Error('anthropic: empty response')
  const usage = readUsage(data.usage)
  return { text, provider: p.name, model: p.model, ...(usage ? { usage } : {}) }
}

/** Diagnostic: try each configured provider with a tiny prompt; report ok/error per provider. */
export async function probeAll(): Promise<Array<{ name: string; ok: boolean; model: string; error?: string }>> {
  const out: Array<{ name: string; ok: boolean; model: string; error?: string }> = []
  for (const p of providers()) {
    try {
      const r = p.kind === 'anthropic'
        ? await callAnthropic(p, [{ role: 'user', content: 'ping' }], { maxTokens: 5 })
        : await callOpenAICompat(p, [{ role: 'user', content: 'ping' }], { maxTokens: 5 })
      out.push({ name: p.name, ok: true, model: r.model })
    } catch (e) {
      out.push({ name: p.name, ok: false, model: p.model, error: e instanceof Error ? e.message.slice(0, 220) : String(e) })
    }
  }
  return out
}

/**
 * Generate a completion from the first available provider, falling through on per-provider error.
 * Throws "no_llm_provider" when nothing is configured (callers should degrade to sources-only).
 */
export async function complete(messages: LlmMessage[], opts: LlmOptions = {}): Promise<LlmResult> {
  // Opt-in semantic cache: a near-identical prior prompt returns the cached
  // answer without any provider call. Graceful — a miss/error just continues.
  const cacheKey = opts.cache ? messages.map((m) => `${m.role}:${m.content}`).join('\n') : ''
  if (opts.cache) {
    const hit = await getCached(cacheKey)
    if (hit) return { text: hit.response, provider: `cache:${hit.source}`, model: hit.model ?? 'cache' }
  }

  let provs = providers()
  if (provs.length === 0) throw new Error('no_llm_provider')
  const needsVision = messages.some((m) => m.images?.length)
  if (needsVision) {
    provs = provs.filter((p) => VISION_CAPABLE.has(p.name))
    if (provs.length === 0) throw new Error('no_vision_provider')
  }
  if (opts.taskProfile) {
    const order = orderForProfile(provs.map((p) => p.name), opts.taskProfile)
    provs = [...provs].sort((a, b) => order.indexOf(a.name) - order.indexOf(b.name))
  }
  let lastErr: unknown = null
  for (const p of provs) {
    // Free tiers rate-limit under multi-step workflows (Groq 429 killed steps 5-6 of a
    // 6-step run). One retry after a short backoff before falling through — kept short
    // because the workflow execute route runs under Vercel's maxDuration=60s budget.
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        const result = p.kind === 'anthropic'
          ? await callAnthropic(p, messages, opts)
          : await callOpenAICompat(p, messages, opts)
        if (opts.cache) void setCached(cacheKey, result.text, result.model)
        return result
      } catch (e) {
        lastErr = e
        const msg = e instanceof Error ? e.message : String(e)
        const rateLimited = /\b429\b|rate.?limit/i.test(msg)
        if (!rateLimited || attempt === 1) break
        await new Promise((r) => setTimeout(r, 12_000))
      }
    }
  }
  throw lastErr instanceof Error ? lastErr : new Error('all_providers_failed')
}
