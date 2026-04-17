#!/usr/bin/env bash
# =============================================================================
# Configura el cron job semanal para el digest de Claude
# Uso: bash setup_cron.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/claude_news_digest.py"
LOG_PATH="$SCRIPT_DIR/digest.log"
PYTHON=$(which python3)

# Verifica que existe el .env
if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
  echo "⚠️  No se encontró .env. Cópialo desde .env.example y rellena los valores:"
  echo "    cp $SCRIPT_DIR/.env.example $SCRIPT_DIR/.env"
  exit 1
fi

# Cron: todos los lunes a las 08:00
CRON_SCHEDULE="0 8 * * 1"
CRON_CMD="$CRON_SCHEDULE $PYTHON $SCRIPT_PATH >> $LOG_PATH 2>&1"

# Añade la línea al crontab si no existe ya
(crontab -l 2>/dev/null | grep -v "$SCRIPT_PATH"; echo "$CRON_CMD") | crontab -

echo "✅ Cron job configurado:"
echo "   $CRON_CMD"
echo ""
echo "El digest se enviará todos los lunes a las 08:00."
echo "Logs en: $LOG_PATH"
echo ""
echo "Otros comandos útiles:"
echo "  Ver cron jobs:    crontab -l"
echo "  Editar cron:      crontab -e"
echo "  Probar ahora:     python3 $SCRIPT_PATH"
echo "  Ver logs:         tail -f $LOG_PATH"
