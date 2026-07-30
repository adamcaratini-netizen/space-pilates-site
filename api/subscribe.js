import nodemailer from 'nodemailer';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { firstName, lastName, email, interest } = req.body || {};

  if (!firstName || !email) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const transport = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: 'adam.caratini@gmail.com',
      pass: process.env.GMAIL_APP_PASSWORD,
    },
  });

  const name = [firstName, lastName].filter(Boolean).join(' ');
  const interestLine = interest ? `\nInterest: ${interest}` : '';

  try {
    await transport.sendMail({
      from: '"SPACE Pilates" <adam.caratini@gmail.com>',
      to: 'hi@spacepilatesandwellness.com',
      subject: `New lead: ${name} — SPACE Pilates`,
      text: `New founding member inquiry\n\nName: ${name}\nEmail: ${email}${interestLine}\n\nSubmitted via space-pilates.vercel.app/coming-soon`,
      html: `
        <div style="font-family:sans-serif;max-width:520px;padding:32px;background:#fff;border:1px solid #eee;">
          <p style="font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#C4937E;margin:0 0 20px;">SPACE Pilates — New Lead</p>
          <table style="width:100%;border-collapse:collapse;font-size:14px;color:#1A1714;">
            <tr><td style="padding:10px 0;border-bottom:1px solid #eee;color:#8A807A;width:120px;">Name</td><td style="padding:10px 0;border-bottom:1px solid #eee;font-weight:600;">${name}</td></tr>
            <tr><td style="padding:10px 0;border-bottom:1px solid #eee;color:#8A807A;">Email</td><td style="padding:10px 0;border-bottom:1px solid #eee;"><a href="mailto:${email}" style="color:#1A1714;">${email}</a></td></tr>
            ${interest ? `<tr><td style="padding:10px 0;color:#8A807A;">Interest</td><td style="padding:10px 0;">${interest}</td></tr>` : ''}
          </table>
          <p style="font-size:11px;color:#aaa;margin:24px 0 0;">Submitted via SPACE coming-soon page</p>
        </div>
      `,
    });

    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('Email error:', err);
    return res.status(500).json({ error: 'Failed to send' });
  }
}
