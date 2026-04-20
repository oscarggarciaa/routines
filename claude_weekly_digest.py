#!/usr/bin/env python3
"""
Claude Weekly Digest
Busca las últimas novedades de Claude AI (modelos, herramientas, GitHub, apps, YouTube)
y envía un resumen por email a ogarcia@seidor.es.

Cron semanal (cada lunes 9:00):
  0 9 * * 1 /usr/bin/python3 /home/user/routines/claude_weekly_digest.py >> /home/user/routines/digest.log 2>&1

Variables de entorno necesarias (en ~/.claude_digest.env o exportadas):
  ANTHROPIC_API_KEY       - Clave API de Anthropic
  DIGEST_EMAIL_FROM       - Email remitente (cuenta Gmail)
  DIGEST_EMAIL_PASSWORD   - Contraseña de aplicación Gmail (Google App Password)
  DIGEST_EMAIL_TO         - Destinatario (por defecto: ogarcia@seidor.es)
"""

import os
import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ── Cargar variables de entorno desde archivo si existe ─────────────────────
_env_file = Path.home() / ".claude_digest.env"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# ── Configuración ────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
EMAIL_FROM = os.getenv("DIGEST_EMAIL_FROM", "")
EMAIL_PASSWORD = os.getenv("DIGEST_EMAIL_PASSWORD", "")
EMAIL_TO = os.getenv("DIGEST_EMAIL_TO", "ogarcia@seidor.es")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")

# ── Temas de búsqueda ────────────────────────────────────────────────────────
WEB_QUERIES = [
    "Claude AI new model release 2026",
    "Anthropic Claude new features tools April 2026",
    "Claude Code new skills plugins MCP 2026",
    "Claude AI GitHub repositories productivity tools 2026",
    "Anthropic Claude applications integrations 2026",
    "Claude AI agent workflows automation 2026",
    "Claude MCP server new tools April 2026",
]

YOUTUBE_QUERIES = [
    "Claude AI new features 2026 tutorial",
    "Claude Code skills plugins tutorial 2026",
    "Anthropic Claude AI productivity 2026",
]

# ── Búsqueda web ─────────────────────────────────────────────────────────────

def search_web(query: str, max_results: int = 6) -> list[dict]:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        logger.warning(f"Web search failed for '{query}': {e}")
        return []


def search_youtube(query: str, max_results: int = 5) -> list[dict]:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            return list(ddgs.videos(query, max_results=max_results))
    except Exception as e:
        logger.warning(f"YouTube search failed for '{query}': {e}")
        return []


def search_reddit_hackernews(query: str, max_results: int = 5) -> list[dict]:
    """Busca en Reddit y HackerNews via DuckDuckGo."""
    results = []
    for site in ["site:reddit.com", "site:news.ycombinator.com"]:
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                hits = list(ddgs.text(f"{site} {query}", max_results=max_results))
                results.extend(hits)
        except Exception as e:
            logger.warning(f"Forum search failed: {e}")
    return results

# ── Recopilación de datos ────────────────────────────────────────────────────

def gather_all_data() -> dict:
    week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    logger.info("Iniciando recopilación de datos...")

    web_results, youtube_results, forum_results = [], [], []

    for q in WEB_QUERIES:
        hits = search_web(q)
        web_results.extend(hits)
        logger.info(f"  Web '{q[:50]}...' → {len(hits)} resultados")

    for q in YOUTUBE_QUERIES:
        hits = search_youtube(q)
        youtube_results.extend(hits)
        logger.info(f"  YouTube '{q[:50]}...' → {len(hits)} resultados")

    forum_hits = search_reddit_hackernews("Claude AI new tools features 2026")
    forum_results.extend(forum_hits)
    logger.info(f"  Foros → {len(forum_results)} resultados")

    # Deduplicar por URL
    def dedup(items: list[dict], url_key: str) -> list[dict]:
        seen, out = set(), []
        for item in items:
            url = item.get(url_key, item.get("href", ""))
            if url and url not in seen:
                seen.add(url)
                out.append(item)
        return out

    return {
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "week_start": week_start,
        "web": dedup(web_results, "href"),
        "youtube": dedup(youtube_results, "content"),
        "forums": dedup(forum_results, "href"),
    }

# ── Generación del digest con Claude ────────────────────────────────────────

def _fmt_web(items: list[dict], limit: int = 30) -> str:
    lines = []
    for r in items[:limit]:
        title = r.get("title", "Sin título")
        url = r.get("href", r.get("url", ""))
        body = r.get("body", r.get("description", ""))[:250]
        lines.append(f"- [{title}]({url}): {body}")
    return "\n".join(lines)


def _fmt_youtube(items: list[dict], limit: int = 12) -> str:
    lines = []
    for r in items[:limit]:
        title = r.get("title", "Sin título")
        url = r.get("content", r.get("url", ""))
        desc = r.get("description", "")[:200]
        lines.append(f"- [{title}]({url}): {desc}")
    return "\n".join(lines)


def generate_digest(data: dict) -> str:
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY no configurada")

    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    web_txt = _fmt_web(data["web"])
    yt_txt = _fmt_youtube(data["youtube"])
    forum_txt = _fmt_web(data["forums"], limit=10)

    prompt = f"""Eres un asistente experto en IA. Crea un DIGEST SEMANAL en ESPAÑOL con las últimas novedades de Claude AI para Oscar García, profesional que usa Claude para mejorar su productividad en SEIDOR.

Fecha: {data['date']}
Semana desde: {data['week_start']}

═══ RESULTADOS WEB ═══
{web_txt}

═══ VIDEOS YOUTUBE ═══
{yt_txt}

═══ FOROS (Reddit / HN) ═══
{forum_txt}

Genera un email HTML profesional con estas secciones. Para cada item incluye el link clickable:

<h2>🚀 Nuevos Modelos y Versiones de Claude</h2>
<h2>🛠️ Nuevas Herramientas, Skills y MCP Tools</h2>
<h2>📁 Repositorios GitHub Destacados</h2>
<h2>📱 Aplicaciones y Casos de Uso Relevantes</h2>
<h2>🎥 Videos Recomendados (YouTube)</h2>
<h2>💬 Lo Más Comentado en Foros</h2>
<h2>💡 Consejos para Mejorar tu Productividad con Claude</h2>

Estilo: HTML limpio, fuente sans-serif, fondo #f9f9f9, secciones con borde izquierdo de color.
Solo incluye novedades REALES de los resultados. Elimina duplicados. Sé conciso pero completo.
Empieza directamente con el HTML (sin ```html ni explicaciones previas)."""

    logger.info("Generando digest con Claude...")
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text

# ── Envío de email ────────────────────────────────────────────────────────────

def send_email(subject: str, html_body: str) -> bool:
    if not EMAIL_FROM or not EMAIL_PASSWORD:
        logger.error(
            "Credenciales de email no configuradas.\n"
            "Configura DIGEST_EMAIL_FROM y DIGEST_EMAIL_PASSWORD en ~/.claude_digest.env"
        )
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
        logger.info(f"✅ Email enviado a {EMAIL_TO}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error(
            "Error de autenticación SMTP. Asegúrate de usar una 'App Password' de Google, "
            "no tu contraseña normal. Genera una en: https://myaccount.google.com/apppasswords"
        )
        return False
    except Exception as e:
        logger.error(f"Error enviando email: {e}")
        return False

# ── Guardar HTML como respaldo ────────────────────────────────────────────────

def save_digest(html: str) -> Path:
    out = Path("/home/user/routines") / f"digest_{datetime.now().strftime('%Y%m%d')}.html"
    out.write_text(html, encoding="utf-8")
    logger.info(f"Digest guardado en: {out}")
    return out

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    logger.info("═" * 60)
    logger.info("Claude Weekly Digest — inicio")
    logger.info("═" * 60)

    data = gather_all_data()
    logger.info(
        f"Datos recopilados: {len(data['web'])} web, "
        f"{len(data['youtube'])} YouTube, {len(data['forums'])} foros"
    )

    html = generate_digest(data)

    week_str = datetime.now().strftime("%d/%m/%Y")
    subject = f"[Claude Digest] Novedades semanales — {week_str}"

    sent = send_email(subject, html)
    if not sent:
        save_digest(html)

    logger.info("Claude Weekly Digest — completado")


if __name__ == "__main__":
    main()
