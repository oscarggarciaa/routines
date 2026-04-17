#!/usr/bin/env bash
# Configura el cron job semanal (lunes 08:00)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/claude_news_digest.py"
LOG_PATH="$SCRIPT_DIR/digest.log"
PYTHON=$(which python3)

# Busca el mcp-config de Gmail más reciente
MCP_CONFIG=$(ls -t /tmp/mcp-config-*.json 2>/dev/null | head -1 || true)
if [[ -z "$MCP_CONFIG" ]]; then
  echo "⚠️  No se encontró mcp-config. Ejecuta este script desde una sesión Claude Code activa."
  exit 1
fi

echo "✓ MCP config encontrado: $MCP_CONFIG"

# Cron: lunes a las 08:00
CRON_CMD="0 8 * * 1 MCP_CONFIG_PATH=$MCP_CONFIG $PYTHON $SCRIPT_PATH >> $LOG_PATH 2>&1"

(crontab -l 2>/dev/null | grep -v "$SCRIPT_PATH"; echo "$CRON_CMD") | crontab -

echo "✅ Cron job activado: lunes a las 08:00"
echo "   Log: $LOG_PATH"
echo "   Prueba inmediata: python3 $SCRIPT_PATH"
