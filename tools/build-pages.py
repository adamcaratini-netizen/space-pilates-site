#!/usr/bin/env python3
"""Builds the content pages (pricing, classes, guides) from team.html's shell so they
share its nav, footer and styles. Facts live in FACTS below; edit them there, rerun:

    python3 tools/build-pages.py

Prices come from the Mariana Tek storefront (/buy-now). Instructors per class come from
the live schedule. Both change: re-check before editing copy that quotes them.
"""
import html, json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mdlite  # noqa: E402

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
        "benefits": [
            "**Core strength and control:** the deep abdominals, back and hips working together",
            "**Alignment:** better awareness of how you stand, sit and move",
            "**Mobility:** controlled movement through the spine and hips",
            "**Low impact:** no jumping, kind to joints, scalable for every level",
            "**A foundation:** the control you build here carries into Sculpt and Strength",
        ],
        "faq": [
            ("Do I need Pilates experience?", "No. Most people who walk in have never done Pilates. Instructors cue modifications throughout, and you can rest or adjust at any point."),
            ("Is this reformer Pilates?", "No. Space is a mat studio. Space Pilates is classical mat Pilates with light props, and many classical exercises are harder on the mat because no springs assist you."),
            ("How is Space Pilates different from Space Sculpt?", "Space Pilates is slower and precise, built on the classical mat repertoire with light props. Space Sculpt is continuous and set to music, with dumbbells and bands."),
            ("What should I bring?", "Grippy socks are required (they are sold at the studio). Bring water and wear something you can move in; everything else is provided."),
        ],
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
        "benefits": [
            "**Strength and endurance:** continuous work with dumbbells, bands and bodyweight",
            "**Full-body control:** Pilates principles applied at a faster pace",
            "**Coordination:** moving with the rhythm of the room",
            "**Scalable:** lighter options cued for every move, beginner to advanced",
        ],
        "faq": [
            ("Is Space Sculpt good for beginners?", "Yes. It is listed for beginner to advanced, and instructors cue lighter options throughout. If you are brand new, a Space Pilates class first is a good way to learn the basics."),
            ("What is the music like?", "Sculpt is music-led. Expect upbeat playlists; Carey's classes lean on hip hop and dance remixes."),
            ("How is Sculpt different from Space Strength?", "Sculpt is faster and continuous, set to music. Space Strength is slower and heavier, with fewer movements done at a deliberate pace."),
        ],
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
        "benefits": [
            "**Strength for daily life:** lifting, carrying and climbing with more ease",
            "**Stability:** control around the hips, shoulders and core under load",
            "**Progression:** programming that builds week to week",
            "**Confidence with weights:** coaching on form from experienced coaches",
        ],
        "faq": [
            ("Do I need lifting experience?", "No. Space Strength is open to all levels, and coaches teach form and offer lighter options."),
            ("Who programs Space Strength?", "Co-founder Adam Caratini, who has 14 years of experience coaching strength and conditioning, functional fitness and personal training."),
            ("What equipment is used?", "Heavier dumbbells, kettlebells and resistance bands. Everything is provided."),
            ("How does it fit with Pilates?", "Pilates builds control and alignment; Strength adds load. Most members rotate through both during the week."),
        ],
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
        "benefits": [
            "**Mobility:** easing stiffness through hips, back and shoulders",
            "**Breath:** slower, fuller breathing practiced on purpose",
            "**Recovery:** a counterweight to Sculpt and Strength days",
            "**A pause:** time to slow down, reset and reconnect",
        ],
        "faq": [
            ("Do I need to be flexible?", "No. Space Yoga is restorative and open to all levels. Flexibility is something you build, not a requirement to start."),
            ("Is Space Yoga a workout?", "It is a restoration, not a challenge to push through: mobility, breath and release, drawn from restorative and gentle vinyasa yoga."),
            ("How often should I take yoga?", "A good starting pattern is one yoga class a week alongside Pilates, Sculpt or Strength, as a recovery day."),
        ],
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
    .content ol { margin: 0 0 20px 22px; }
    .byline { font-size: 0.86rem; color: var(--text-light); margin: 0 0 28px; padding-bottom: 20px; border-bottom: 1px solid var(--line); }
    .byline strong { color: var(--text-dark); font-weight: 500; }
    .cta-box { background: var(--cream); border: 1px solid var(--line); padding: 26px; margin: 40px 0 8px; }
    .cta-box p { margin-bottom: 10px; }
    .related { margin-top: 40px; }
    .hub-section { margin-bottom: 8px; }
    @media (max-width: 640px) { .facts, .card-list { grid-template-columns: 1fr; } }
"""

FOOTER_LINKS = """      <a href="/">Home</a>
      <a href="/classes">Classes</a>
      <a href="/learn">Learn</a>
      <a href="/pricing">Pricing</a>
      <a href="/team">The Team</a>
      <a href="/book-now">Schedule</a>
      <a href="/privacy-policy">Privacy</a>
      <a href="/terms">Terms</a>"""

UPDATED = "Updated October 2026."

NAV_LINKS = ('<a class="nav-link" href="/classes">Classes</a>\n      <a class="nav-link" href="/learn">Learn</a>\n'
             '      <a class="nav-link" href="/pricing">Pricing</a>\n      <a class="nav-link" href="/team">Team</a>')

CAREY = {"@type": "Person", "@id": SITE + "/team#carey", "name": "Carey Caratini",
         "jobTitle": "Founder and Pilates instructor, licensed mental health therapist",
         "description": "Pilates instructor, NASM certified personal trainer and licensed mental health therapist with a master's in Clinical Mental Health Counseling.",
         "worksFor": {"@id": SITE + "/#studio"}, "url": SITE + "/team"}
AUTHOR_LINE = ('By <strong>Carey Caratini</strong>, founder of Space Pilates + Wellness Society. '
               'Pilates instructor, NASM certified personal trainer and licensed mental health therapist.')

# ---- articles (content/learn/*.md), loaded first so class pages can link to them
ARTICLES = {}
for f in sorted((ROOT / "content" / "learn").glob("*.md")):
    meta, md = mdlite.parse(f.read_text(), f.name)
    if meta["slug"] != f.stem:
        raise SystemExit(f"{f.name}: slug {meta['slug']!r} does not match filename")
    if meta["class"] not in CLASSES:
        raise SystemExit(f"{f.name}: unknown class {meta['class']!r}")
    body_html, faq = mdlite.render(md, f.name)
    ARTICLES[f.stem] = dict(meta, html=body_html, faq=faq, words=len(re.findall(r"[A-Za-z']+", md)))
for slug, a in ARTICLES.items():
    for r in a["related"] + [a["pillar"]]:
        if r not in ARTICLES:
            raise SystemExit(f"{slug}: links to unknown article {r!r}")
PILLARS = [s for s, a in ARTICLES.items() if a["type"] == "pillar"]


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
    out = out.replace('<a class="nav-link" href="/about">The Studio</a>', NAV_LINKS)
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


def related_html(slugs, heading="Related reading"):
    slugs = [x for x in slugs if x in ARTICLES]
    if not slugs:
        return ""
    items = "\n".join(f'        <a href="/learn/{x}"><strong>{esc(ARTICLES[x]["title"])}</strong><span>{esc(ARTICLES[x]["description"])}</span></a>' for x in slugs)
    return f'      <h2 class="related">{esc(heading)}</h2>\n      <div class="card-list">\n{items}\n      </div>'


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
      <h2>Benefits</h2>
      <ul>
{chr(10).join('        <li>' + mdlite.inline(b) + '</li>' for b in c['benefits'])}
      </ul>
      <h2>Book it</h2>
      <p>{FACTS['schedule']} <a href="/book-now">See the live schedule</a>. New to Space? <a href="/intro">Try 2 weeks unlimited for $69</a>.</p>
      <h2>Questions</h2>
{faq_html(c['faq'])}
{related_html([s for s, a in ARTICLES.items() if a['class'] == k], 'Read more')}
      <p>Other formats: {others}</p>"""
    course = {"@type": "Service", "@id": f"{SITE}/classes/{k}#service", "name": f"{c['name']} class in Sanford, FL",
              "serviceType": c["short"], "description": c["lead"], "provider": business_ref(),
              "areaServed": ["Sanford, FL", "Lake Mary, FL", "Longwood, FL", "Heathrow, FL"],
              "offers": {"@type": "Offer", "price": "29", "priceCurrency": "USD", "description": "Drop-in class", "url": SITE + "/buy-now"}}
    schema_extra = [faq_schema(c["faq"], f"/classes/{k}")]
    built.append(page(f"/classes/{k}", f"{c['name']}: {c['short']} in Sanford, FL | Space Pilates",
         f"{c['name']} at Space Pilates in Downtown Sanford: {c['short'].lower()}, {c['length']}, {c['level'].lower()}. Drop-in $29 or 2 weeks unlimited for $69.",
         "Classes", c["name"] + ".", c["short"] + ".", body,
         [course, *schema_extra, breadcrumb([("Home", "/"), ("Classes", "/classes"), (c["name"], f"/classes/{k}")])]))

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


# ---- /learn/<slug> articles
PILLAR_LABEL = {s: re.sub(r"[:|].*$", "", ARTICLES[s]["title"]).strip() for s in PILLARS}

for slug, a in ARTICLES.items():
    c = CLASSES[a["class"]]
    pillar = a["pillar"]
    crumbs = [("Home", "/"), ("Learn", "/learn")]
    if pillar != slug:
        crumbs.append((PILLAR_LABEL.get(pillar, ARTICLES[pillar]["title"]), f"/learn/{pillar}"))
    crumbs.append((a["title"], f"/learn/{slug}"))
    back = "" if pillar == slug else f'      <p>Part of the guide: <a href="/learn/{pillar}">{esc(ARTICLES[pillar]["title"])}</a></p>\n'
    body = f"""      <p class="byline">{AUTHOR_LINE}</p>
{a['html']}
      <div class="cta-box">
        <p><strong>Try it at Space.</strong> {esc(c['name'])}: {esc(c['short'].lower())}, {esc(c['length'])}. <a href="/classes/{a['class']}">About the class</a> &nbsp;·&nbsp; <a href="/intro">2 weeks unlimited for $69</a></p>
      </div>
{back}{related_html(a['related'])}"""
    art = {"@type": "Article", "@id": f"{SITE}/learn/{slug}#article", "headline": a["title"], "description": a["description"],
           "author": CAREY, "publisher": business_ref(), "datePublished": a.get("date", "2026-10-12"),
           "dateModified": a.get("date", "2026-10-12"), "mainEntityOfPage": f"{SITE}/learn/{slug}",
           "image": f"{SITE}/assets/og-cover.jpg", "wordCount": a["words"],
           "about": {"@type": "Thing", "name": PILLAR_LABEL.get(pillar, a["title"])}}
    schema = [art, breadcrumb(crumbs)]
    if a["faq"]:
        schema.append(faq_schema(a["faq"], f"/learn/{slug}"))
    built.append(page(f"/learn/{slug}", f"{a['title']} | Space Pilates Sanford", a["description"],
                      "Guide" if a["type"] == "pillar" else "Learn", a["title"], a["description"], body, schema))

# ---- /learn hub
START_HERE = [x for x in ["pilates-for-beginners", "what-to-wear-to-pilates", "how-often-should-you-do-pilates",
                          "mat-vs-reformer-pilates"] if x in ARTICLES]
sections = [related_html(START_HERE, "Start here")]
for pslug in PILLARS:
    members = [pslug] + sorted(x for x, a in ARTICLES.items() if a["pillar"] == pslug and x != pslug and x not in START_HERE)
    sections.append(related_html(members, PILLAR_LABEL[pslug]))
NEAR_YOU = """      <h2 class="related">Near you</h2>
      <div class="card-list">
        <a href="/pilates-lake-mary"><strong>Pilates near Lake Mary</strong><span>A short drive up I-4 to Historic Downtown Sanford.</span></a>
        <a href="/classes"><strong>The four Space formats</strong><span>Pilates, Sculpt, Strength and Yoga, explained.</span></a>
      </div>"""
sections.append(NEAR_YOU)
body = ("      <p>Guides on Pilates, yoga and strength from Space Pilates + Wellness Society in Historic Downtown Sanford. "
        "Written by founder Carey Caratini, a Pilates instructor and licensed mental health therapist, with strength programming "
        "from co-founder Adam Caratini (14 years coaching).</p>\n" + "\n".join(x for x in sections if x))
built.append(page("/learn", "Learn: Pilates, Yoga & Strength Guides | Space Pilates Sanford",
                  "Guides to the benefits of Pilates, yoga and strength training, beginner tips and how to choose a class, from Space Pilates in Sanford, FL.",
                  STUDIO, "Learn.", "Pilates, yoga and strength, explained by the people who teach it.", body,
                  [{"@type": "CollectionPage", "@id": SITE + "/learn#hub", "name": "Learn", "publisher": business_ref(),
                    "hasPart": [{"@type": "Article", "headline": a["title"], "url": f"{SITE}/learn/{s}"} for s, a in ARTICLES.items()]},
                   breadcrumb([("Home", "/"), ("Learn", "/learn")])]))

# ---- patch the hand-written pages (idempotent): same destinations everywhere
MENU_ITEMS = "\n".join(f'      <li><a href="{href}" class="menu-link">{label}</a></li>' for href, label in [
    ("/", "Home"), ("/classes", "Classes"), ("/learn", "Learn"), ("/pricing", "Pricing"),
    ("/book-now", "Book a Class"), ("/buy-now", "Memberships"), ("/team", "Meet the Team")])
CARD_TARGET = {"PILATES": "pilates", "STRENGTH": "strength", "SCULPT": "sculpt", "YOGA": "yoga"}
generated = set(built)
for f in sorted(ROOT.glob("*.html")):
    if f.stem in ("mariana-tools", "book-a-call", "waiver", "about") or f"/{f.stem}" in generated:
        continue
    s = o = f.read_text()
    s = re.sub(r'(<ul class="menu-nav">\n).*?(\n    </ul>)', lambda m: m.group(1) + MENU_ITEMS + m.group(2), s, count=1, flags=re.S)
    s = s.replace('<a class="nav-link" href="/about">The Studio</a>', NAV_LINKS)
    footer = re.search(r'<div class="footer-links">.*?</div>', s, re.S)
    if footer and 'href="/learn"' not in footer.group(0):
        s = s.replace(footer.group(0), footer.group(0).replace('<a href="/classes">Classes</a>', '<a href="/classes">Classes</a>\n      <a href="/learn">Learn</a>', 1), 1)
    if f.name == "index.html":
        def card(m):
            name = re.search(r'<span class="card-bold">(PILATES|STRENGTH|SCULPT|YOGA)</span>', m.group(0))
            if not name:
                return m.group(0)
            target = f"/classes/{CARD_TARGET[name.group(1)]}"
            label = f'aria-label="About Space {name.group(1).title()}"'
            return re.sub(r'<a class="circle-arrow" href="[^"]*"( aria-label="[^"]*")?>', f'<a class="circle-arrow" href="{target}" {label}>', m.group(0), count=1)
        s = re.sub(r'<div class="class-card .*?<a class="circle-arrow"[^>]*>', card, s, flags=re.S)
    if s != o:
        f.write_text(s)

# ---- sitemap, llms.txt, routes
SITEMAP = ["/", "/intro", "/classes", *[f"/classes/{k}" for k in CLASSES], "/pricing", "/learn",
           *[f"/learn/{s}" for s in ARTICLES], "/pilates-lake-mary", "/team", "/book-now", "/buy-now"]
(ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                  + "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>2026-10-12</lastmod></url>\n" for u in SITEMAP) + "</urlset>\n")

llms = (ROOT / "llms.txt").read_text()
llms = re.sub(r"\n## Guides \(by Carey Caratini\)\n.*\Z", "", llms, flags=re.S).rstrip("\n") + "\n"
llms = llms.replace(f"- [Mat vs reformer Pilates guide]({SITE}/mat-vs-reformer-pilates)\n", f"- [Learn: guides on Pilates, yoga and strength]({SITE}/learn)\n")
llms += "\n## Guides (by Carey Caratini)\n" + "".join(f"- [{a['title']}]({SITE}/learn/{s}): {a['description']}\n" for s, a in ARTICLES.items())
(ROOT / "llms.txt").write_text(llms)

v = json.loads((ROOT / "vercel.json").read_text())
LEARN_SRCS = ("/mat-vs-reformer-pilates", "/learn", "/learn/(?<slug>[a-z0-9-]+)")
routes = [r for r in v["routes"] if r.get("src") not in LEARN_SRCS]
catch = routes.pop()
assert catch.get("src") == "/(.*)", "catch-all route must stay last"
routes.insert(0, {"src": "/mat-vs-reformer-pilates", "status": 301, "headers": {"Location": "/learn/mat-vs-reformer-pilates"}})
routes += [{"src": "/learn", "dest": "/learn.html"}, {"src": "/learn/(?<slug>[a-z0-9-]+)", "dest": "/learn/$slug.html"}, catch]
v["routes"] = routes
(ROOT / "vercel.json").write_text(json.dumps(v, indent=2) + "\n")
stale = ROOT / "mat-vs-reformer-pilates.html"
if stale.exists():
    stale.unlink()

print("\n".join(built))
import subprocess  # noqa: E402
sys.exit(subprocess.call([sys.executable, str(ROOT / "tools" / "check-site.py")]))
