# routines

Automatizaciones periódicas para potenciar el uso de Claude.

---

## 📬 Digest Semanal de Novedades de Claude

Busca automáticamente cada semana las últimas novedades sobre Claude de Anthropic
(modelos, herramientas, GitHub, YouTube, foros, apps) y las envía por email.

### Qué incluye cada email

- Nuevos modelos y actualizaciones (benchmarks, precios)
- Nuevas herramientas y funcionalidades de la API
- Repositorios de GitHub destacados
- Vídeos de YouTube relevantes
- Discusiones en Reddit / HackerNews
- Aplicaciones e integraciones nuevas
- Noticias oficiales del blog de Anthropic
- Recomendación de la semana

### Configuración

**1. Copia y rellena el archivo de configuración:**

```bash
cp .env.example .env
# Edita .env con tu editor favorito
```

Necesitas:
- **`ANTHROPIC_API_KEY`** — obtén la tuya en https://console.anthropic.com/
- **`SMTP_USER` / `SMTP_PASSWORD`** — credenciales de email para enviar

Para Gmail, crea una *App Password*:
> Google Account → Security → 2-Step Verification → App passwords

**2. Instala la dependencia:**

```bash
pip3 install anthropic
```

**3. Activa el cron job semanal (lunes 08:00):**

```bash
bash setup_cron.sh
```

**4. Prueba inmediata (opcional):**

```bash
python3 claude_news_digest.py
```

### Archivos

| Archivo | Descripción |
|---|---|
| `claude_news_digest.py` | Script principal |
| `.env.example` | Plantilla de configuración |
| `.env` | Tu configuración (no subir a git) |
| `setup_cron.sh` | Configura el cron job semanal |
| `digest.log` | Log de ejecuciones (generado automáticamente) |

### Gestión del cron job

```bash
crontab -l          # Ver jobs activos
crontab -e          # Editar manualmente
tail -f digest.log  # Ver logs en tiempo real
```
