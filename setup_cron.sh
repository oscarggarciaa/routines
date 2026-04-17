#!/usr/bin/env bash
# setup_cron.sh — Instala el cron job para ejecutar el digest semanal de Claude
# Ejecución: bash setup_cron.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/weekly_claude_digest.py"
LOG_PATH="$SCRIPT_DIR/digest.log"
ENV_PATH="$SCRIPT_DIR/.env"

# ── Verificaciones previas ────────────────────────────────────────────────────
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "ERROR: No se encuentra $SCRIPT_PATH"
    exit 1
fi

if [ ! -f "$ENV_PATH" ]; then
    echo "AVISO: No existe el archivo .env"
    echo "Copia .env.example a .env y rellena tus credenciales:"
    echo "  cp $SCRIPT_DIR/.env.example $SCRIPT_DIR/.env"
    echo "  nano $SCRIPT_DIR/.env"
    exit 1
fi

PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
    echo "ERROR: Python no encontrado en el PATH"
    exit 1
fi

# ── Construir la línea cron ───────────────────────────────────────────────────
# Cada lunes a las 08:00
CRON_SCHEDULE="0 8 * * 1"
CRON_CMD="$CRON_SCHEDULE cd $SCRIPT_DIR && $PYTHON $SCRIPT_PATH >> $LOG_PATH 2>&1"

# ── Instalar cron job (evita duplicados) ──────────────────────────────────────
EXISTING_CRON=$(crontab -l 2>/dev/null || true)
MARKER="weekly_claude_digest"

if echo "$EXISTING_CRON" | grep -q "$MARKER"; then
    echo "El cron job ya existe. Para modificarlo edita con: crontab -e"
else
    (echo "$EXISTING_CRON"; echo "# $MARKER"; echo "$CRON_CMD") | crontab -
    echo "Cron job instalado correctamente."
fi

# ── Resumen ───────────────────────────────────────────────────────────────────
echo ""
echo "Configuración:"
echo "  Script  : $SCRIPT_PATH"
echo "  Horario : Cada lunes a las 08:00 (hora del servidor)"
echo "  Log     : $LOG_PATH"
echo "  Python  : $PYTHON"
echo ""
echo "Para verificar que el cron está activo:"
echo "  crontab -l"
echo ""
echo "Para ejecutar manualmente (prueba):"
echo "  cd $SCRIPT_DIR && $PYTHON $SCRIPT_PATH"
echo ""
echo "Para cambiar el horario edita el cron con:"
echo "  crontab -e"
echo ""
echo "Ejemplos de horario cron:"
echo "  0 8  * * 1   → Cada lunes a las 08:00"
echo "  0 9  * * 5   → Cada viernes a las 09:00"
echo "  0 7  * * 0   → Cada domingo a las 07:00"
