import html
import re
from django.utils.safestring import mark_safe

LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+|/[^\s)]*)\)")


def _inline(text):
    escaped = html.escape(text, quote=True)
    escaped = LINK_RE.sub(lambda m: f'<a href="{html.escape(m.group(2), quote=True)}" rel="nofollow noopener">{m.group(1)}</a>', escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*", r"<em>\1</em>", escaped)
    return escaped


def render_article_body(source):
    """Render a small Markdown subset while escaping all authored HTML."""
    blocks = []
    paragraph, list_items, list_kind, code_lines = [], [], None, None

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            blocks.append(f"<p>{_inline(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_list():
        nonlocal list_items, list_kind
        if list_items:
            tag = "ol" if list_kind == "ol" else "ul"
            blocks.append(f"<{tag}>" + "".join(f"<li>{_inline(item)}</li>" for item in list_items) + f"</{tag}>")
            list_items, list_kind = [], None

    for raw in source.splitlines():
        line = raw.rstrip()
        if code_lines is not None:
            if line.startswith("```"):
                blocks.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines = None
            else:
                code_lines.append(line)
            continue
        if line.startswith("```"):
            flush_paragraph(); flush_list(); code_lines = []; continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        bullet = re.match(r"^\s*[-*]\s+(.+)$", line)
        ordered = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        if heading:
            flush_paragraph(); flush_list(); level = min(len(heading.group(1)) + 1, 6)
            blocks.append(f"<h{level}>{_inline(heading.group(2))}</h{level}>")
        elif bullet or ordered:
            flush_paragraph(); kind = "ul" if bullet else "ol"
            if list_kind and list_kind != kind:
                flush_list()
            list_kind = kind; list_items.append((bullet or ordered).group(1))
        elif not line.strip():
            flush_paragraph(); flush_list()
        else:
            flush_list(); paragraph.append(line)
    flush_paragraph(); flush_list()
    if code_lines is not None:
        blocks.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
    return mark_safe("\n".join(blocks))
