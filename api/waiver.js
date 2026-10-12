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

  const {
    firstName, lastName, email, phone, dob,
    emergencyName, emergencyPhone,
    medicalConditions, medicalDetails,
    photoRelease, signature, signedAt
  } = req.body || {};

  if (!firstName || !lastName || !email || !signature) {
    return res.status(400).json({ error: 'Required fields missing.' });
  }

  const fullName = `${firstName} ${lastName}`;
  const photoText = photoRelease === 'yes' ? 'Yes — consented' : 'No — declined';

  try {
    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: { user: GMAIL_USER, pass: GMAIL_PASS },
    });

    await transporter.sendMail({
      from: `"Space Pilates Waiver" <${GMAIL_USER}>`,
      to: `${GMAIL_USER}, hi@spacepilatesandwellness.com`,
      subject: `Liability Waiver Signed — ${fullName}`,
      html: `
        <div style="font-family:sans-serif;max-width:620px;margin:0 auto;padding:32px;color:#1a1614;background:#faf8f4;">
          <h2 style="margin:0 0 8px;font-size:1.2rem;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;">Liability Waiver Signed</h2>
          <p style="margin:0 0 28px;font-size:0.85rem;color:#9a938c;">Space Pilates + Wellness Society</p>

          <table style="width:100%;border-collapse:collapse;margin-bottom:28px;">
            <tr style="background:#f0ede8;">
              <td colspan="2" style="padding:10px 14px;font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#4a4440;">Participant</td>
            </tr>
            <tr><td style="padding:10px 14px;border-bottom:1px solid #e8e0d8;font-weight:600;width:180px;">Full Name</td><td style="padding:10px 14px;border-bottom:1px solid #e8e0d8;">${esc(fullName)}</td></tr>
            <tr><td style="padding:10px 14px;border-bottom:1px solid #e8e0d8;font-weight:600;">Email</td><td style="padding:10px 14px;border-bottom:1px solid #e8e0d8;"><a href="mailto:${esc(email)}" style="color:#4a4440;">${esc(email)}</a></td></tr>
            <tr><td style="padding:10px 14px;border-bottom:1px solid #e8e0d8;font-weight:600;">Phone</td><td style="padding:10px 14px;border-bottom:1px solid #e8e0d8;">${esc(phone) || '—'}</td></tr>
            <tr><td style="padding:10px 14px;font-weight:600;">Date of Birth</td><td style="padding:10px 14px;">${esc(dob) || '—'}</td></tr>
          </table>

          <table style="width:100%;border-collapse:collapse;margin-bottom:28px;">
            <tr style="background:#f0ede8;">
              <td colspan="2" style="padding:10px 14px;font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#4a4440;">Emergency Contact</td>
            </tr>
            <tr><td style="padding:10px 14px;border-bottom:1px solid #e8e0d8;font-weight:600;width:180px;">Name</td><td style="padding:10px 14px;border-bottom:1px solid #e8e0d8;">${esc(emergencyName) || '—'}</td></tr>
            <tr><td style="padding:10px 14px;font-weight:600;">Phone</td><td style="padding:10px 14px;">${esc(emergencyPhone) || '—'}</td></tr>
          </table>

          <table style="width:100%;border-collapse:collapse;margin-bottom:28px;">
            <tr style="background:#f0ede8;">
              <td colspan="2" style="padding:10px 14px;font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#4a4440;">Health & Consent</td>
            </tr>
            <tr><td style="padding:10px 14px;border-bottom:1px solid #e8e0d8;font-weight:600;width:180px;">Medical Conditions</td><td style="padding:10px 14px;border-bottom:1px solid #e8e0d8;">${medicalConditions === 'yes' ? 'Yes — see details' : 'None reported'}</td></tr>
            <tr><td style="padding:10px 14px;border-bottom:1px solid #e8e0d8;font-weight:600;">Medical Details</td><td style="padding:10px 14px;border-bottom:1px solid #e8e0d8;">${esc(medicalDetails) || '—'}</td></tr>
            <tr><td style="padding:10px 14px;font-weight:600;">Photo/Video Release</td><td style="padding:10px 14px;">${esc(photoText)}</td></tr>
          </table>

          <table style="width:100%;border-collapse:collapse;margin-bottom:28px;">
            <tr style="background:#f0ede8;">
              <td colspan="2" style="padding:10px 14px;font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#4a4440;">Signature</td>
            </tr>
            <tr><td style="padding:10px 14px;border-bottom:1px solid #e8e0d8;font-weight:600;width:180px;">Electronic Signature</td><td style="padding:10px 14px;border-bottom:1px solid #e8e0d8;font-style:italic;font-size:1.1rem;">${esc(signature)}</td></tr>
            <tr><td style="padding:10px 14px;font-weight:600;">Signed At</td><td style="padding:10px 14px;">${esc(signedAt || new Date().toISOString())}</td></tr>
          </table>

          <p style="margin-top:32px;font-size:0.72rem;color:#9a938c;line-height:1.7;">
            This record confirms electronic acceptance of the Space Pilates + Wellness Society Liability Waiver and Release.<br>
            spacepilatesandwellness.com &mdash; hi@spacepilatesandwellness.com
          </p>
        </div>
      `,
    });

    return res.status(200).json({ success: true });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Failed to submit waiver.' });
  }
}
