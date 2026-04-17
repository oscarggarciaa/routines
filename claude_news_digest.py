#!/usr/bin/env python3
"""
Weekly Claude AI News Digest
Searches for the latest Claude news across web, YouTube, GitHub, forums
and sends a summary email every week.
"""

import os
import sys
import smtplib
import textwrap
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from pathlib import Path
import anthropic

# ---------------------------------------------------------------------------
# Load .env if present
# ---------------------------------------------------------------------------
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

# ---------------------------------------------------------------------------
# Configuration — set these in .env or as environment variables
# ---------------------------------------------------------------------------
ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
SMTP_HOST          = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT          = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER          = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD      = os.environ.get("SMTP_PASSWORD", "")
SMTP_USE_SSL       = os.environ.get("SMTP_USE_SSL", "true").lower() == "true"
SENDER_EMAIL       = os.environ.get("SENDER_EMAIL", SMTP_USER)
RECIPIENT_EMAIL    = os.environ.get("RECIPIENT_EMAIL", "ogarcia@seidor.es")
MODEL              = "claude-sonnet-4-6"
MAX_WEB_SEARCHES   = 10


def validate_config():
    missing = []
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not SMTP_USER:
        missing.append("SMTP_USER")
    if not SMTP_PASSWORD:
        missing.append("SMTP_PASSWORD")
    if missing:
        print(f"ERROR: Missing required config variables: {', '.join(missing)}")
        print(f"Copy .env.example to .env and fill in the values.")
        sys.exit(1)


def search_claude_news() -> str:
    """Use Claude with web search to gather last week's Claude-related content."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    today     = datetime.now().strftime("%d de %B de %Y")
    last_week = (datetime.now() - timedelta(days=7)).strftime("%d de %B de %Y")

    system = (
        "Eres un investigador experto en inteligencia artificial especializado en Claude de Anthropic. "
        "Tu objetivo es encontrar y sintetizar las novedades más relevantes de la última semana. "
        "Sé exhaustivo: usa la herramienta de búsqueda múltiples veces con queries diferentes. "
        "Responde siempre en español."
    )

    user_prompt = f"""Fecha actual: {today}. Período a cubrir: última semana ({last_week} – {today}).

Busca las novedades más importantes sobre Claude de Anthropic usando estas búsquedas (hazlas todas):

1. "Claude Anthropic new model 2026" — nuevos modelos (Claude 4, Opus, Sonnet, Haiku)
2. "Claude API new features tools 2026" — nuevas herramientas, skills, capabilities
3. "site:github.com Claude MCP server tools 2026" — repos de GitHub con integraciones
4. "Claude AI YouTube tutorial demo 2026" — vídeos relevantes de YouTube
5. "Claude Anthropic Reddit forum discussion 2026" — discusiones en Reddit / HackerNews
6. "Anthropic blog announcement 2026" — posts oficiales del blog de Anthropic
7. "Claude AI app integration plugin 2026" — aplicaciones y plugins nuevos
8. "Claude computer use agent workflow 2026" — agentes, automatizaciones, workflows

Tras las búsquedas, redacta un **informe semanal completo en español** con esta estructura:

---
## 🚀 Resumen Ejecutivo
(3-4 frases con lo más importante de la semana)

## 🤖 Nuevos Modelos y Actualizaciones
(versiones, benchmarks, precios, cambios)

## 🛠️ Nuevas Herramientas y Funcionalidades
(features de la API, skills, tools use, capabilities)

## 📦 GitHub: Repos y Proyectos Destacados
(repos nuevos/actualizados con descripción y enlace)

## 🎬 YouTube: Vídeos Destacados
(título, canal, enlace, breve descripción)

## 💬 Foros y Comunidad
(Reddit, HackerNews, Discord — temas más discutidos)

## 📱 Aplicaciones e Integraciones Nuevas
(apps, plugins, integraciones relevantes)

## 📰 Noticias Oficiales de Anthropic
(blog posts, papers, anuncios)

## ⭐ Recomendación de la Semana
(el recurso más útil para mejorar el uso de Claude)
---

Incluye enlaces directos siempre que sea posible. Si no hay novedades en alguna sección, indícalo brevemente."""

    messages = [{"role": "user", "content": user_prompt}]

    response = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        system=system,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": MAX_WEB_SEARCHES,
        }],
        messages=messages,
    )

    # Collect all text blocks from the response
    parts = []
    for block in response.content:
        if hasattr(block, "text"):
            parts.append(block.text)

    return "\n\n".join(parts).strip()


def markdown_to_html(md: str) -> str:
    """Very lightweight markdown → HTML converter (no extra deps required)."""
    import re
    lines = md.splitlines()
    html_lines = []
    in_ul = False

    for line in lines:
        # Headings
        if line.startswith("## "):
            if in_ul:
                html_lines.append("</ul>"); in_ul = False
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            if in_ul:
                html_lines.append("</ul>"); in_ul = False
            html_lines.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("---"):
            if in_ul:
                html_lines.append("</ul>"); in_ul = False
            html_lines.append("<hr>")
        # Bullet points
        elif re.match(r"^[\*\-] ", line):
            if not in_ul:
                html_lines.append("<ul>"); in_ul = True
            item = line[2:]
            item = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", item)
            item = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', item)
            html_lines.append(f"<li>{item}</li>")
        # Blank lines
        elif line.strip() == "":
            if in_ul:
                html_lines.append("</ul>"); in_ul = False
            html_lines.append("")
        else:
            if in_ul:
                html_lines.append("</ul>"); in_ul = False
            line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
            line = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', line)
            html_lines.append(f"<p>{line}</p>")

    if in_ul:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def build_html_email(content: str) -> str:
    today = datetime.now().strftime("%d/%m/%Y")
    body = markdown_to_html(content)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
    max-width: 760px; margin: 0 auto; padding: 0; color: #222; background: #f9f9f9;
  }}
  .wrapper {{ background: #fff; border-radius: 12px; overflow: hidden;
              box-shadow: 0 2px 12px rgba(0,0,0,.08); }}
  .header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 30px 35px; color: #fff;
  }}
  .header h1 {{ margin: 0 0 6px; font-size: 24px; font-weight: 700; }}
  .header p  {{ margin: 0; font-size: 13px; opacity: .75; }}
  .badge {{
    display: inline-block; background: rgba(255,255,255,.15);
    border-radius: 20px; padding: 4px 12px; font-size: 12px; margin-top: 12px;
  }}
  .content {{ padding: 30px 35px; }}
  h2 {{ color: #0f3460; font-size: 18px; margin-top: 28px; margin-bottom: 8px;
        border-bottom: 2px solid #e8f0fe; padding-bottom: 6px; }}
  h3 {{ color: #16213e; font-size: 15px; margin-top: 16px; }}
  p  {{ line-height: 1.7; margin: 8px 0; }}
  ul {{ padding-left: 20px; }}
  li {{ line-height: 1.7; margin: 4px 0; }}
  a  {{ color: #cc4a1b; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  hr {{ border: none; border-top: 1px solid #eee; margin: 20px 0; }}
  strong {{ color: #0f3460; }}
  .footer {{
    background: #f5f5f5; padding: 18px 35px; font-size: 12px; color: #888;
    border-top: 1px solid #e8e8e8;
  }}
</style>
</head>
<body>
<div class="wrapper">
  <div class="header">
    <h1>🤖 Digest Semanal — Novedades de Claude</h1>
    <p>Semana del {today}</p>
    <span class="badge">Generado automáticamente con Claude {MODEL}</span>
  </div>
  <div class="content">
    {body}
  </div>
  <div class="footer">
    Este email fue generado automáticamente por tu rutina semanal de Claude Code.<br>
    Fuentes: YouTube · GitHub · Reddit · HackerNews · Blog Anthropic · Web general.<br>
    Para cancelar o modificar la frecuencia, edita el cron job en <code>crontab -e</code>.
  </div>
</div>
</body>
</html>"""


def send_email(subject: str, html_content: str, plain_content: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECIPIENT_EMAIL

    msg.attach(MIMEText(plain_content, "plain", "utf-8"))
    msg.attach(MIMEText(html_content,  "html",  "utf-8"))

    if SMTP_USE_SSL:
        smtp_cls = smtplib.SMTP_SSL
    else:
        smtp_cls = smtplib.SMTP

    with smtp_cls(SMTP_HOST, SMTP_PORT) as smtp:
        if not SMTP_USE_SSL:
            smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

    print(f"  ✓ Email enviado a {RECIPIENT_EMAIL}")


def main():
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] Iniciando digest semanal de Claude...")

    validate_config()

    print("  → Buscando novedades en la web...")
    content = search_claude_news()

    if not content:
        print("  ✗ No se obtuvo contenido. Abortando.")
        sys.exit(1)

    today   = datetime.now().strftime("%d/%m/%Y")
    week_no = datetime.now().isocalendar()[1]
    subject = f"🤖 Novedades Claude — Semana {week_no} ({today})"

    print("  → Construyendo email...")
    html_content  = build_html_email(content)
    plain_content = f"Novedades de Claude — Semana {week_no} ({today})\n\n{content}"

    print("  → Enviando email...")
    send_email(subject, html_content, plain_content)

    print(f"[{datetime.now():%Y-%m-%d %H:%M}] ¡Completado!")


if __name__ == "__main__":
    main()
