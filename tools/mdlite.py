"""Minimal Markdown for the /learn articles. Supports exactly what the article brief allows:
## / ### headings, paragraphs, "- " and "1. " lists, **bold**, *italic*, [text](/path) links.
Anything else is a content error, so unknown block syntax raises instead of rendering oddly."""
import html
import re

HEADER_KEYS = ("title", "slug", "description", "type", "pillar", "class", "related")
OPTIONAL_KEYS = ("author", "reviewed", "date")


def parse(text, source="article"):
    """Split '---' frontmatter (flat key: value lines) from the Markdown body."""
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
    if not m:
        raise ValueError(f"{source}: missing --- frontmatter block")
    meta = {}
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"{source}: bad frontmatter line {line!r}")
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    missing = [k for k in HEADER_KEYS if not meta.get(k)]
    if missing:
        raise ValueError(f"{source}: frontmatter missing {missing}")
    unknown = set(meta) - set(HEADER_KEYS) - set(OPTIONAL_KEYS)
    if unknown:
        raise ValueError(f"{source}: unknown frontmatter keys {sorted(unknown)}")
    meta["related"] = [s.strip() for s in meta["related"].split(",") if s.strip()]
    return meta, m.group(2).strip() + "\n"


def inline(s):
    out = html.escape(s, quote=False)
    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>', out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", out)
    return out


def render(body, source="article"):
    """Returns (html, faq) where faq is [(question, answer)] from the '## Questions' section."""
    blocks = re.split(r"\n\s*\n", body.strip())
    out, faq, in_questions, pending_q = [], [], False, None
    for b in blocks:
        lines = b.strip("\n").splitlines()
        first = lines[0]
        if first.startswith("### "):
            if len(lines) > 1:
                raise ValueError(f"{source}: text directly under heading {first!r}; add a blank line")
            q = first[4:].strip()
            out.append(f"      <h3>{inline(q)}</h3>")
            pending_q = q if in_questions else None
        elif first.startswith("## "):
            if len(lines) > 1:
                raise ValueError(f"{source}: text directly under heading {first!r}; add a blank line")
            t = first[3:].strip()
            in_questions = t.lower() == "questions"
            pending_q = None
            out.append(f"      <h2>{inline(t)}</h2>")
        elif first.startswith("#"):
            raise ValueError(f"{source}: only ## and ### headings are allowed: {first!r}")
        elif all(re.match(r"- ", l) for l in lines):
            out.append("      <ul>\n" + "\n".join(f"        <li>{inline(l[2:].strip())}</li>" for l in lines) + "\n      </ul>")
        elif all(re.match(r"\d+\. ", l) for l in lines):
            items = [inline(re.sub(r"^\d+\. ", "", l).strip()) for l in lines]
            out.append("      <ol>\n" + "\n".join(f"        <li>{i}</li>" for i in items) + "\n      </ol>")
        elif re.match(r"(- |\d+\. |>|\||```|<)", first):
            raise ValueError(f"{source}: unsupported or mixed block starting {first[:40]!r}")
        else:
            para = " ".join(l.strip() for l in lines)
            out.append(f"      <p>{inline(para)}</p>")
            if pending_q:
                faq.append((pending_q, re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", para).replace("**", "").replace("*", "")))
                pending_q = None
    return "\n".join(out), faq
