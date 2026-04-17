#!/usr/bin/env python3
"""
Weekly Claude AI News Digest
- Busca novedades de Claude (modelos, tools, GitHub, YouTube, foros)
- Incluye vídeos específicos de: Nate Gentile, MoureDev, MiduDev y comunidad hispana
- Guarda nota en Obsidian vault
- Crea borrador en Gmail via MCP
"""

import os
import sys
import subprocess
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Load .env
# ---------------------------------------------------------------------------
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
CLAUDE_BIN          = os.environ.get("CLAUDE_BIN", "/opt/node22/bin/claude")
RECIPIENT_EMAIL     = os.environ.get("RECIPIENT_EMAIL", "ogarcia@seidor.es")
MCP_CONFIG_PATH     = os.environ.get("MCP_CONFIG_PATH", "")
OBSIDIAN_VAULT_PATH = os.environ.get("OBSIDIAN_VAULT_PATH", "")   # ej: /Users/oscar/Documents/Obsidian/MyVault
OBSIDIAN_FOLDER     = os.environ.get("OBSIDIAN_FOLDER", "Novedades Claude")


def find_mcp_config() -> str:
    if MCP_CONFIG_PATH and Path(MCP_CONFIG_PATH).exists():
        return MCP_CONFIG_PATH
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


def build_prompt() -> str:
    today     = datetime.now().strftime("%d de %B de %Y")
    last_week = (datetime.now() - timedelta(days=7)).strftime("%d de %B de %Y")
    week_no   = datetime.now().isocalendar()[1]
    date_str  = datetime.now().strftime("%d/%m/%Y")
    year      = datetime.now().year
    subject   = f"🤖 Novedades Claude — Semana {week_no} ({date_str})"

    return f"""Fecha actual: {today}. Período: última semana ({last_week} – {today}).

TAREA: Busca novedades de Claude de Anthropic y crea un borrador de email en Gmail.

═══ PASO 1: BÚSQUEDAS WEB (realiza TODAS con WebSearch) ═══

Búsquedas generales:
1. "Claude Anthropic new model {year}"
2. "Claude API new features tools {year}"
3. "Claude MCP server GitHub {year}"
4. "Anthropic blog announcement {year}"
5. "Claude AI app integration {year}"
6. "Claude Anthropic Reddit HackerNews {year}"

Búsquedas específicas de YouTube — canales de la comunidad hispana y tech:
7. "Nate Gentile Claude Anthropic YouTube {year}" — busca vídeos recientes del canal Nate Gentile
8. "MoureDev Claude Anthropic YouTube {year}" — busca vídeos recientes del canal MoureDev
9. "MiduDev Claude Anthropic YouTube {year}" — busca vídeos recientes del canal MiduDev
10. "Dot CSV Claude Anthropic YouTube {year}" — busca vídeos recientes del canal DotCSV
11. "site:youtube.com Claude Anthropic tutorial {year}" — otros vídeos relevantes en inglés
12. "Claude Code tutorial YouTube {year}" — tutoriales de Claude Code en YouTube

Para cada vídeo encontrado extrae: título, canal, URL directa de YouTube y duración si disponible.

═══ PASO 2: REDACTA EL INFORME ═══

Redacta un informe semanal completo en español con esta estructura EXACTA:

---
## 🚀 Resumen Ejecutivo
(3-4 frases con lo más importante de la semana)

## 🤖 Nuevos Modelos y Actualizaciones
(versiones, benchmarks, precios, cambios de contexto)

## 🛠️ Nuevas Herramientas y Funcionalidades
(API features, Agent Skills, tool use, nuevas capacidades)

## 📦 GitHub: Repos y Proyectos Destacados
Para cada repo incluye: nombre, descripción breve y enlace directo.

## 🎬 YouTube — Comunidad Hispana
Para cada vídeo incluye: título, canal, enlace directo a YouTube y descripción en 1 línea.
Incluye vídeos de: Nate Gentile, MoureDev, MiduDev, DotCSV y otros creadores relevantes.

## 🎬 YouTube — Comunidad Internacional
Para cada vídeo incluye: título, canal, enlace directo a YouTube y descripción en 1 línea.

## 💬 Foros y Comunidad
(Reddit, HackerNews — temas más discutidos con links)

## 📱 Aplicaciones e Integraciones Nuevas
(apps, plugins, integraciones con otros servicios)

## 📰 Noticias Oficiales de Anthropic
(blog posts, papers de investigación, anuncios)

## ⭐ Recomendación de la Semana
(el recurso MÁS útil para mejorar el uso de Claude, con enlace directo)
---

IMPORTANTE: Incluye SIEMPRE enlaces directos (URLs completas). Para YouTube, enlace directo al vídeo.

═══ PASO 3: CREA EL BORRADOR EN GMAIL ═══

Usa mcp__Gmail__create_draft con:
- to: ["{RECIPIENT_EMAIL}"]
- subject: "{subject}"
- htmlBody: el informe formateado como HTML con este encabezado:

<div style="font-family:Arial,sans-serif;max-width:700px;margin:0 auto;color:#222;">
<div style="background:linear-gradient(135deg,#1a1a2e,#0f3460);padding:25px 30px;color:white;border-radius:8px 8px 0 0;">
<h1 style="margin:0;font-size:22px;">🤖 Digest Semanal — Novedades de Claude</h1>
<p style="margin:6px 0 0;opacity:.7;font-size:13px;">Semana {week_no} · {date_str} · Fuentes: YouTube · GitHub · Reddit · Anthropic Blog</p>
</div>
<div style="padding:25px 30px;background:white;border-radius:0 0 8px 8px;border:1px solid #e8e8e8;">
[CONTENIDO HTML AQUÍ — usa h2, ul, li, a con color:#cc4a1b para los enlaces]
</div>
<div style="padding:15px 30px;background:#f5f5f5;font-size:11px;color:#999;border-top:1px solid #e8e8e8;">
Generado automáticamente cada lunes con Claude Code
</div>
</div>

Tras crear el borrador, devuelve el informe completo en MARKDOWN (sin HTML) para guardarlo en Obsidian."""


def save_to_obsidian(markdown_content: str):
    """Guarda el digest como nota en la vault de Obsidian."""
    if not OBSIDIAN_VAULT_PATH:
        print("  ℹ Obsidian: OBSIDIAN_VAULT_PATH no configurado, saltando.")
        return

    vault = Path(OBSIDIAN_VAULT_PATH)
    if not vault.exists():
        print(f"  ✗ Obsidian: ruta no encontrada: {vault}")
        return

    folder = vault / OBSIDIAN_FOLDER
    folder.mkdir(parents=True, exist_ok=True)

    date_str  = datetime.now().strftime("%Y-%m-%d")
    week_no   = datetime.now().isocalendar()[1]
    filename  = f"{date_str} Novedades Claude Semana {week_no}.md"
    note_path = folder / filename

    # Frontmatter YAML para Obsidian
    frontmatter = f"""---
title: "Novedades Claude — Semana {week_no}"
date: {date_str}
tags: [claude, anthropic, ia, digest, semanal]
semana: {week_no}
---

"""
    note_path.write_text(frontmatter + markdown_content, encoding="utf-8")
    print(f"  ✓ Nota guardada en Obsidian: {note_path}")


def run_digest():
    mcp_config = find_mcp_config()
    if not mcp_config:
        print("  ✗ No se encontró mcp-config con Gmail. Ejecuta desde una sesión Claude Code activa.")
        sys.exit(1)

    print(f"  → Usando MCP config: {mcp_config}")

    cmd = [
        CLAUDE_BIN, "-p",
        build_prompt(),
        "--allowedTools", "WebSearch,mcp__Gmail__create_draft",
        "--mcp-config", mcp_config,
        "--dangerously-skip-permissions",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    if result.returncode != 0:
        print(f"  ✗ Error:\n{result.stderr[:1000]}")
        sys.exit(1)

    output = result.stdout.strip()
    print(output[:300])

    # Guardar en Obsidian si está configurado
    if OBSIDIAN_VAULT_PATH:
        save_to_obsidian(output)

    print(f"\n  ✓ Borrador creado en Gmail → {RECIPIENT_EMAIL}")
    if OBSIDIAN_VAULT_PATH:
        print(f"  ✓ Nota guardada en Obsidian")


def main():
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] Iniciando digest semanal de Claude...")

    if not Path(CLAUDE_BIN).exists():
        print(f"ERROR: claude no encontrado en {CLAUDE_BIN}")
        sys.exit(1)

    run_digest()
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] ¡Completado!")


if __name__ == "__main__":
    main()
