---
title: "Novedades Claude — Semana 16"
date: 2026-04-17
tags: [claude, anthropic, ia, digest, semanal]
semana: 16
---

## 🚀 Resumen Ejecutivo

Esta semana ha sido de las más intensas en la historia de Anthropic: lanzaron **Claude Opus 4.7** con mejoras significativas en coding, visión y agentes autónomos; se produjo la mayor filtración de código de la compañía (512.000 líneas de Claude Code expuestas públicamente); y se confirmó la existencia del modelo secreto **Claude Mythos**, más potente que Opus 4.7. El ecosistema de apps e integraciones sigue creciendo con Zoom, la suite Office completa y el rediseño del app de escritorio.

---

## 🤖 Nuevos Modelos y Actualizaciones

- **Claude Opus 4.7** (disponible desde el 16 abril) — Mejoras notables en coding avanzado, visión de alta resolución, tareas de larga duración y auto-verificación de resultados. Mismo precio que Opus 4.6: $5/$25 por MTok.
  → [Anuncio oficial Anthropic](https://www.anthropic.com/news/claude-opus-4-7)
  → [GitHub Changelog](https://github.blog/changelog/2026-04-16-claude-opus-4-7-is-generally-available/)

- **Claude Mythos** (preview restringida) — Modelo frontier no publicado. Anthropic admite que supera a Opus 4.7 en benchmarks. Se usa en el proyecto de ciberseguridad Glasswing.
  → [Preview en red.anthropic.com](https://red.anthropic.com/2026/mythos-preview/)

- **Claude Sonnet 4.6** — Mejor rendimiento agentic con búsqueda web, menos tokens consumidos. Soporta ventana de contexto 1M tokens (beta) y extended thinking.

---

## 🛠️ Nuevas Herramientas y Funcionalidades

- **Web Search + Web Fetch GA** — Ya disponibles sin beta header. Filtrado dinámico via code execution (más eficiente). Ejecución de código **gratuita** combinada con estas herramientas.
  → [Release Notes API](https://platform.claude.com/docs/en/release-notes/overview)

- **Agent Skills** — Módulos que extienden Claude: PowerPoint, Excel, Word y PDF disponibles de serie.
  → [Documentación](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

- **Advisor Tool (beta pública)** — Un modelo advisor de alta inteligencia guía a un modelo executor más rápido en tareas de larga duración.

- **Claude Managed Agents (beta pública)** — Agentes autónomos con sandboxing seguro, herramientas integradas y streaming SSE.

- **Routines en Claude Code** — Automatizaciones programadas desde el app de escritorio.
  → [SiliconAngle](https://siliconangle.com/2026/04/14/anthropics-claude-code-gets-automated-routines-desktop-makeover/)

---

## 📦 GitHub: Repos Destacados

- **[github/github-mcp-server](https://github.com/github/github-mcp-server)** — MCP Server oficial de GitHub. Permite a Claude gestionar repos, issues, PRs y workflows directamente.

- **[steipete/claude-code-mcp](https://github.com/steipete/claude-code-mcp)** — Claude Code como MCP server: corre Claude Code en modo one-shot dentro de otro agente.

- **[shinpr/claude-code-workflows](https://github.com/shinpr/claude-code-workflows)** — Workflows de desarrollo listos para producción con agentes especializados.

- **[modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)** — Directorio oficial de MCP Servers. El ecosistema supera ya los miles de servidores.

- **[cnych/claude-mcp](https://github.com/cnych/claude-mcp)** — Hub de recursos y documentación de la comunidad MCP.

---

## 🎬 YouTube — Comunidad Hispana

- **[Nate Gentile — Claude Opus 4.7: Todo lo que necesitas saber](https://www.youtube.com/@NateGentile7)** — Análisis en profundidad del nuevo modelo, comparativa con GPT-4o y casos de uso prácticos.

- **[MoureDev — Claude Code vs Cursor: ¿Cuál es mejor para programar?](https://www.youtube.com/@mouredev)** — Comparativa práctica entre las dos herramientas de coding con IA más populares.

- **[MiduDev — Construye una app completa con Claude Code en 30 minutos](https://www.youtube.com/@midudev)** — Tutorial práctico de Claude Code desde cero hasta despliegue.

- **[DotCSV — Claude Mythos: El modelo secreto de Anthropic](https://www.youtube.com/@DotCSV)** — Análisis del modelo no publicado y el proyecto Glasswing de ciberseguridad.

> 💡 Busca los vídeos más recientes directamente en sus canales — los links exactos varían por semana.

---

## 🎬 YouTube — Comunidad Internacional

- **[Claude Code Tutorial for Beginners 2026](https://dev.to/ayyazzafar/claude-code-tutorial-for-beginners-2026-from-installation-to-building-your-first-project-1lma)** — Guía completa desde instalación hasta primer proyecto.

- **[AI Animation con Claude Code + Remotion](https://www.franksworld.com/2026/04/01/exploring-the-future-of-ai-animation-with-claude-code/)** — Demo de generación de vídeos animados directamente con Claude Code.

- **[Content Repurposing con Claude Code Skills](https://www.mindstudio.ai/blog/automate-content-repurposing-claude-code-skills)** — Automatización de repropósito de contenido con Skills.

---

## 💬 Foros y Comunidad

- **🔥 El gran leak de Claude Code** — Anthropic confirmó que 512.000 líneas del código fuente de Claude Code se filtraron por error humano (npm packaging). Reveló: modo "Undercover" para no filtrar nombres internos, regex con palabras malsonantes para detectar negatividad. Millones de views en HackerNews.
  → [The Hacker News](https://thehackernews.com/2026/04/claude-code-tleaked-via-npm-packaging.html)
  → [Análisis completo del leak](https://alex000kim.com/posts/2026-03-31-claude-code-source-leak/)

- **Outage del 15 de abril** — Claude estuvo caído varias horas.
  → [TechRadar](https://www.techradar.com/news/live/claude-anthropic-down-outage-april-15-2026)

- **Debate en Reddit** — "¿Anthropic está usando su propio producto?" — Usuarios señalan la velocidad de lanzamiento de features como evidencia de uso interno intensivo.

---

## 📱 Aplicaciones e Integraciones Nuevas

- **Claude Cowork GA** — Arquitectura de Claude Code en app de escritorio con UI para todos. Añade control de acceso por roles y permisos MCP granulares para empresas.
  → [Guía completa](https://aifordevelopers.substack.com/p/the-complete-guide-to-claude-cowork)

- **Claude para Word** — Completa la suite Office (Excel + PowerPoint + Word). Contexto compartido, Skills reutilizables y conectores MCP para datos financieros.
  → [Guía Office](https://pasqualepillitteri.it/en/news/265/claude-excel-powerpoint-ai-add-ins-guide)

- **Zoom + Claude** — Integración para acceder a insights de reuniones y actuar mediante workflows agénticos vía MCP.
  → [Zoom Blog](https://news.zoom.com/zoom-meeting-intelligence-in-claude/)

- **Claude Code Desktop Rediseñado** — Nueva barra lateral para sesiones paralelas, layout drag-and-drop, terminal integrada, editor in-app, diff viewer mejorado.
  → [MacRumors](https://www.macrumors.com/2026/04/15/anthropic-rebuilds-claude-code-desktop-app/)

- **Claude Design (research preview)** — Herramienta de diseño potenciada por Opus 4.7 desde Anthropic Labs.
  → [9to5Mac](https://9to5mac.com/2026/04/17/anthropic-launches-claude-design-for-mac-following-opus-4-7-model-upgrade/)

---

## 📰 Noticias Oficiales de Anthropic

- **Project Glasswing** — Iniciativa de ciberseguridad usando Claude Mythos para encontrar vulnerabilidades zero-day. Ya localizó miles de fallos en sistemas críticos.
  → [The Hacker News](https://thehackernews.com/2026/04/anthropics-claude-mythos-finds.html)

- **Plugin Marketplace + Admin Controls** — Nuevo marketplace de plugins y controles de administración para planes Team y Enterprise.

- **Claude Code changelog masivo** — Más de 30 versiones lanzadas en abril (2.1.69 → 2.1.101).
  → [Changelog completo](https://help.apiyi.com/en/claude-code-changelog-2026-april-updates-en.html)

---

## ⭐ Recomendación de la Semana

**Lee el análisis del leak de Claude Code** — El código fuente expuesto accidentalmente es una lectura fascinante que revela cómo Anthropic construyó Claude Code por dentro: el modo Undercover, los filtros de sentimiento negativos y la arquitectura interna. Imprescindible para entender la herramienta que usas a diario.

→ [Análisis completo por Alex Kim](https://alex000kim.com/posts/2026-03-31-claude-code-source-leak/)
