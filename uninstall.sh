#!/bin/bash

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
