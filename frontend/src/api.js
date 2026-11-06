// All requests go through the same origin (/api); no secrets live in the browser.
async function request(path, options) {
  const res = await fetch(path, options)
  let body = null
  try { body = await res.json() } catch { /* empty body */ }
  if (!res.ok) {
    const err = new Error((body && body.detail) || `Request failed (${res.status})`)
    err.status = res.status
    throw err
  }
  return body
}

const qs = (params) => {
  const p = new URLSearchParams()
  Object.entries(params || {}).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') p.set(k, v)
  })
  const s = p.toString()
  return s ? `?${s}` : ''
}

export const api = {
  districts: () => request('/api/districts'),
  categories: () => request('/api/categories'),
  crops: (params) => request(`/api/crops${qs(params)}`),
  search: (params) => request(`/api/crops/search${qs(params)}`),
  crop: (id) => request(`/api/crops/${id}`),
  districtCrops: (id, params) => request(`/api/districts/${id}/crops${qs(params)}`),
  cropDistricts: (id) => request(`/api/crops/${id}/districts`),
  calendar: (params) => request(`/api/calendar${qs(params)}`),
  guide: (params) => request(`/api/cultivation-guide${qs(params)}`),
  sketch: (id, params) => request(`/api/sketches/${id}${qs(params)}`),
  research: (body) => request('/api/research', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  }),
  job: (id) => request(`/api/research/jobs/${id}`),
  jobs: () => request('/api/research/jobs'),
  usage: () => request('/api/research/usage'),
}
