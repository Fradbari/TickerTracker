/**
 * EstimateForm — create a new trading estimate.
 *
 * Features:
 *   - Client-side validation via Zod + react-hook-form
 *   - Direction toggle: LONG (bull) / SHORT (bear)
 *   - Ticker input with uppercase auto-format and format validation
 *   - Real-time profit/stop-loss price preview (Decimal-precise arithmetic)
 *   - Submit disabled while mutation is in-flight
 *   - API errors surfaced via react-hot-toast (useNotify)
 *
 * Note on ticker_id:
 *   The API expects a UUID in `ticker_id`. Since /api/tickers/search does not
 *   exist yet in the MVP, this form uses the raw ticker symbol string as a
 *   placeholder value.
 *   // TODO: replace with UUID from /api/tickers/search (TASK 4.x)
 *
 * Note on entry_price:
 *   `entry_price` is a form-only field used to compute the real-time preview.
 *   It is NOT sent to the API — the backend resolves the current market price
 *   at creation time from its own market data service.
 *
 * Note on notes:
 *   `notes` is collected for UX completeness but is not part of
 *   `CreateEstimatePayload` in the current MVP.
 *   // TODO: map to ai_reasoning or a dedicated notes field when the backend
 *   //        schema is extended (TASK 4.x)
 */
import { useMemo } from 'react'
import { useForm, type SubmitHandler } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Decimal from 'decimal.js'
import { useTranslation } from 'react-i18next'

import { useCreateEstimateAsync } from '../api/mutations'
import { useInsertionTracker } from '../hooks/useInsertionTracker'
import { InsertionTrackerBox } from './InsertionTrackerBox'
import type { EstimateDirection } from '../types'
import { formatMoney, fromDecimalAmount } from '@/shared/finance'
import { useNotify } from '@/shared/ui'
import { isApiError } from '@/shared/api'

// ---------------------------------------------------------------------------
// Validation schema — Zod v4
//
// All numeric fields use z.string().refine() instead of z.coerce.number()
// because z.coerce.number() behaviour changed in Zod v4 and HTML <input>
// elements always produce string values. This pattern keeps the output type
// as `string`, matching CreateEstimatePayload exactly.
// ---------------------------------------------------------------------------

/** Validates a numeric string for a percentage field in (minVal, maxVal]. */
function numericStringRefinement(
  val: string,
  min: number,
  max: number,
): boolean {
  try {
    const n = new Decimal(val)
    return n.isFinite() && n.greaterThan(min) && n.lessThanOrEqualTo(max)
  } catch {
    return false
  }
}

const schema = z.object({
  /** Ticker symbol — upper-case, 1–10 alphanumeric chars. */
  ticker: z
    .string()
    .min(1, 'Ticker obbligatorio')
    .max(10, 'Massimo 10 caratteri')
    .regex(
      /^[A-Z0-9.]+$/,
      'Solo lettere maiuscole, numeri e punti (es. AAPL, BRK.A)',
    ),

  /** Trade direction — LONG or SHORT. */
  direction: z.enum(['LONG', 'SHORT'] as const),

  /**
   * Preview-only field: current market price the user references.
   * Used exclusively for the real-time target/stop preview; not sent to API.
   */
  entry_price: z
    .string()
    .min(1, 'Inserisci un prezzo di riferimento per il preview')
    .refine(
      val => {
        try {
          const n = new Decimal(val)
          return n.isFinite() && n.greaterThan(0)
        } catch {
          return false
        }
      },
      { message: 'Deve essere un numero positivo (es. 182.50)' },
    ),

  /** Target profit — percentage, 0.01 % to 100 %. */
  target_profit_percent: z
    .string()
    .min(1, 'Obiettivo profitto obbligatorio')
    .refine(
      val => numericStringRefinement(val, 0, 100),
      { message: 'Deve essere tra 0.01 % e 100 %' },
    ),

  /** Stop-loss — percentage, 0.01 % to 100 %. */
  stop_loss_percent: z
    .string()
    .min(1, 'Stop-loss obbligatorio')
    .refine(
      val => numericStringRefinement(val, 0, 100),
      { message: 'Deve essere tra 0.01 % e 100 %' },
    ),

  /** Optional internal notes — not in CreateEstimatePayload (MVP). */
  notes: z.string().optional(),
})

type FormValues = z.infer<typeof schema>

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface EstimateFormProps {
  /**
   * Called after a successful create, with the newly created estimate's id.
   * Use to redirect to the detail view or close a modal.
   */
  onSuccess?: (estimateId: string) => void
  /** Called when the user explicitly cancels (e.g. presses "Annulla"). */
  onCancel?: () => void
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Computes the absolute target and stop-loss prices from the given inputs
 * using exact Decimal arithmetic.
 *
 * For LONG:
 *   targetPrice = entryPrice × (1 + profitPct / 100)
 *   stopPrice   = entryPrice × (1 − stopPct   / 100)
 *
 * For SHORT (directions are inverted):
 *   targetPrice = entryPrice × (1 − profitPct / 100)
 *   stopPrice   = entryPrice × (1 + stopPct   / 100)
 *
 * Returns `null` for any field if the corresponding input cannot be parsed.
 */
function computePreview(
  entryPriceStr: string,
  profitPctStr: string,
  stopPctStr: string,
  direction: EstimateDirection,
  currency: string,
): { targetPrice: string | null; stopPrice: string | null } {
  let entry: InstanceType<typeof Decimal>
  let pp: InstanceType<typeof Decimal>
  let sp: InstanceType<typeof Decimal>

  try {
    entry = new Decimal(entryPriceStr)
    if (entry.lessThanOrEqualTo(0)) throw new Error()
  } catch {
    return { targetPrice: null, stopPrice: null }
  }

  try { pp = new Decimal(profitPctStr) } catch { pp = new Decimal(NaN) }
  try { sp = new Decimal(stopPctStr) } catch { sp = new Decimal(NaN) }

  const profitFactor = pp.isFinite() ? pp.dividedBy(100) : new Decimal(NaN)
  const stopFactor   = sp.isFinite() ? sp.dividedBy(100) : new Decimal(NaN)

  let targetPrice: string | null = null
  let stopPrice:   string | null = null

  if (pp.isFinite() && pp.greaterThan(0)) {
    const multiplier = direction === 'LONG'
      ? new Decimal(1).plus(profitFactor)
      : new Decimal(1).minus(profitFactor)
    targetPrice = formatMoney(
      fromDecimalAmount(entry.times(multiplier).toDecimalPlaces(4), currency),
    )
  }

  if (sp.isFinite() && sp.greaterThan(0)) {
    const multiplier = direction === 'LONG'
      ? new Decimal(1).minus(stopFactor)
      : new Decimal(1).plus(stopFactor)
    stopPrice = formatMoney(
      fromDecimalAmount(entry.times(multiplier).toDecimalPlaces(4), currency),
    )
  }

  return { targetPrice, stopPrice }
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function EstimateForm({ onSuccess, onCancel }: EstimateFormProps) {
  const notify = useNotify()
  const { t } = useTranslation('common')

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      ticker: '',
      direction: 'LONG',
      entry_price: '',
      target_profit_percent: '',
      stop_loss_percent: '',
      notes: '',
    },
  })

  const { addTask } = useInsertionTracker()
  const { mutate, isPending } = useCreateEstimateAsync()

  // ── Watch all fields for real-time preview ─────────────────────────────
  const [watchedTicker, watchedDirection, watchedEntryPrice, watchedProfit, watchedStop] =
    watch(['ticker', 'direction', 'entry_price', 'target_profit_percent', 'stop_loss_percent'])

  // ── Real-time preview (Decimal-precise) ────────────────────────────────
  const preview = useMemo(
    () =>
      computePreview(
        watchedEntryPrice ?? '',
        watchedProfit ?? '',
        watchedStop ?? '',
        watchedDirection ?? 'LONG',
        'USD', // default currency — backend may return actual currency
      ),
    [watchedEntryPrice, watchedProfit, watchedStop, watchedDirection],
  )

  // ── Submit handler ─────────────────────────────────────────────────────
  const onSubmit: SubmitHandler<FormValues> = data => {
    mutate(
      {
        // TODO: replace with UUID from /api/tickers/search (TASK 4.x)
        // Using the ticker symbol as a placeholder until the ticker-lookup
        // endpoint is available.
        ticker_id: data.ticker,
        direction: data.direction,
        target_profit_percent: data.target_profit_percent,
        stop_loss_percent: data.stop_loss_percent,
      },
      {
        onSuccess: response => {
          // Aggiungi la task al tracker
          addTask({
            taskId: response.task_id,
            ticker: data.ticker,
            direction: data.direction,
            status: 'Pending',
            createdAt: new Date().toISOString()
          })
          
          notify.success(`Stima per ${data.ticker} in elaborazione asincrona.`)
          
          // Resettiamo il form subito (ma manteniamo la direzione)
          setValue('ticker', '')
          setValue('entry_price', '')
          setValue('target_profit_percent', '')
          setValue('stop_loss_percent', '')
          setValue('notes', '')
        },
        onError: (error: Error) => {
          // useCreateEstimateAsync uses raw useMutation (not useApiMutation),
          // so we handle the toast here manually.
          const msg = isApiError(error)
            ? error.message
            : 'Errore durante la creazione della stima'
          const id = isApiError(error) ? error.code : undefined
          notify.error(msg, { id })
        },
      },
    )
  }

  const isLoading = isPending || isSubmitting

  // ── JSX ───────────────────────────────────────────────────────────────
  return (
    <form
      onSubmit={(e) => { void handleSubmit(onSubmit)(e)?.catch(() => {}); }}
      noValidate
      className="space-y-6"
      aria-label={t('formSection', 'Nuova stima di trading')}
    >
      {/* ── Ticker ──────────────────────────────────────────────────── */}
      <div>
        <label
          htmlFor="ticker"
          className="block text-sm font-medium text-slate-300 mb-1.5"
        >
          Ticker <span className="text-red-400">*</span>
        </label>
        {/* TODO: replace with autocomplete when /api/tickers/search is available (TASK 4.x) */}
        <input
          id="ticker"
          type="text"
          inputMode="text"
          autoCapitalize="characters"
          maxLength={10}
          placeholder="es. AAPL"
          aria-invalid={!!errors.ticker}
          aria-describedby={errors.ticker ? 'ticker-error' : undefined}
          {...register('ticker', {
            onChange: e => {
              // Force uppercase in real-time, before Zod runs
              e.target.value = e.target.value.toUpperCase()
              setValue('ticker', e.target.value, { shouldValidate: true })
            },
          })}
          className={inputClass(!!errors.ticker)}
        />
        {errors.ticker && (
          <p id="ticker-error" role="alert" className={errorClass}>
            {errors.ticker.message}
          </p>
        )}
      </div>

      {/* ── Direction toggle ─────────────────────────────────────────── */}
      <div>
        <span className="block text-sm font-medium text-slate-300 mb-1.5">
          Direzione <span className="text-red-400">*</span>
        </span>
        <div className="flex rounded-md overflow-hidden border border-slate-700">
          {(['LONG', 'SHORT'] as const).map(dir => (
            <button
              key={dir}
              type="button"
              onClick={() => setValue('direction', dir, { shouldValidate: true })}
              aria-pressed={watchedDirection === dir}
              className={directionButtonClass(watchedDirection === dir, dir)}
            >
              {dir === 'LONG' ? '▲ LONG' : '▼ SHORT'}
            </button>
          ))}
        </div>
        {/* Hidden input so react-hook-form registers the field */}
        <input type="hidden" {...register('direction')} />
      </div>

      {/* ── Entry price (preview only) ───────────────────────────────── */}
      <div>
        <label
          htmlFor="entry_price"
          className="block text-sm font-medium text-slate-300 mb-1.5"
        >
          Prezzo attuale{' '}
          <span className="text-slate-500 font-normal text-xs">
            (solo per il preview — non inviato all'API)
          </span>{' '}
          <span className="text-red-400">*</span>
        </label>
        <input
          id="entry_price"
          type="text"
          inputMode="decimal"
          placeholder="es. 182.50"
          aria-invalid={!!errors.entry_price}
          aria-describedby={errors.entry_price ? 'entry-price-error' : undefined}
          {...register('entry_price')}
          className={inputClass(!!errors.entry_price)}
        />
        {errors.entry_price && (
          <p id="entry-price-error" role="alert" className={errorClass}>
            {errors.entry_price.message}
          </p>
        )}
      </div>

      {/* ── Profit / Stop-loss row ────────────────────────────────────── */}
      <div className="grid grid-cols-2 gap-4">
        {/* Target profit % */}
        <div>
          <label
            htmlFor="target_profit_percent"
            className="block text-sm font-medium text-slate-300 mb-1.5"
          >
            Obiettivo profitto (%) <span className="text-red-400">*</span>
          </label>
          <div className="relative">
            <input
              id="target_profit_percent"
              type="text"
              inputMode="decimal"
              placeholder="es. 15"
              aria-invalid={!!errors.target_profit_percent}
              aria-describedby={
                errors.target_profit_percent
                  ? 'target-profit-error'
                  : undefined
              }
              {...register('target_profit_percent')}
              className={`${inputClass(!!errors.target_profit_percent)} pr-8`}
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none">
              %
            </span>
          </div>
          {errors.target_profit_percent && (
            <p id="target-profit-error" role="alert" className={errorClass}>
              {errors.target_profit_percent.message}
            </p>
          )}
        </div>

        {/* Stop-loss % */}
        <div>
          <label
            htmlFor="stop_loss_percent"
            className="block text-sm font-medium text-slate-300 mb-1.5"
          >
            Stop-loss (%) <span className="text-red-400">*</span>
          </label>
          <div className="relative">
            <input
              id="stop_loss_percent"
              type="text"
              inputMode="decimal"
              placeholder="es. 5"
              aria-invalid={!!errors.stop_loss_percent}
              aria-describedby={
                errors.stop_loss_percent ? 'stop-loss-error' : undefined
              }
              {...register('stop_loss_percent')}
              className={`${inputClass(!!errors.stop_loss_percent)} pr-8`}
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none">
              %
            </span>
          </div>
          {errors.stop_loss_percent && (
            <p id="stop-loss-error" role="alert" className={errorClass}>
              {errors.stop_loss_percent.message}
            </p>
          )}
        </div>
      </div>

      {/* ── Real-time preview ─────────────────────────────────────────── */}
      {(preview.targetPrice !== null || preview.stopPrice !== null) && (
        <div
          className="rounded-lg border border-slate-700 bg-slate-900/60 p-4 space-y-2"
          aria-live="polite"
          aria-label="Preview calcoli"
        >
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
            Preview prezzi ({watchedTicker || '—'} ·{' '}
            <span
              className={
                watchedDirection === 'LONG' ? 'text-emerald-400' : 'text-red-400'
              }
            >
              {watchedDirection}
            </span>
            )
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <PreviewCard
              label="Prezzo target"
              value={preview.targetPrice}
              colorClass="text-emerald-400"
              hint={`+${watchedProfit ?? '?'}%`}
            />
            <PreviewCard
              label="Prezzo stop-loss"
              value={preview.stopPrice}
              colorClass="text-red-400"
              hint={`−${watchedStop ?? '?'}%`}
            />
          </div>
        </div>
      )}

      {/* ── Notes (optional) ──────────────────────────────────────────── */}
      <div>
        <label
          htmlFor="notes"
          className="block text-sm font-medium text-slate-300 mb-1.5"
        >
          Note{' '}
          <span className="text-slate-500 font-normal text-xs">(opzionale)</span>
        </label>
        <textarea
          id="notes"
          rows={3}
          placeholder="Ragionamento, livelli chiave, link ad analisi…"
          {...register('notes')}
          className="w-full rounded-md border border-slate-700 bg-slate-900 px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
        />
      </div>

      {/* ── Action buttons ────────────────────────────────────────────── */}
      <div className="flex items-center justify-end gap-3 pt-2">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="rounded-md border border-slate-600 px-5 py-2.5 text-sm font-medium text-slate-300 hover:border-slate-400 hover:text-slate-100 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 focus:ring-offset-slate-950"
          >
            {t('cancel', 'Annulla')}
          </button>
        )}
        <button
          type="submit"
          disabled={isLoading}
          className="rounded-md bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-slate-950 flex items-center gap-2"
        >
          {isLoading && (
            <svg
              className="h-4 w-4 animate-spin text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
          )}
          {isLoading ? 'Invio in corso…' : t('createEstimate', 'Crea stima')}
        </button>
      </div>
      <InsertionTrackerBox />    </form>
  )
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface PreviewCardProps {
  label: string
  value: string | null
  colorClass: string
  hint: string
}

function PreviewCard({ label, value, colorClass, hint }: PreviewCardProps) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-slate-500">{label}</span>
      {value !== null ? (
        <>
          <span className={`text-lg font-semibold tabular-nums ${colorClass}`}>
            {value}
          </span>
          <span className="text-xs text-slate-600">{hint}</span>
        </>
      ) : (
        <span className="text-slate-600 text-sm">—</span>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Style helpers (avoid Tailwind class concatenation from dynamic strings)
// ---------------------------------------------------------------------------

function inputClass(hasError: boolean): string {
  const base =
    'w-full rounded-md border bg-slate-900 px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-1 transition-colors'
  return hasError
    ? `${base} border-red-500 focus:border-red-400 focus:ring-red-400`
    : `${base} border-slate-700 focus:border-blue-500 focus:ring-blue-500`
}

const errorClass = 'mt-1.5 text-xs text-red-400'

function directionButtonClass(active: boolean, dir: EstimateDirection): string {
  const base = 'flex-1 py-2.5 text-sm font-semibold transition-colors focus:outline-none'
  if (!active) return `${base} bg-slate-900 text-slate-500 hover:text-slate-300`
  return dir === 'LONG'
    ? `${base} bg-emerald-700/30 text-emerald-400 border-emerald-600`
    : `${base} bg-red-700/30 text-red-400 border-red-600`
}
