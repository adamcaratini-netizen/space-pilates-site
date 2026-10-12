import nodemailer from 'nodemailer';

const GMAIL_USER = process.env.GMAIL_USER;
const GMAIL_PASS = process.env.GMAIL_PASS;
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { name, email, phone, source } = req.body || {};
  if (!name || !email) return res.status(400).json({ error: 'Name and email required.' });

  try {
    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: { user: GMAIL_USER, pass: GMAIL_PASS },
    });

    await transporter.sendMail({
      from: `"Space Pilates Presale" <${GMAIL_USER}>`,
      to: GMAIL_USER,
      subject: `New Presale Lead — ${name}`,
      html: `
        <div style="font-family:sans-serif;max-width:560px;margin:0 auto;padding:32px;color:#2C1A0F;background:#FDFAF6;">
          <h2 style="margin:0 0 24px;font-size:1.3rem;font-weight:400;">New Presale Signup — Space Pilates</h2>
          <table style="width:100%;border-collapse:collapse;">
            <tr><td style="padding:10px 0;border-bottom:1px solid #E8D9CA;font-weight:600;width:160px;">Name</td><td style="padding:10px 0;border-bottom:1px solid #E8D9CA;">${esc(name)}</td></tr>
            <tr><td style="padding:10px 0;border-bottom:1px solid #E8D9CA;font-weight:600;">Email</td><td style="padding:10px 0;border-bottom:1px solid #E8D9CA;"><a href="mailto:${esc(email)}" style="color:#B8785A;">${esc(email)}</a></td></tr>
            <tr><td style="padding:10px 0;border-bottom:1px solid #E8D9CA;font-weight:600;">Phone</td><td style="padding:10px 0;border-bottom:1px solid #E8D9CA;">${esc(phone) || '—'}</td></tr>
            <tr><td style="padding:10px 0;font-weight:600;">How they heard</td><td style="padding:10px 0;">${esc(source) || '—'}</td></tr>
          </table>
          <p style="margin-top:32px;font-size:0.75rem;color:#A07B62;">Space Pilates + Wellness Society — spacepilatesandwellness.com</p>
        </div>
      `,
    });

    return res.status(200).json({ success: true });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Failed to submit.' });
  }
}
