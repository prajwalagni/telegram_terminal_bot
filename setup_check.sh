#!/bin/bash

# Quick setup verification for Telegram Terminal Bot
echo "🔍 Telegram Terminal Bot - Quick Setup Check"
echo "============================================"

# Check if installed
if [[ -f "/opt/tgbot/tgbot.sh" ]]; then
    echo "✅ Bot installed at /opt/tgbot/"
else
    echo "❌ Bot not installed. Run: sudo ./install.sh"
    exit 1
fi

# Check service status
if systemctl is-active --quiet tgbot.service; then
    echo "✅ Service running"
else
    echo "⚠️  Service not running. Start with: sudo systemctl start tgbot.service"
fi

# Check config
if [[ -f "/etc/tgbot/config.env" ]]; then
    source "/etc/tgbot/config.env"
    if [[ "$BOT_TOKEN" == "YOUR_BOT_TOKEN_HERE" ]]; then
        echo "❌ Bot token not configured. Edit: /etc/tgbot/config.env"
    else
        echo "✅ Configuration file exists"
    fi
else
    echo "❌ Configuration file missing"
fi

echo ""
echo "💡 Quick commands:"
echo "   tgbot status  - Check service status"
echo "   tgbot test    - Test configuration"
echo "   tgbot logs    - View logs"
echo "   tgbot config  - Edit configuration"
