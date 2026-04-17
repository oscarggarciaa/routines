#!/usr/bin/env python3
"""
Weekly Claude Digest
Busca novedades sobre Claude (modelos, tools, GitHub, YouTube, foros)
y envía un resumen por email cada semana.
"""

import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

import anthropic

# ── Configuración ─────────────────────────────────────────────────────────────
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "ogarcia@seidor.es")
SMTP_HOST       = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT       = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER       = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD   = os.environ.get("SMTP_PASSWORD", "")
SENDER_EMAIL    = os.environ.get("SENDER_EMAIL", SMTP_USER)
ANTHROPIC_KEY   = os.environ.get("ANTHROPIC_API_KEY", "")

SEARCH_PROMPT = """
Eres un asistente experto en IA. Realiza búsquedas exhaustivas en internet y recopila
TODO lo publicado en los ÚLTIMOS 7 DÍAS relacionado con Claude (el modelo de Anthropic).

Busca en estas fuentes y categorías:

## 1. NUEVOS MODELOS Y ACTUALIZACIONES
- Anuncios oficiales de Anthropic (anthropic.com/news, blog)
- Nuevas versiones de Claude (Claude 4, Claude 3.x, Haiku, Sonnet, Opus...)
- Cambios en la API, nuevos endpoints, nuevas capacidades del modelo

## 2. NUEVAS FEATURES Y TOOLS
- Nuevas herramientas integradas (web search, code execution, files...)
- Nuevas capacidades (extended thinking, memory, vision...)
- Cambios en Claude Code, Claude.ai, API
- MCP (Model Context Protocol) novedades

## 3. GITHUB - REPOSITORIOS RELEVANTES
- Repos nuevos o actualizados con integraciones de Claude
- Frameworks, SDKs, wrappers nuevos para Claude
- Agentes y sistemas multi-agente basados en Claude
- Herramientas de productividad que usan Claude

## 4. YOUTUBE - VIDEOS RECIENTES
- Tutoriales nuevos sobre Claude o Claude Code
- Demostraciones de nuevas capacidades
- Reviews y comparativas con otros modelos
- Canales relevantes: productivity, AI coding, prompting

## 5. TÉCNICAS Y PROMPTING
- Nuevas técnicas de prompting para Claude
- Mejores prácticas publicadas en la última semana
- Papers o artículos técnicos sobre Claude
- Casos de uso avanzados

## 6. APLICACIONES Y PRODUCTOS
- Apps nuevas construidas sobre Claude
- Integraciones en productos populares (Cursor, VS Code, etc.)
- Servicios empresariales que añaden soporte para Claude

## 7. COMUNIDAD (Reddit, HackerNews, foros)
- Hilos destacados sobre Claude esta semana
- Debates técnicos relevantes
- Trucos y descubrimientos de la comunidad

Para cada ítem encontrado incluye:
- Título descriptivo
- Resumen breve (2-3 líneas) de por qué es relevante
- URL si está disponible
- Nivel de importancia: 🔴 Alto | 🟡 Medio | 🟢 Informativo

Sé exhaustivo. Prioriza novedades de los últimos 7 días.
Responde en español.
"""


def fetch_claude_news() -> str:
    """Usa Claude API con web search para obtener las últimas novedades."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    print("  Conectando con Claude API...")
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": SEARCH_PROMPT}],
    )

    # Extraer texto final de la respuesta (puede haber bloques de tool_use)
    content_parts = []
    for block in response.content:
        if hasattr(block, "text"):
            content_parts.append(block.text)

    return "\n".join(content_parts)


def markdown_to_html(text: str) -> str:
    """Convierte markdown básico a HTML."""
    lines = text.split("\n")
    html_lines = []
    in_list = False

    for line in lines:
        # Encabezados
        if line.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h3>{line[4:]}</h3>")
        # Listas
        elif line.startswith("- ") or line.startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{_inline_md(line[2:])}</li>")
        # Líneas vacías
        elif line.strip() == "":
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("<br>")
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<p>{_inline_md(line)}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def _inline_md(text: str) -> str:
    """Convierte negrita e itálica inline."""
    import re
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\[(.+?)\]\((https?://[^\)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def build_email_html(content: str) -> tuple[str, str]:
    """Devuelve (subject, html_body)."""
    date_str = datetime.now().strftime("%d/%m/%Y")
    subject = f"Digest Semanal Claude — {date_str}"

    body_html = markdown_to_html(content)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
    max-width: 780px; margin: 0 auto; padding: 24px; color: #1a1a1a; background: #fff;
  }}
  .header {{
    background: linear-gradient(135deg, #7B3FE4 0%, #4F46E5 100%);
    color: white; padding: 28px 32px; border-radius: 12px; margin-bottom: 28px;
  }}
  .header h1 {{ margin: 0 0 6px 0; font-size: 24px; }}
  .header .subtitle {{ margin: 0; opacity: 0.85; font-size: 14px; }}
  h2 {{
    color: #7B3FE4; border-left: 4px solid #7B3FE4;
    padding-left: 12px; margin-top: 32px;
  }}
  h3 {{ color: #333; margin-top: 20px; }}
  ul {{ padding-left: 20px; }}
  li {{ margin-bottom: 8px; line-height: 1.6; }}
  p {{ line-height: 1.7; }}
  a {{ color: #7B3FE4; }}
  code {{
    background: #f3f0ff; padding: 2px 6px;
    border-radius: 4px; font-family: monospace; font-size: 13px;
  }}
  .footer {{
    margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee;
    font-size: 12px; color: #999; text-align: center;
  }}
</style>
</head>
<body>
  <div class="header">
    <h1>Digest Semanal: Lo Último de Claude</h1>
    <p class="subtitle">Generado automáticamente el {date_str} · Destinatario: {RECIPIENT_EMAIL}</p>
  </div>

  {body_html}

  <div class="footer">
    Este digest fue generado automáticamente mediante Claude API con búsqueda web.<br>
    Para darte de baja o cambiar la frecuencia, edita el cron job en tu servidor.
  </div>
</body>
</html>"""

    return subject, html


def send_email(subject: str, html_body: str, plain_text: str) -> None:
    """Envía el digest por SMTP o lo imprime si SMTP no está configurado."""
    if not SMTP_USER or not SMTP_PASSWORD:
        print("\n" + "=" * 60)
        print("SMTP no configurado — imprimiendo digest en consola:")
        print("=" * 60)
        print(plain_text)
        print("=" * 60)
        print("\nConfigure SMTP_USER y SMTP_PASSWORD en el archivo .env para enviar email.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECIPIENT_EMAIL

    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_body,  "html",  "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

    print(f"Email enviado correctamente a {RECIPIENT_EMAIL}")


def load_dotenv(path: str = ".env") -> None:
    """Carga variables de entorno desde un archivo .env si existe."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main() -> int:
    load_dotenv()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY no está configurada.")
        print("Añádela al archivo .env o como variable de entorno.")
        return 1

    global RECIPIENT_EMAIL, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SENDER_EMAIL, ANTHROPIC_KEY
    RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "ogarcia@seidor.es")
    SMTP_HOST       = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT       = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER       = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD   = os.environ.get("SMTP_PASSWORD", "")
    SENDER_EMAIL    = os.environ.get("SENDER_EMAIL", SMTP_USER)
    ANTHROPIC_KEY   = os.environ.get("ANTHROPIC_API_KEY", "")

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Iniciando Digest Semanal Claude")
    print(f"  Destinatario: {RECIPIENT_EMAIL}")

    print("  Buscando novedades con Claude + web search...")
    content = fetch_claude_news()

    print("  Formateando email HTML...")
    subject, html_body = build_email_html(content)

    print("  Enviando email...")
    send_email(subject, html_body, content)

    print("Digest completado con éxito.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
