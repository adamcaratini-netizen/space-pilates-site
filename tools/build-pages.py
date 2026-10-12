#!/usr/bin/env python3
"""Builds the content pages (pricing, classes, guides) from team.html's shell so they
share its nav, footer and styles. Facts live in FACTS below; edit them there, rerun:

    python3 tools/build-pages.py

Prices come from the Mariana Tek storefront (/buy-now). Instructors per class come from
the live schedule. Both change: re-check before editing copy that quotes them.
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://spacepilatesandwellness.com"
STUDIO = "Space Pilates + Wellness Society"

FACTS = {
    "address": "307 E 2nd St, Sanford, FL 32771",
    "phone": "(321) 249-2262",
    "tel": "+13212492262",
    "email": "hi@spacepilatesandwellness.com",
    "class_size": 15,
    "schedule": "Classes run from 6:00 AM to 6:30 PM on weekdays, with Saturday and Sunday morning classes.",
}

# Mariana Tek storefront, read 2026-10-12.
PRICES = [
    ("Two Week Intro Offer", 69, "Unlimited classes for 2 weeks. New members, one time.", "intro"),
    ("Lifestyle", 199, "Unlimited classes, billed monthly.", "membership"),
    ("Routine", 149, "8 classes per month, billed monthly.", "membership"),
    ("Reset", 89, "4 classes per month, billed monthly.", "membership"),
    ("Drop In Class", 29, "One class.", "pack"),
    ("10 Class Pack", 230, "10 classes ($23 per class).", "pack"),
]

CLASSES = {
    "pilates": {
        "name": "Space Pilates",
        "short": "Classical mat Pilates",
        "level": "All levels welcome",
        "length": "45 to 50 minutes",
        "equipment": "Mat, with light props: rings, bands and light weights",
        "teachers": ["Alejandra Arispe", "Camryn Stephens", "Sherrell Carter"],
        "lead": "A modern take on classical mat Pilates, built around breath, control, precision and intentional movement. Space Pilates strengthens the core, improves alignment and builds the foundation for everything else you do.",
        "expect": [
            "The classical mat repertoire, taught with clear cueing and modifications for every level",
            "Slow, controlled work for the deep core, hips and back",
            "Light props (rings, bands, light weights) to add challenge without impact",
            "A calm room: no leaderboard, nothing to prove",
        ],
        "for": "Anyone new to Pilates, anyone returning to movement, and anyone who wants the foundation done properly. Most members start here.",
    },
    "sculpt": {
        "name": "Space Sculpt",
        "short": "Rhythm-driven strength set to music",
        "level": "Beginner to advanced",
        "length": "45 to 55 minutes",
        "equipment": "Dumbbells, bands and bodyweight",
        "teachers": ["Carey Caratini", "Alejandra Arispe", "Jayson LaFortune", "Camryn Stephens"],
        "lead": "Power in motion. Space Sculpt blends Pilates-inspired movement with dumbbells, bands and bodyweight, all set to the rhythm of the room. A faster, continuous class that builds strength, endurance and full-body control.",
        "expect": [
            "Continuous, music-led sequences (expect hip hop and dance remixes)",
            "Pilates-inspired strength with dumbbells, bands and bodyweight",
            "A quicker pace than Space Pilates, with options to scale every move",
            "The most scheduled format at Space, with classes most days of the week",
        ],
        "for": "People who like to move to music and want strength and stamina in one class. New members are welcome; instructors cue lighter options throughout.",
    },
    "strength": {
        "name": "Space Strength",
        "short": "Slower, heavier strength training",
        "level": "All levels welcome",
        "length": "45 to 50 minutes",
        "equipment": "Heavier dumbbells, kettlebells and resistance bands",
        "teachers": ["Carey Caratini", "Adam Caratini"],
        "lead": "Strength training, refined. Using heavier dumbbells, kettlebells and resistance bands, Space Strength builds strength, stability and resilience through purposeful, progressive movement.",
        "expect": [
            "Progressive strength work, programmed by co-founder Adam Caratini (14 years coaching strength and conditioning)",
            "Fewer, heavier movements done well, at a deliberate pace",
            "Pilates principles of control and alignment applied to lifting",
            "Coaching on form so you can progress safely week to week",
        ],
        "for": "Anyone who wants to get stronger and more durable for daily life. No lifting experience needed.",
    },
    "yoga": {
        "name": "Space Yoga",
        "short": "Restorative yoga",
        "level": "All levels welcome",
        "length": "45 to 60 minutes",
        "equipment": "Mat and studio props",
        "teachers": ["Jenny Jump"],
        "lead": "Yoga for restoration. Space Yoga blends mobility, breath, balance and purposeful movement to improve how your body feels and moves, while creating space to slow down, reset and reconnect.",
        "expect": [
            "Mobility and breath-led movement drawn from restorative and gentle vinyasa yoga",
            "Longer holds and time to release, not a workout to push through",
            "A natural counterpart to Pilates, Sculpt and Strength days",
        ],
        "for": "Anyone who wants recovery, mobility and a reset. Pairs well with the other three formats.",
    },
}

EXTRA_CSS = """
    .content { background: var(--white); padding: 72px 24px 96px; }
    .content-inner { max-width: 760px; margin: 0 auto; }
    .content h2 { font-family: 'Lora', serif; font-weight: 400; font-size: 1.7rem; color: var(--text-dark); margin: 48px 0 16px; }
    .content h2:first-child { margin-top: 0; }
    .content h3 { font-family: 'Lora', serif; font-weight: 500; font-size: 1.2rem; color: var(--text-dark); margin: 28px 0 10px; }
    .content p, .content li { font-size: 1rem; font-weight: 300; line-height: 1.75; color: var(--text-mid); }
    .content p { margin-bottom: 16px; }
    .content ul { margin: 0 0 20px 20px; }
    .content li { margin-bottom: 8px; }
    .content a { color: var(--text-dark); }
    .facts { display: grid; grid-template-columns: 1fr 1fr; gap: 1px; background: var(--line); border: 1px solid var(--line); margin: 24px 0 32px; }
    .facts div { background: var(--cream); padding: 16px 18px; }
    .facts dt { font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-light); margin-bottom: 4px; }
    .facts dd { font-size: 0.98rem; color: var(--text-dark); }
    .price-table { width: 100%; border-collapse: collapse; margin: 16px 0 32px; }
    .price-table th, .price-table td { text-align: left; padding: 14px 10px; border-bottom: 1px solid var(--line); font-size: 0.98rem; }
    .price-table th { font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-light); font-weight: 500; }
    .price-table td.price { font-family: 'Lora', serif; font-size: 1.2rem; color: var(--text-dark); white-space: nowrap; }
    .price-desc { display: block; font-size: 0.86rem; font-weight: 300; color: var(--text-light); margin-top: 4px; }
    .card-list { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 24px 0; }
    .card-list a { display: block; border: 1px solid var(--line); padding: 22px; text-decoration: none; background: var(--cream); }
    .card-list strong { display: block; font-family: 'Lora', serif; font-weight: 500; font-size: 1.15rem; color: var(--text-dark); margin-bottom: 6px; }
    .card-list span { font-size: 0.92rem; color: var(--text-mid); font-weight: 300; line-height: 1.6; }
    .updated { font-size: 0.8rem; color: var(--text-light); margin-top: 40px; }
    @media (max-width: 640px) { .facts, .card-list { grid-template-columns: 1fr; } }
"""

FOOTER_LINKS = """      <a href="/">Home</a>
      <a href="/classes">Classes</a>
      <a href="/pricing">Pricing</a>
      <a href="/team">The Team</a>
      <a href="/book-now">Schedule</a>
      <a href="/privacy-policy">Privacy</a>
      <a href="/terms">Terms</a>"""

UPDATED = "Updated October 2026."


def esc(s):
    return html.escape(s, quote=True)


def business_ref():
    return {"@type": "ExerciseGym", "@id": SITE + "/#studio", "name": STUDIO}


def breadcrumb(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p} for i, (n, p) in enumerate(trail)]}


def page(path, title, description, eyebrow, h1, subtitle, body, schema):
    shell = (ROOT / "team.html").read_text()
    head_meta = f"""  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <link rel="canonical" href="{SITE}{path}" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:image" content="{SITE}/assets/og-cover.jpg" />
  <meta property="og:url" content="{SITE}{path}" />
  <meta property="og:type" content="website" />"""
    out = re.sub(r"  <title>.*?<meta property=\"og:type\" content=\"website\" />", lambda m: head_meta, shell, count=1, flags=re.S)
    out = out.replace("  </style>", EXTRA_CSS + "  </style>", 1)
    ld = json.dumps({"@context": "https://schema.org", "@graph": schema}, indent=2, ensure_ascii=False)
    out = out.replace("</head>", f'  <script type="application/ld+json">\n{ld}\n  </script>\n</head>', 1)
    header = f"""  <!-- PAGE HEADER -->
  <header class="page-header">
    <div class="page-header-inner">
      <span class="page-eyebrow">{esc(eyebrow)}</span>
      <h1 class="page-title">{esc(h1)}</h1>
      <p class="page-subtitle">{esc(subtitle)}</p>
    </div>
  </header>

  <section class="content">
    <div class="content-inner">
{body}
      <p class="updated">{UPDATED}</p>
    </div>
  </section>

"""
    out = re.sub(r"  <!-- PAGE HEADER -->.*?(?=  <!-- CLOSING CTA -->)", lambda m: header, out, count=1, flags=re.S)
    out = re.sub(r'(<div class="footer-links">\n).*?(\n    </div>)', lambda m: m.group(1) + FOOTER_LINKS + m.group(2), out, count=1, flags=re.S)
    out = out.replace('src="assets/', 'src="/assets/')
    out = out.replace('<a class="nav-link" href="/about">The Studio</a>', '<a class="nav-link" href="/classes">Classes</a>\n      <a class="nav-link" href="/pricing">Pricing</a>')
    out = out.replace('href="/#join">Join the Society</a>\n    </div>\n  </section>', 'href="/intro">Try 2 Weeks for $69</a>\n    </div>\n  </section>')
    for ldblock in re.findall(r'<script type="application/ld\+json">(.*?)</script>', out, re.S):
        json.loads(ldblock)
    dest = ROOT / (path.strip("/") + ".html")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out)
    return path


def facts_block(rows):
    return '      <dl class="facts">\n' + "\n".join(f"        <div><dt>{esc(k)}</dt><dd>{v}</dd></div>" for k, v in rows) + "\n      </dl>"


def faq_schema(qas, path):
    return {"@type": "FAQPage", "@id": SITE + path + "#faq", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qas]}


def faq_html(qas):
    return "\n".join(f"      <h3>{esc(q)}</h3>\n      <p>{esc(a)}</p>" for q, a in qas)


built = []

# ---- /pricing
rows = "\n".join(
    f"          <tr><td>{esc(n)}<span class=\"price-desc\">{esc(d)}</span></td><td class=\"price\">${p}</td></tr>" for n, p, d, _ in PRICES)
pricing_qas = [
    ("How much is a class at Space Pilates in Sanford?", "A single drop-in class is $29. A 10 class pack is $230, which works out to $23 per class. New members can take unlimited classes for 2 weeks for $69."),
    ("What is the best option for a new member?", "The Two Week Intro Offer: unlimited classes across all four formats (Space Pilates, Space Sculpt, Space Strength and Space Yoga) for $69, so you can find your favorites before choosing a membership."),
    ("Is there a contract?", "No long-term contract. Memberships are month to month. The intro offer is a one-time purchase with no commitment."),
    ("Which membership should I choose?", "Reset ($89, 4 classes a month) suits once a week. Routine ($149, 8 classes a month) suits twice a week. Lifestyle ($199, unlimited) is the best value from about three classes a week."),
]
body = f"""      <h2>Prices</h2>
      <p>Every option includes all four formats: Space Pilates, Space Sculpt, Space Strength and Space Yoga. Classes are capped at {FACTS['class_size']} people.</p>
      <table class="price-table">
        <thead><tr><th>Option</th><th>Price</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
      <p><a href="/intro">Start the 2 week intro for $69</a> &nbsp;·&nbsp; <a href="/buy-now">Buy a membership or pack</a></p>
      <h2>Questions</h2>
{faq_html(pricing_qas)}"""
offers = {"@type": "OfferCatalog", "name": "Memberships and class packs", "itemListElement": [
    {"@type": "Offer", "name": n, "price": str(p), "priceCurrency": "USD", "description": d, "url": SITE + "/buy-now"} for n, p, d, _ in PRICES]}
built.append(page("/pricing", "Pilates Class Prices in Sanford, FL | Space Pilates + Wellness Society",
     "Space Pilates prices: 2 weeks unlimited for $69, drop-in $29, 10 class pack $230, memberships from $89 a month. Downtown Sanford, FL.",
     STUDIO, "Pricing.", "Simple, month to month, all four formats included.", body,
     [dict(business_ref(), hasOfferCatalog=offers), faq_schema(pricing_qas, "/pricing"),
      breadcrumb([("Home", "/"), ("Pricing", "/pricing")])]))

# ---- /classes hub
cards = "\n".join(
    f'        <a href="/classes/{k}"><strong>{esc(c["name"])}</strong><span>{esc(c["short"])}. {esc(c["length"])}. {esc(c["level"])}.</span></a>'
    for k, c in CLASSES.items())
body = f"""      <h2>Four formats, one method</h2>
      <p>Space is a mat-based studio in Historic Downtown Sanford. Every class is small (up to {FACTS['class_size']} people), led by a certified instructor, and built to make you longer and stronger with nothing to prove. Most members rotate through all four formats each week.</p>
      <div class="card-list">
{cards}
      </div>
      <h2>When classes run</h2>
      <p>{FACTS['schedule']} See the <a href="/book-now">live schedule</a> to book a spot.</p>
      <h2>Your first class</h2>
      <ul>
        <li>No experience needed. Tell your instructor it is your first time.</li>
        <li>Arrive ten minutes early. Wear something you can move in.</li>
        <li>Grippy socks are required (available at the studio). Bring water; everything else is provided.</li>
        <li>New members: <a href="/intro">2 weeks unlimited for $69</a>.</li>
      </ul>"""
built.append(page("/classes", "Pilates, Sculpt, Strength & Yoga Classes in Sanford, FL | Space Pilates",
     "Four class formats at Space Pilates in Downtown Sanford: classical mat Pilates, Sculpt, Strength and restorative Yoga. Small classes, all levels.",
     STUDIO, "Classes.", "Space Pilates, Space Sculpt, Space Strength and Space Yoga.", body,
     [business_ref(), {"@type": "ItemList", "itemListElement": [
         {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/classes/{k}", "name": c["name"]} for i, (k, c) in enumerate(CLASSES.items())]},
      breadcrumb([("Home", "/"), ("Classes", "/classes")])]))

# ---- /classes/<format>
for k, c in CLASSES.items():
    others = " &nbsp;·&nbsp; ".join(f'<a href="/classes/{o}">{esc(oc["name"])}</a>' for o, oc in CLASSES.items() if o != k)
    body = f"""{facts_block([("Format", esc(c['short'])), ("Length", esc(c['length'])), ("Level", esc(c['level'])), ("Equipment", esc(c['equipment'])), ("Class size", f"Up to {FACTS['class_size']}"), ("Where", esc(FACTS['address']))])}
      <p>{esc(c['lead'])}</p>
      <h2>What to expect</h2>
      <ul>
{chr(10).join('        <li>' + esc(e) + '</li>' for e in c['expect'])}
      </ul>
      <h2>Who it is for</h2>
      <p>{esc(c['for'])}</p>
      <h2>Who teaches it</h2>
      <p>{esc(', '.join(c['teachers']))}. Meet them on <a href="/team">the team page</a>.</p>
      <h2>Book it</h2>
      <p>{FACTS['schedule']} <a href="/book-now">See the live schedule</a>. New to Space? <a href="/intro">Try 2 weeks unlimited for $69</a>.</p>
      <p>Other formats: {others}</p>"""
    course = {"@type": "Service", "@id": f"{SITE}/classes/{k}#service", "name": f"{c['name']} class in Sanford, FL",
              "serviceType": c["short"], "description": c["lead"], "provider": business_ref(),
              "areaServed": ["Sanford, FL", "Lake Mary, FL", "Longwood, FL", "Heathrow, FL"],
              "offers": {"@type": "Offer", "price": "29", "priceCurrency": "USD", "description": "Drop-in class", "url": SITE + "/buy-now"}}
    built.append(page(f"/classes/{k}", f"{c['name']}: {c['short']} in Sanford, FL | Space Pilates",
         f"{c['name']} at Space Pilates in Downtown Sanford: {c['short'].lower()}, {c['length']}, {c['level'].lower()}. Drop-in $29 or 2 weeks unlimited for $69.",
         "Classes", c["name"] + ".", c["short"] + ".", body,
         [course, breadcrumb([("Home", "/"), ("Classes", "/classes"), (c["name"], f"/classes/{k}")])]))

# ---- /mat-vs-reformer-pilates
guide_qas = [
    ("What is the difference between mat and reformer Pilates?", "Mat Pilates is done on a mat using your own bodyweight, sometimes with small props like rings, bands and light weights. Reformer Pilates is done on a machine with a sliding carriage and springs that add or reduce resistance. Both follow the same principles: breath, control, core strength and alignment."),
    ("Is mat Pilates easier than reformer Pilates?", "Not necessarily. On a mat there are no springs to assist you, so many classical exercises are harder on the mat than on a reformer. Either can be scaled for beginners."),
    ("Which is better for beginners?", "Both work. Mat Pilates teaches you to control your own body with nothing assisting, which carries over to everything else. It is also usually more affordable, because classes do not depend on expensive machines."),
    ("Does Space Pilates have reformers?", "No. Space is a mat-based studio. Space Pilates is classical mat Pilates, and Space Sculpt and Space Strength add dumbbells, kettlebells and bands for strength."),
]
body = f"""      <p>If you are choosing a Pilates studio in Sanford, Lake Mary or Longwood, the first question is usually mat or reformer. Here is the honest difference, and where Space fits.</p>
      <h2>Mat Pilates</h2>
      <p>Mat Pilates is the original form of the method: a sequence of controlled exercises on a mat, using your own bodyweight. Small props such as rings, bands and light weights can add challenge. Because nothing assists you, it builds strength and control you can use anywhere.</p>
      <h2>Reformer Pilates</h2>
      <p>A reformer is a machine with a sliding carriage, springs and straps. The springs can add resistance or support, which lets an instructor change an exercise quickly. Reformer classes are usually smaller and priced higher, because each person needs a machine.</p>
      <h2>How to choose</h2>
      <ul>
        <li><strong>Budget:</strong> mat classes usually cost less per class.</li>
        <li><strong>Variety:</strong> at Space, mat Pilates sits alongside Sculpt, Strength and Yoga, so one membership covers core, strength and recovery.</li>
        <li><strong>Carry-over:</strong> mat work trains you to control your body with no assistance.</li>
        <li><strong>Preference:</strong> if you love the machine, a reformer studio is a good choice. Many people do both.</li>
      </ul>
      <h2>Questions</h2>
{faq_html(guide_qas)}
      <p>Try it yourself: <a href="/intro">2 weeks unlimited for $69</a> at {esc(FACTS['address'])}.</p>"""
built.append(page("/mat-vs-reformer-pilates", "Mat vs Reformer Pilates: Which Is Right for You? | Space Pilates Sanford",
     "Mat vs reformer Pilates explained: cost, difficulty and which suits beginners. From Space Pilates, a mat-based studio in Downtown Sanford, FL.",
     "Guide", "Mat vs Reformer Pilates.", "The honest difference, and how to choose.", body,
     [{"@type": "Article", "headline": "Mat vs Reformer Pilates: Which Is Right for You?", "author": {"@type": "Person", "name": "Carey Caratini"},
       "publisher": business_ref(), "datePublished": "2026-10-12", "mainEntityOfPage": SITE + "/mat-vs-reformer-pilates"},
      faq_schema(guide_qas, "/mat-vs-reformer-pilates"), breadcrumb([("Home", "/"), ("Mat vs Reformer Pilates", "/mat-vs-reformer-pilates")])]))

# ---- /pilates-lake-mary
lm_qas = [
    ("How far is Space Pilates from Lake Mary?", "Space is at 307 E 2nd St in Historic Downtown Sanford, a short drive from Lake Mary via I-4 or US 17-92, typically 15 to 20 minutes depending on where you start and traffic."),
    ("Are there early morning or after-work classes?", "Yes. Weekday classes start as early as 6:00 AM and run into the early evening, with Saturday and Sunday morning classes, which suits people commuting along I-4."),
    ("What does it cost?", "New members get 2 weeks unlimited for $69. After that, drop-ins are $29 and memberships start at $89 a month."),
]
body = f"""      <p>Lake Mary has plenty of reformer and franchise studios. If you want something smaller and more personal, Space Pilates + Wellness Society is a short drive away in Historic Downtown Sanford.</p>
      <h2>Why Lake Mary members make the drive</h2>
      <ul>
        <li><strong>Small classes</strong>, capped at {FACTS['class_size']}, taught by certified instructors.</li>
        <li><strong>Four formats in one membership</strong>: <a href="/classes/pilates">classical mat Pilates</a>, <a href="/classes/sculpt">Sculpt</a>, <a href="/classes/strength">Strength</a> and <a href="/classes/yoga">restorative Yoga</a>.</li>
        <li><strong>Founded by a licensed mental health therapist</strong>, Carey Caratini, with strength programming by Adam Caratini (14 years coaching).</li>
        <li><strong>Downtown Sanford after class</strong>: coffee, restaurants and the riverfront are a walk away.</li>
      </ul>
      <h2>Questions</h2>
{faq_html(lm_qas)}
      <p><a href="/book-now">See the schedule</a> &nbsp;·&nbsp; <a href="/intro">Start 2 weeks for $69</a></p>"""
built.append(page("/pilates-lake-mary", "Pilates Near Lake Mary, FL | Space Pilates + Wellness Society, Sanford",
     "Looking for Pilates near Lake Mary? Space Pilates in Downtown Sanford: small mat Pilates, Sculpt, Strength and Yoga classes. 2 weeks unlimited for $69.",
     STUDIO, "Pilates near Lake Mary.", "A short drive up I-4 to Historic Downtown Sanford.", body,
     [business_ref(), faq_schema(lm_qas, "/pilates-lake-mary"), breadcrumb([("Home", "/"), ("Pilates near Lake Mary", "/pilates-lake-mary")])]))

print("\n".join(built))
