const SESSION_KEY = 'offerpilot_session_v1'

export function loadSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY) || '{}')
  } catch {
    return {}
  }
}

export function saveSession(patch) {
  const current = loadSession()
  const next = { ...current, ...patch }
  localStorage.setItem(SESSION_KEY, JSON.stringify(next))
  return next
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY)
}
