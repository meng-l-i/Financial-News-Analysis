const BASE = '/api'

function getToken() {
  const match = document.cookie.match(/(?:^|;\s*)cc_token=([^;]*)/)
  return match ? decodeURIComponent(match[1]) : ''
}

function authHeaders() {
  const t = getToken()
  return t ? { 'Authorization': t } : {}
}

export function setToken(token) {
  document.cookie = `cc_token=${encodeURIComponent(token)};path=/;max-age=86400;SameSite=Lax`
}

export function getStoredToken() {
  return getToken()
}

export async function login(username, password) {
  const res = await fetch(`${BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  return res.json()
}

async function authedFetch(path) {
  const res = await fetch(path, { headers: authHeaders() })
  if (!res.ok) throw new Error(`${path}: ${res.status}`)
  const json = await res.json()
  return json.data || []
}

export function fetchFields() {
  return authedFetch(`${BASE}/data?target=field`)
}

export function fetchCompanies() {
  return authedFetch(`${BASE}/data?target=company`)
}

export function fetchNews() {
  return authedFetch(`${BASE}/data?target=news`)
}

export async function fetchHealth() {
  const res = await fetch(`${BASE}/health`)
  return res.json()
}
