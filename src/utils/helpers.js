import { USERS } from '../data/mockData'

export const avg = (arr) =>
  arr.length ? (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1) : '0.0'

export const getUser = (id) => USERS.find((u) => u.id === id)

export const fileIcon = (t) => ({ PDF:'📕', PPT:'📊', DOC:'📝', IMG:'🖼️' }[t] || '📄')

export const fmtTime = () =>
  new Date().toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' })

export const deepCopy = (o) => JSON.parse(JSON.stringify(o))
