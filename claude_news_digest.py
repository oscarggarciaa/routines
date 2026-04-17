#!/usr/bin/env python3
"""
Weekly Claude AI News Digest
Usa `claude -p` (Claude Code CLI) para buscar noticias — sin API key propia.
Envía el resultado por email via Gmail SMTP.
"""

import os
import sys
import subprocess
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from pathlib import Path

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
# Configuration — solo necesitas SMTP_USER y SMTP_PASSWORD en .env
# ---------------------------------------------------------------------------
SMTP_HOST       = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT       = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER       = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD   = os.environ.get("SMTP_PASSWORD", "")
SMTP_USE_SSL    = os.environ.get("SMTP_USE_SSL", "true").lower() == "true"
SENDER_EMAIL    = os.environ.get("SENDER_EMAIL", SMTP_USER)
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "ogarcia@seidor.es")
CLAUDE_BIN      = os.environ.get("CLAUDE_BIN", "/opt/node22/bin/claude")


def validate_config():
    missing = []
    if not SMTP_USER:
        missing.append("SMTP_USER")
    if not SMTP_PASSWORD:
        missing.append("SMTP_PASSWORD")
    if missing:
        print(f"ERROR: Faltan variables en .env: {', '.join(missing)}")
        sys.exit(1)
    if not Path(CLAUDE_BIN).exists():
        print(f"ERROR: No se encuentra claude CLI en {CLAUDE_BIN}")
        sys.exit(1)


def search_claude_news() -> str:
    """Ejecuta `claude -p` para buscar novedades de Claude con web search."""
    today     = datetime.now().strftime("%d de %B de %Y")
    last_week = (datetime.now() - timedelta(days=7)).strftime("%d de %B de %Y")

    prompt = f"""Fecha actual: {today}. Período: última semana ({last_week} – {today}).

Eres un investigador de IA. Busca en la web (usa WebSearch múltiples veces) las novedades más importantes sobre Claude de Anthropic:

1. Nuevos modelos Claude: lanzamientos, benchmarks, precios
2. Nuevas herramientas y features de la API de Claude
3. Repositorios GitHub destacados con integraciones para Claude
4. Vídeos de YouTube relevantes sobre Claude
5. Discusiones en Reddit/HackerNews sobre Claude
6. Posts del blog oficial de Anthropic
7. Aplicaciones y plugins nuevos que usan Claude
8. Agentes, workflows y automatizaciones con Claude

Redacta un informe semanal completo en español con esta estructura exacta:

## 🚀 Resumen Ejecutivo
(3-4 frases con lo más importante)

## 🤖 Nuevos Modelos y Actualizaciones
(versiones, benchmarks, cambios)

## 🛠️ Nuevas Herramientas y Funcionalidades
(API features, skills, tool use)

## 📦 GitHub: Repos Destacados
(nombre, descripción breve, enlace)

## 🎬 YouTube: Vídeos Destacados
(título, canal, enlace)

## 💬 Foros y Comunidad
(temas más discutidos en Reddit/HackerNews)

## 📱 Aplicaciones e Integraciones
(apps y plugins nuevos)

## 📰 Noticias Oficiales de Anthropic
(blog posts, papers, anuncios)

## ⭐ Recomendación de la Semana
(el recurso más útil para mejorar el uso de Claude)

Incluye enlaces siempre que sea posible."""

    result = subprocess.run(
        [CLAUDE_BIN, "-p", prompt, "--allowedTools", "WebSearch"],
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode != 0:
        print(f"  ✗ Error ejecutando claude: {result.stderr[:500]}")
        sys.exit(1)

    return result.stdout.strip()


def markdown_to_html(md: str) -> str:
    lines = md.splitlines()
    html_lines = []
    in_ul = False

    for line in lines:
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
        elif re.match(r"^[\*\-] ", line):
            if not in_ul:
                html_lines.append("<ul>"); in_ul = True
            item = line[2:]
            item = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", item)
            item = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', item)
            html_lines.append(f"<li>{item}</li>")
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
    body  = markdown_to_html(content)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;
         max-width:760px;margin:0 auto;padding:0;color:#222;background:#f9f9f9;}}
  .wrapper {{background:#fff;border-radius:12px;overflow:hidden;
             box-shadow:0 2px 12px rgba(0,0,0,.08);}}
  .header {{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);
            padding:30px 35px;color:#fff;}}
  .header h1 {{margin:0 0 6px;font-size:24px;font-weight:700;}}
  .header p  {{margin:0;font-size:13px;opacity:.75;}}
  .badge {{display:inline-block;background:rgba(255,255,255,.15);border-radius:20px;
           padding:4px 12px;font-size:12px;margin-top:12px;}}
  .content {{padding:30px 35px;}}
  h2 {{color:#0f3460;font-size:18px;margin-top:28px;margin-bottom:8px;
       border-bottom:2px solid #e8f0fe;padding-bottom:6px;}}
  h3 {{color:#16213e;font-size:15px;margin-top:16px;}}
  p  {{line-height:1.7;margin:8px 0;}}
  ul {{padding-left:20px;}}
  li {{line-height:1.7;margin:4px 0;}}
  a  {{color:#cc4a1b;text-decoration:none;}}
  hr {{border:none;border-top:1px solid #eee;margin:20px 0;}}
  strong {{color:#0f3460;}}
  .footer {{background:#f5f5f5;padding:18px 35px;font-size:12px;color:#888;
            border-top:1px solid #e8e8e8;}}
</style>
</head>
<body>
<div class="wrapper">
  <div class="header">
    <h1>🤖 Digest Semanal — Novedades de Claude</h1>
    <p>Semana del {today}</p>
    <span class="badge">Generado automáticamente con Claude Code</span>
  </div>
  <div class="content">{body}</div>
  <div class="footer">
    Generado automáticamente cada lunes. Fuentes: YouTube · GitHub · Reddit · HackerNews · Anthropic Blog.<br>
    Para ajustar la frecuencia: <code>crontab -e</code>
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

    smtp_cls = smtplib.SMTP_SSL if SMTP_USE_SSL else smtplib.SMTP
    with smtp_cls(SMTP_HOST, SMTP_PORT) as smtp:
        if not SMTP_USE_SSL:
            smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

    print(f"  ✓ Email enviado a {RECIPIENT_EMAIL}")


def main():
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] Iniciando digest semanal de Claude...")

    validate_config()

    print("  → Buscando novedades (puede tardar 1-2 min)...")
    content = search_claude_news()

    if not content:
        print("  ✗ Sin contenido. Abortando.")
        sys.exit(1)

    week_no = datetime.now().isocalendar()[1]
    today   = datetime.now().strftime("%d/%m/%Y")
    subject = f"🤖 Novedades Claude — Semana {week_no} ({today})"

    print("  → Enviando email...")
    send_email(subject, build_html_email(content), content)

    print(f"[{datetime.now():%Y-%m-%d %H:%M}] ¡Completado!")


if __name__ == "__main__":
    main()
