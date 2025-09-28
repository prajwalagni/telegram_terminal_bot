#!/bin/bash

# ===================================================================
# Telegram Terminal Bot - Test Script
# ===================================================================

CONFIG_FILE="/etc/tgbot/config.env"
INSTALL_DIR="/opt/tgbot"

echo "🧪 Testing Telegram Terminal Bot Configuration"
echo "=============================================="
echo

# Check if bot is installed
if [[ ! -f "$INSTALL_DIR/tgbot.sh" ]]; then
    echo "❌ Bot not installed. Run install.sh first."
    exit 1
fi

# Check configuration file
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Configuration file not found: $CONFIG_FILE"
    exit 1
fi

echo "✅ Installation files found"

# Load configuration
source "$CONFIG_FILE"

# Test configuration values
echo "🔧 Checking configuration..."

if [[ -z "$BOT_TOKEN" || "$BOT_TOKEN" == "YOUR_BOT_TOKEN_HERE" ]]; then
    echo "❌ BOT_TOKEN not configured"
    echo "   Edit $CONFIG_FILE and set your bot token from @BotFather"
    exit 1
fi

if [[ -z "$AUTHORIZED_USERS" || "$AUTHORIZED_USERS" == "123456789" ]]; then
    echo "⚠️  AUTHORIZED_USERS not configured properly"
    echo "   Edit $CONFIG_FILE and set your user ID from @userinfobot"
fi

if [[ -z "$ADMIN_USER_ID" || "$ADMIN_USER_ID" == "123456789" ]]; then
    echo "⚠️  ADMIN_USER_ID not configured properly"
    echo "   Edit $CONFIG_FILE and set your admin user ID"
fi

echo "✅ Configuration file loaded"

# Test network connectivity
echo "🌐 Testing network connectivity..."
if ping -c 1 -W 5 api.telegram.org &> /dev/null; then
    echo "✅ Can reach Telegram API servers"
else
    echo "❌ Cannot reach Telegram API servers"
    echo "   Check your internet connection"
    exit 1
fi

# Test Telegram Bot API
echo "🤖 Testing Telegram Bot API..."
API_URL="https://api.telegram.org/bot${BOT_TOKEN}"
response=$(curl -s "${API_URL}/getMe")

if echo "$response" | jq -e '.ok' >/dev/null 2>&1; then
    bot_name=$(echo "$response" | jq -r '.result.username')
    echo "✅ Bot API working - Connected to @$bot_name"
else
    echo "❌ Bot API test failed"
    echo "   Response: $response"
    echo "   Check your BOT_TOKEN in $CONFIG_FILE"
    exit 1
fi

# Test required commands
echo "🔧 Testing system commands..."

commands_to_test=("curl" "jq" "systemctl")
for cmd in "${commands_to_test[@]}"; do
    if command -v "$cmd" &> /dev/null; then
        echo "✅ $cmd available"
    else
        echo "❌ $cmd not found"
    fi
done

# Test optional commands
echo "📸 Testing optional features..."
screenshot_tools=("gnome-screenshot" "scrot" "import")
screenshot_available=false
for tool in "${screenshot_tools[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo "✅ Screenshot tool: $tool"
        screenshot_available=true
        break
    fi
done

if [[ "$screenshot_available" == false ]]; then
    echo "⚠️  No screenshot tools available"
    echo "   Install: gnome-screenshot, scrot, or imagemagick"
fi

# Test audio tools
audio_tools=("amixer" "pactl")
for tool in "${audio_tools[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo "✅ Audio control: $tool"
    else
        echo "⚠️  Audio tool not found: $tool"
    fi
done

# Test display tools
if command -v "xrandr" &> /dev/null; then
    echo "✅ Display control: xrandr"
else
    echo "⚠️  Display control not available: xrandr not found"
fi

# Test service status
echo "🔄 Testing service status..."
if systemctl is-active --quiet tgbot.service; then
    echo "✅ Bot service is running"
elif systemctl list-unit-files | grep -q "tgbot.service"; then
    echo "⚠️  Bot service exists but not running"
    echo "   Start it with: sudo systemctl start tgbot.service"
else
    echo "⚠️  Bot service not installed"
    echo "   Install it with: sudo $INSTALL_DIR/tgbot.sh --install"
fi

# Test file permissions
echo "🔐 Testing file permissions..."
if [[ -r "$CONFIG_FILE" ]]; then
    echo "✅ Configuration file readable"
else
    echo "❌ Cannot read configuration file"
fi

if [[ -x "$INSTALL_DIR/tgbot.sh" ]]; then
    echo "✅ Bot script executable"
else
    echo "❌ Bot script not executable"
fi

echo
echo "🧪 Test completed!"
echo
echo "Next steps:"
echo "  1. Configure your bot token and user IDs if not done"
echo "  2. Start the service: sudo systemctl start tgbot.service"  
echo "  3. Check logs: sudo journalctl -u tgbot.service -f"
echo "  4. Message your bot on Telegram to test functionality"
