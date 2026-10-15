// Live class schedule for /schedule. Reads the public Mariana Tek class list and fills the
// <!--LIVE-->...<!--/LIVE--> block of the static /schedule.html shell (built by tools/build-pages.py).
// Spot counts are NOT shown: the studio has is_remaining_spot_count_public = false in Mariana.
export const config = { runtime: 'edge' };

const API = 'https://space.marianatek.com/api/customer/v1/classes';
const LOCATION = '48717';
const TZ = 'America/New_York';
const DAYS = 7;
const CLASS_PAGE = { pilates: '/classes/pilates', sculpt: '/classes/sculpt', strength: '/classes/strength', yoga: '/classes/yoga' };

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const ymd = (d) => new Intl.DateTimeFormat('en-CA', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit' }).format(d);

function clock(hms) {
  const [h, m] = hms.split(':').map(Number);
  return `${((h + 11) % 12) + 1}:${String(m).padStart(2, '0')} ${h < 12 ? 'am' : 'pm'}`;
}

function dayLabel(date, today, tomorrow) {
  if (date === today) return 'Today';
  if (date === tomorrow) return 'Tomorrow';
  const [y, mo, d] = date.split('-').map(Number);
  return new Date(Date.UTC(y, mo - 1, d, 12)).toLocaleDateString('en-US', { timeZone: 'UTC', weekday: 'long', month: 'short', day: 'numeric' });
}

function render(classes, now) {
  const today = ymd(now);
  const tomorrow = ymd(new Date(now.getTime() + 864e5));
  const byDay = new Map();
  for (const c of classes) {
    if (!byDay.has(c.start_date)) byDay.set(c.start_date, []);
    byDay.get(c.start_date).push(c);
  }
  if (!byDay.size) {
    return '<p class="sched-empty">No upcoming classes are published yet. See the <a href="/book-now">booking calendar</a>.</p>';
  }
  let out = '';
  for (const [date, list] of [...byDay].sort()) {
    out += `<h2 class="sched-day" id="d-${date}">${esc(dayLabel(date, today, tomorrow))}</h2>\n<ul class="sched-list">\n`;
    for (const c of list.sort((a, b) => a.start_time.localeCompare(b.start_time))) {
      const type = (c.class_type?.name || c.name).replace(/\s*\(\d+ min\)/, '');
      const key = type.toLowerCase().split(/\s/)[0];
      const name = CLASS_PAGE[key] ? `<a href="${CLASS_PAGE[key]}">${esc(type)}</a>` : esc(type);
      const teacher = (c.instructors || []).map((i) => i.name).join(' & ');
      const mins = c.class_type?.duration ? `${c.class_type.duration} min` : '';
      const full = c.capacity > 0 && c.available_spot_count === 0;
      const book = `/book-now?_mt=${encodeURIComponent(`/classes/${c.id}/reserve`)}`;
      out += `  <li class="sched-item">
    <span class="sched-time">${clock(c.start_time)}</span>
    <span class="sched-what"><strong>${name}</strong><span>${esc([teacher, mins].filter(Boolean).join(' · '))}</span></span>
    <a class="sched-book${full ? ' is-full' : ''}" href="${book}">${full ? 'Join waitlist' : 'Book'}</a>
  </li>\n`;
    }
    out += '</ul>\n';
  }
  return out;
}

export default async function handler(req) {
  const origin = new URL(req.url).origin;
  const shellRes = await fetch(`${origin}/schedule.html`);
  if (!shellRes.ok) return Response.redirect(`${origin}/book-now`, 302);
  const shell = await shellRes.text();
  const now = new Date();
  const headers = { 'content-type': 'text/html; charset=utf-8' };
  try {
    const url = `${API}?location=${LOCATION}&min_start_date=${ymd(now)}&max_start_date=${ymd(new Date(now.getTime() + (DAYS - 1) * 864e5))}&page_size=200`;
    const r = await fetch(url, { headers: { accept: 'application/json' } });
    if (!r.ok) throw new Error(`mariana ${r.status}`);
    const classes = ((await r.json()).results || []).filter((c) => !c.is_cancelled && new Date(c.start_datetime) > now);
    const live = `<!--LIVE-->\n${render(classes, now)}<!--/LIVE-->`;
    headers['cache-control'] = 'public, max-age=0, s-maxage=300, stale-while-revalidate=600';
    return new Response(shell.replace(/<!--LIVE-->[\s\S]*?<!--\/LIVE-->/, live), { headers });
  } catch (e) {
    // Booking system unreachable: serve the shell's static fallback, cached briefly.
    headers['cache-control'] = 'public, max-age=0, s-maxage=60';
    return new Response(shell, { headers });
  }
}
