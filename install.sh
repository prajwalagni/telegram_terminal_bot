#!/bin/bash

# ===================================================================
# Telegram Terminal Bot - Installation Script
# ===================================================================

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/tgbot"
CONFIG_DIR="/etc/tgbot"
LOG_DIR="/var/log"
SERVICE_USER="root"  # Can be changed to a specific user

echo "==================================="
echo "Telegram Terminal Bot Installation"
echo "==================================="
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)" 
   exit 1
fi

echo "📦 Installing required packages..."

# Detect package manager and install dependencies
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    apt-get update
    apt-get install -y curl jq imagemagick scrot alsa-utils pulseaudio-utils x11-xserver-utils bc socat

    # Try to install gnome-screenshot if available
    apt-get install -y gnome-screenshot 2>/dev/null || true

elif command -v yum &> /dev/null; then
    # RHEL/CentOS
    yum install -y curl jq ImageMagick scrot alsa-utils pulseaudio-utils xrandr bc socat

elif command -v dnf &> /dev/null; then
    # Fedora
    dnf install -y curl jq ImageMagick scrot alsa-utils pulseaudio-utils xrandr bc socat

elif command -v pacman &> /dev/null; then
    # Arch Linux
    pacman -S --noconfirm curl jq imagemagick scrot alsa-utils pulseaudio xorg-xrandr bc socat

elif command -v zypper &> /dev/null; then
    # openSUSE
    zypper install -y curl jq ImageMagick scrot alsa pulseaudio-utils xrandr bc socat

else
    echo "⚠️  Unknown package manager. Please install manually:"
    echo "   - curl, jq, imagemagick, scrot, alsa-utils, pulseaudio-utils, xrandr, bc, socat"
    echo "   - Continue installation? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Required packages installed"

echo "📁 Creating directories..."
mkdir -p "$INSTALL_DIR" "$CONFIG_DIR" "$LOG_DIR"
chmod 755 "$INSTALL_DIR" "$CONFIG_DIR"
chmod 755 "$LOG_DIR"

echo "📋 Copying files..."
cp "$SCRIPT_DIR/tgbot.sh" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/tgbot.sh"

# Copy configuration template if config doesn't exist
if [[ ! -f "$CONFIG_DIR/config.env" ]]; then
    if [[ -f "$SCRIPT_DIR/config.env.template" ]]; then
        cp "$SCRIPT_DIR/config.env.template" "$CONFIG_DIR/config.env"
        echo "📝 Configuration template copied to $CONFIG_DIR/config.env"
    else
        echo "⚠️  Configuration template not found. Creating basic template..."
        cat > "$CONFIG_DIR/config.env" << 'EOF'
# Telegram Terminal Bot Configuration File
BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
AUTHORIZED_USERS="123456789"
AUTHORIZED_GROUPS=""
ADMIN_USER_ID="123456789"
UPDATE_URL="https://raw.githubusercontent.com/yourusername/yourrepo/main/tgbot.sh"
BATTERY_LOW_THRESHOLD=20
BATTERY_HIGH_THRESHOLD=90
EOF
    fi
    chmod 600 "$CONFIG_DIR/config.env"  # Protect sensitive config
else
    echo "📝 Configuration file already exists at $CONFIG_DIR/config.env"
fi

echo "🔧 Creating systemd service..."

# Create systemd service file
cat > /etc/systemd/system/tgbot.service << EOF
[Unit]
Description=Telegram Terminal Bot
Documentation=https://github.com/yourrepo/telegram-terminal-bot
After=network-online.target graphical-session.target
Wants=network-online.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/tgbot.sh --daemon
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
TimeoutStopSec=20

# Environment variables
Environment=HOME=/root
Environment=DISPLAY=:0
Environment=XAUTHORITY=/root/.Xauthority

# Security settings
NoNewPrivileges=false
PrivateTmp=false
ProtectSystem=false
ProtectHome=false
ReadWritePaths=$CONFIG_DIR $LOG_DIR /tmp

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=tgbot

[Install]
WantedBy=multi-user.target
EOF

# Create user service for startup notifications
cat > /etc/systemd/user/tgbot-notify.service << EOF
[Unit]
Description=Telegram Bot Login Notifier
After=graphical-session.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'sleep 5 && $INSTALL_DIR/tgbot.sh --notify-login'
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
EOF

echo "🔄 Enabling and starting services..."
systemctl daemon-reload
systemctl enable tgbot.service

# Enable user service for all users
systemctl --global enable tgbot-notify.service

echo "🔐 Setting up log rotation..."
cat > /etc/logrotate.d/tgbot << EOF
$LOG_DIR/tgbot.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    postrotate
        systemctl reload tgbot.service || true
    endscript
}
EOF

echo "📋 Creating desktop shortcut (optional)..."
if [[ -d "/usr/share/applications" ]]; then
    cat > /usr/share/applications/tgbot-config.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Telegram Bot Config
Comment=Configure Telegram Terminal Bot
Exec=xdg-open $CONFIG_DIR/config.env
Icon=utilities-terminal
Terminal=false
Categories=System;Network;
EOF
fi

# Create helper scripts
echo "🛠️  Creating helper scripts..."

# Create startup script for login notifications
cat > "$INSTALL_DIR/notify-login.sh" << 'EOF'
#!/bin/bash
CONFIG_FILE="/etc/tgbot/config.env"
if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
    if [[ -n "$BOT_TOKEN" && -n "$ADMIN_USER_ID" ]]; then
        USER=$(whoami)
        HOSTNAME=$(hostname)
        TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
        MESSAGE="✅ User **$USER** logged in to **$HOSTNAME** at $TIMESTAMP"

        curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage"             -d "chat_id=${ADMIN_USER_ID}"             -d "text=${MESSAGE}"             -d "parse_mode=MarkdownV2" > /dev/null
    fi
fi
EOF
chmod +x "$INSTALL_DIR/notify-login.sh"

# Create test script
cat > "$INSTALL_DIR/test-bot.sh" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
./tgbot.sh --test
EOF
chmod +x "$INSTALL_DIR/test-bot.sh"

# Create management script
cat > "$INSTALL_DIR/manage.sh" << EOF
#!/bin/bash
case "\$1" in
    start)
        systemctl start tgbot.service
        echo "Bot started"
        ;;
    stop)
        systemctl stop tgbot.service
        echo "Bot stopped"
        ;;
    restart)
        systemctl restart tgbot.service
        echo "Bot restarted"
        ;;
    status)
        systemctl status tgbot.service
        ;;
    logs)
        journalctl -u tgbot.service -f
        ;;
    test)
        "$INSTALL_DIR/tgbot.sh" --test
        ;;
    config)
        \${EDITOR:-nano} "$CONFIG_DIR/config.env"
        ;;
    *)
        echo "Usage: \$0 {start|stop|restart|status|logs|test|config}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the bot service"
        echo "  stop     - Stop the bot service"
        echo "  restart  - Restart the bot service"
        echo "  status   - Show service status"
        echo "  logs     - Show live logs"
        echo "  test     - Test bot configuration"
        echo "  config   - Edit configuration file"
        ;;
esac
EOF
chmod +x "$INSTALL_DIR/manage.sh"

# Create symlink for easier access
ln -sf "$INSTALL_DIR/manage.sh" /usr/local/bin/tgbot

echo
echo "✅ Installation completed successfully!"
echo
echo "📝 Next steps:"
echo "   1. Edit the configuration file: nano $CONFIG_DIR/config.env"
echo "   2. Set your BOT_TOKEN from @BotFather"
echo "   3. Set your AUTHORIZED_USERS (get your ID from @userinfobot)"
echo "   4. Test the configuration: tgbot test"
echo "   5. Start the bot: tgbot start"
echo
echo "🔧 Management commands:"
echo "   tgbot start     - Start the bot"
echo "   tgbot stop      - Stop the bot"  
echo "   tgbot restart   - Restart the bot"
echo "   tgbot status    - Show status"
echo "   tgbot logs      - View live logs"
echo "   tgbot test      - Test configuration"
echo "   tgbot config    - Edit configuration"
echo
echo "📍 Important files:"
echo "   Bot script:      $INSTALL_DIR/tgbot.sh"
echo "   Configuration:   $CONFIG_DIR/config.env"
echo "   Log file:        $LOG_DIR/tgbot.log"
echo "   Service file:    /etc/systemd/system/tgbot.service"
echo
echo "⚠️  Remember to:"
echo "   - Configure your bot token and authorized users"
echo "   - Test the bot before starting the service"
echo "   - Check firewall settings if having connection issues"
echo "   - Review the log file if you encounter problems"
echo
echo "🔗 For help and documentation:"
echo "   - Check the README.md file"
echo "   - View logs: journalctl -u tgbot.service"
echo "   - Test configuration: $INSTALL_DIR/tgbot.sh --test"
