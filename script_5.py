# Create uninstall script
uninstall_script = '''#!/bin/bash

# ===================================================================
# Telegram Terminal Bot - Uninstallation Script
# ===================================================================

set -e

INSTALL_DIR="/opt/tgbot"
CONFIG_DIR="/etc/tgbot"
LOG_DIR="/var/log"
SERVICE_NAME="tgbot.service"
USER_SERVICE_NAME="tgbot-notify.service"

echo "======================================="
echo "Telegram Terminal Bot Uninstallation"
echo "======================================="
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)" 
   exit 1
fi

echo "⚠️  This will completely remove Telegram Terminal Bot from your system."
echo "❓ Do you want to continue? (y/N)"
read -r response

if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "❌ Uninstallation cancelled"
    exit 0
fi

echo "🛑 Stopping and disabling services..."

# Stop and disable main service
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    systemctl stop "$SERVICE_NAME"
    echo "   ✅ Stopped $SERVICE_NAME"
fi

if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
    systemctl disable "$SERVICE_NAME"
    echo "   ✅ Disabled $SERVICE_NAME"
fi

# Stop and disable user service
if systemctl --global is-enabled --quiet "$USER_SERVICE_NAME" 2>/dev/null; then
    systemctl --global disable "$USER_SERVICE_NAME"
    echo "   ✅ Disabled $USER_SERVICE_NAME"
fi

echo "🗑️  Removing service files..."

# Remove systemd service files
if [[ -f "/etc/systemd/system/$SERVICE_NAME" ]]; then
    rm -f "/etc/systemd/system/$SERVICE_NAME"
    echo "   ✅ Removed /etc/systemd/system/$SERVICE_NAME"
fi

if [[ -f "/etc/systemd/user/$USER_SERVICE_NAME" ]]; then
    rm -f "/etc/systemd/user/$USER_SERVICE_NAME"
    echo "   ✅ Removed /etc/systemd/user/$USER_SERVICE_NAME"
fi

# Reload systemd
systemctl daemon-reload
systemctl --global daemon-reload

echo "📁 Removing installation directory..."
if [[ -d "$INSTALL_DIR" ]]; then
    rm -rf "$INSTALL_DIR"
    echo "   ✅ Removed $INSTALL_DIR"
fi

echo "🔗 Removing symlinks..."
if [[ -L "/usr/local/bin/tgbot" ]]; then
    rm -f "/usr/local/bin/tgbot"
    echo "   ✅ Removed /usr/local/bin/tgbot"
fi

echo "📋 Removing desktop entries..."
if [[ -f "/usr/share/applications/tgbot-config.desktop" ]]; then
    rm -f "/usr/share/applications/tgbot-config.desktop"
    echo "   ✅ Removed desktop entry"
fi

echo "📄 Removing log rotation configuration..."
if [[ -f "/etc/logrotate.d/tgbot" ]]; then
    rm -f "/etc/logrotate.d/tgbot"
    echo "   ✅ Removed log rotation config"
fi

echo "🗂️  Cleaning up log files..."
rm -f "${LOG_DIR}/tgbot.log"* "${LOG_DIR}/tgbot_monitor.log"*
echo "   ✅ Removed log files"

echo "⚙️  Configuration and data:"
echo "   📁 Configuration directory: $CONFIG_DIR"
echo "   📄 Contains: config.env and other configuration files"
echo "   ❓ Remove configuration directory? (y/N)"
read -r config_response

if [[ "$config_response" =~ ^[Yy]$ ]]; then
    if [[ -d "$CONFIG_DIR" ]]; then
        rm -rf "$CONFIG_DIR"
        echo "   ✅ Removed $CONFIG_DIR"
    fi
else
    echo "   📋 Configuration directory preserved at $CONFIG_DIR"
    echo "   💡 You can manually remove it later if needed"
fi

echo "🧹 Cleaning temporary files..."
rm -rf "/tmp/tgbot"
echo "   ✅ Removed temporary files"

echo
echo "✅ Telegram Terminal Bot has been successfully uninstalled!"
echo

if [[ -d "$CONFIG_DIR" ]]; then
    echo "📋 Note: Configuration files are preserved at $CONFIG_DIR"
    echo "   You can remove them manually if you don't plan to reinstall"
fi

echo "🔄 If you want to reinstall later:"
echo "   1. Run the install.sh script again"
echo "   2. Your configuration will be preserved (if not removed)"

echo
echo "Thank you for using Telegram Terminal Bot! 🤖"
'''

with open('uninstall.sh', 'w') as f:
    f.write(uninstall_script)

# Create a simple test script
test_script = '''#!/bin/bash

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
'''

with open('test.sh', 'w') as f:
    f.write(test_script)

# Create a changelog file
changelog = '''# Changelog

All notable changes to the Telegram Terminal Bot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-19

### Added
- Initial release of Telegram Terminal Bot
- Complete remote terminal access via Telegram
- Interactive command execution with session persistence
- File upload and download support (up to 50MB)
- Built-in screenshot functionality with multiple tool support
- Audio volume control (amixer/pactl integration)
- Display brightness control (xrandr integration)
- System information reporting (/sysinfo command)
- Network information display (/network command)
- Automatic service installation with systemd
- User authorization and admin controls
- Group chat support with admin permissions
- Auto-update mechanism via Telegram
- Comprehensive system monitoring and alerting
- Battery monitoring for laptops
- Login/logout notifications
- Shutdown/reboot notifications
- Failed login attempt monitoring
- System health monitoring (CPU, memory, disk, temperature)
- Log rotation and management
- Security features and access control
- Complete installation and uninstallation scripts
- Comprehensive documentation and troubleshooting guide

### Security Features
- User ID based authorization
- Secure configuration file handling
- Command timeout protection
- Session isolation
- File access restrictions
- Network security considerations

### System Integration
- Systemd service integration
- Auto-start on boot
- Desktop integration
- Log management with rotation
- Service management commands
- Multi-distribution support

### Monitoring Capabilities
- Real-time system alerts
- Battery level monitoring
- Disk usage warnings
- Memory usage alerts
- CPU temperature monitoring
- Network connectivity checks
- Service status monitoring
- Security event detection

## [Unreleased]

### Planned Features
- Web interface for configuration
- Plugin system for custom commands
- Multi-language support
- Enhanced file management interface
- Remote desktop functionality
- Database integration options
- Docker container support
- Kubernetes deployment manifests
'''

with open('CHANGELOG.md', 'w') as f:
    f.write(changelog)

print("Created additional files:")
print("✅ uninstall.sh - Complete removal script")
print("✅ test.sh - Configuration testing script")
print("✅ CHANGELOG.md - Version history")

# Create a summary of all files created
files_summary = '''
📦 TELEGRAM TERMINAL BOT - FILE SUMMARY
=====================================

Core Files:
- tgbot.sh                 Main bot script with all functionality
- config.env.template      Configuration template file
- install.sh              Complete installation script
- uninstall.sh            Complete removal script

Utility Files:  
- system_monitor.sh       System monitoring and alerting script
- test.sh                 Configuration and system testing script

Documentation:
- README.md               Comprehensive documentation and guide
- CHANGELOG.md            Version history and updates

🚀 QUICK START:
1. chmod +x install.sh
2. sudo ./install.sh
3. sudo nano /etc/tgbot/config.env  # Configure your bot
4. tgbot test                       # Test configuration
5. tgbot start                      # Start the bot

⚙️ MANAGEMENT:
- tgbot {start|stop|restart|status|logs|test|config}
- Service location: /opt/tgbot/
- Config location: /etc/tgbot/
- Logs location: /var/log/tgbot.log

🔐 IMPORTANT:
- Set BOT_TOKEN from @BotFather
- Set AUTHORIZED_USERS from @userinfobot  
- Only authorize trusted users
- Monitor access logs regularly
'''

print(files_summary)