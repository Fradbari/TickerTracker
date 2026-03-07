/**
 * Shared custom hooks.
 *
 * Rules:
 *   - MUST be generic and reusable across features
 *   - Must NOT call feature-specific APIs or use feature query keys
 *   - Should be accompanied by a unit test in __tests__/
 */

// ---------------------------------------------------------------------------
// useDebounce — delay state updates (useful for search inputs)
// ---------------------------------------------------------------------------

import { useState, useEffect } from 'react'

/**
 * Returns a debounced copy of `value` that only updates after `delayMs`
 * milliseconds of inactivity. Ideal for avoiding rapid API calls on keystroke.
 *
 * @example
 *   const debouncedSearch = useDebounce(searchTerm, 400)
 *   // debouncedSearch only changes when the user stops typing for 400 ms
 */
export function useDebounce<T>(value: T, delayMs: number = 400): T {
  const [debounced, setDebounced] = useState<T>(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs)
    return () => clearTimeout(timer)
  }, [value, delayMs])

  return debounced
}

// ---------------------------------------------------------------------------
// useLocalStorage — persistent state backed by localStorage
// ---------------------------------------------------------------------------

/**
 * Like useState but persisted to localStorage under `key`.
 * Falls back to `initialValue` when the key is absent or the stored value
 * cannot be parsed as JSON.
 *
 * @example
 *   const [theme, setTheme] = useLocalStorage('app:theme', 'dark')
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T,
): [T, (value: T | ((prev: T) => T)) => void] {
  const [stored, setStored] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item !== null ? (JSON.parse(item) as T) : initialValue
    } catch {
      return initialValue
    }
  })

  const setValue = (value: T | ((prev: T) => T)) => {
    try {
      const next = value instanceof Function ? value(stored) : value
      setStored(next)
      window.localStorage.setItem(key, JSON.stringify(next))
    } catch (e) {
      console.warn(`useLocalStorage: could not write key "${key}"`, e)
    }
  }

  return [stored, setValue]
}

// ---------------------------------------------------------------------------
// Future shared hooks (uncomment when implemented):
// ---------------------------------------------------------------------------
// export { useWindowSize } from './useWindowSize'
// export { useOnClickOutside } from './useOnClickOutside'
// export { usePrevious } from './usePrevious'
