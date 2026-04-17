#!/usr/bin/env python3
"""
Weekly Claude AI News Digest
Usa `claude -p` para buscar noticias y crear un borrador en Gmail via MCP.
El borrador aparece en osky01313@gmail.com listo para enviar con un click.
"""

import os
import sys
import subprocess
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
CLAUDE_BIN      = os.environ.get("CLAUDE_BIN", "/opt/node22/bin/claude")
RECIPIENT_EMAIL = "ogarcia@seidor.es"
MCP_CONFIG_PATH = os.environ.get("MCP_CONFIG_PATH", "")  # ruta al mcp-config de Gmail


def find_mcp_config() -> str:
    """Busca el archivo mcp-config con Gmail activo."""
    if MCP_CONFIG_PATH and Path(MCP_CONFIG_PATH).exists():
        return MCP_CONFIG_PATH
    # Busca en /tmp el config más reciente con Gmail
    tmp = Path("/tmp")
    candidates = sorted(tmp.glob("mcp-config-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for c in candidates:
        try:
            data = json.loads(c.read_text())
            if "Gmail" in data.get("mcpServers", {}):
                return str(c)
        except Exception:
            continue
    return ""


def build_search_and_draft_prompt() -> str:
    today     = datetime.now().strftime("%d de %B de %Y")
    last_week = (datetime.now() - timedelta(days=7)).strftime("%d de %B de %Y")
    week_no   = datetime.now().isocalendar()[1]
    date_str  = datetime.now().strftime("%d/%m/%Y")
    subject   = f"🤖 Novedades Claude — Semana {week_no} ({date_str})"

    return f"""Fecha actual: {today}. Período: última semana ({last_week} – {today}).

TAREA: Busca novedades de Claude de Anthropic y crea un borrador de email en Gmail.

PASO 1 — Haz estas búsquedas con WebSearch (todas):
1. "Claude Anthropic new model {datetime.now().year}" — nuevos modelos
2. "Claude API new features tools {datetime.now().year}" — herramientas y API
3. "Claude MCP server GitHub {datetime.now().year}" — repos de GitHub
4. "Claude AI YouTube tutorial {datetime.now().year}" — vídeos
5. "Claude Anthropic Reddit HackerNews {datetime.now().year}" — comunidad
6. "Anthropic blog announcement {datetime.now().year}" — noticias oficiales
7. "Claude AI app integration {datetime.now().year}" — aplicaciones nuevas

PASO 2 — Redacta el contenido del email con esta estructura (en español):

## 🚀 Resumen Ejecutivo
(3-4 frases con lo más importante)

## 🤖 Nuevos Modelos y Actualizaciones

## 🛠️ Nuevas Herramientas y Funcionalidades

## 📦 GitHub: Repos Destacados

## 🎬 YouTube y Recursos de Aprendizaje

## 💬 Foros y Comunidad

## 📱 Aplicaciones e Integraciones Nuevas

## 📰 Noticias Oficiales de Anthropic

## ⭐ Recomendación de la Semana

PASO 3 — Crea un borrador en Gmail usando la herramienta mcp__Gmail__create_draft con:
- to: ["{RECIPIENT_EMAIL}"]
- subject: "{subject}"
- htmlBody: el contenido del email formateado como HTML limpio con estilos inline.
  Usa este encabezado HTML:
  <div style="font-family:Arial,sans-serif;max-width:700px;margin:0 auto;">
  <div style="background:linear-gradient(135deg,#1a1a2e,#0f3460);padding:25px;color:white;border-radius:8px 8px 0 0;">
  <h1 style="margin:0;font-size:22px;">🤖 Digest Semanal — Novedades de Claude</h1>
  <p style="margin:5px 0 0;opacity:.7;">Semana {week_no} · {date_str}</p></div>
  <div style="padding:25px;background:white;border-radius:0 0 8px 8px;">
  [CONTENIDO AQUÍ]
  </div></div>

Confirma cuando el borrador esté creado."""


def run_digest():
    mcp_config = find_mcp_config()
    if not mcp_config:
        print("  ✗ No se encontró mcp-config con Gmail. Ejecuta desde una sesión Claude Code activa.")
        sys.exit(1)

    print(f"  → Usando MCP config: {mcp_config}")

    cmd = [
        CLAUDE_BIN, "-p",
        build_search_and_draft_prompt(),
        "--allowedTools", "WebSearch,mcp__Gmail__create_draft",
        "--mcp-config", mcp_config,
        "--dangerously-skip-permissions",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    if result.returncode != 0:
        print(f"  ✗ Error:\n{result.stderr[:1000]}")
        sys.exit(1)

    print(result.stdout[:500])
    print(f"\n  ✓ Borrador creado en Gmail (osky01313@gmail.com)")
    print(f"    Destinatario: {RECIPIENT_EMAIL}")
    print(f"    Revísalo en Gmail y pulsa Enviar.")


def main():
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] Iniciando digest semanal de Claude...")

    if not Path(CLAUDE_BIN).exists():
        print(f"ERROR: No se encuentra claude en {CLAUDE_BIN}")
        sys.exit(1)

    run_digest()
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] ¡Completado!")


if __name__ == "__main__":
    main()
