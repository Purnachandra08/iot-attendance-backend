export const now = () => new Date();
export const iso = () => new Date().toISOString();
export function dateLocal(d=new Date()) { return new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Kolkata',year:'numeric',month:'2-digit',day:'2-digit'}).format(d); }
export function timeLocal(d=new Date()) { return new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Kolkata',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false}).format(d); }
export function makeId(prefix) { return `${prefix}${Date.now()}${Math.floor(Math.random()*1000)}`; }
export function validDate(s) { return /^\d{4}-\d{2}-\d{2}$/.test(s || ''); }
