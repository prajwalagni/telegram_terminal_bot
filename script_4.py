# Create comprehensive README
readme_content = '''# Telegram Terminal Bot

A comprehensive shell script that provides complete remote access to your Linux system through a Telegram bot. Control your system, execute commands, transfer files, and receive system notifications all through Telegram messages.

## 🚀 Features

### Core Functionality
- **Remote Terminal Access**: Execute any shell command with full interactive support
- **File Transfer**: Upload and download files through Telegram (up to 50MB)
- **Media Support**: Send and receive photos, videos, audio files, and documents
- **Interactive Sessions**: Persistent terminal sessions that maintain state
- **Group Chat Support**: Works in private chats and group chats with admin permissions

### Built-in Commands
- **📸 Screenshot**: `/screenshot` - Capture and send desktop screenshots
- **🔆 Brightness Control**: `/brightness <0.1-1.0>` - Adjust display brightness
- **🔊 Audio Control**: `/volume <up|down|mute|unmute|set> [value]` - Control system volume
- **📊 System Info**: `/sysinfo` - View system status and hardware information
- **🌐 Network Info**: `/network` - Show network configuration and connectivity
- **🔄 Auto-update**: `/update` - Self-update the bot from remote repository

### System Monitoring & Notifications
- **Login Notifications**: Get notified when users log into the system
- **Shutdown Alerts**: Receive notifications when system shuts down or reboots
- **Battery Monitoring**: Low battery and charging complete alerts (laptops)
- **System Health**: CPU, memory, disk usage, and temperature monitoring
- **Security Alerts**: Failed login attempt notifications
- **Service Monitoring**: Critical system service status alerts

### Security & Control
- **User Authorization**: Whitelist specific Telegram user IDs
- **Group Authorization**: Support for authorized group chats
- **Admin Controls**: Special admin-only commands for system management
- **Secure Configuration**: Encrypted bot token and sensitive data protection

### System Integration
- **Auto-start**: Runs as systemd service, starts automatically on boot
- **Log Management**: Comprehensive logging with automatic rotation
- **Service Management**: Easy start/stop/restart with built-in commands
- **Desktop Integration**: Optional desktop shortcuts for configuration

## 📦 Installation

### Prerequisites

The bot requires the following packages (automatically installed by the installer):
- `curl` - For HTTP requests to Telegram API
- `jq` - For JSON parsing and processing  
- `imagemagick` or `scrot` or `gnome-screenshot` - For screenshot functionality
- `alsa-utils` - For audio control
- `xrandr` - For display brightness control
- `bc` - For mathematical calculations
- `socat` - For network operations

### Quick Installation

1. **Download the installation files:**
   ```bash
   wget https://github.com/yourusername/telegram-terminal-bot/archive/main.zip
   unzip main.zip
   cd telegram-terminal-bot-main
   ```

2. **Run the installation script:**
   ```bash
   chmod +x install.sh
   sudo ./install.sh
   ```

3. **Configure the bot:**
   ```bash
   sudo nano /etc/tgbot/config.env
   ```

4. **Set up your bot token and authorized users (see Configuration section)**

5. **Test the configuration:**
   ```bash
   tgbot test
   ```

6. **Start the bot:**
   ```bash
   tgbot start
   ```

## ⚙️ Configuration

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` command
3. Choose a name and username for your bot
4. Copy the bot token (format: `123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 2. Get Your User ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Copy your user ID (format: `123456789`)

### 3. Configure the Bot

Edit the configuration file:
```bash
sudo nano /etc/tgbot/config.env
```

**Required Settings:**
```bash
# Your bot token from @BotFather
BOT_TOKEN="123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"

# Your user ID from @userinfobot (comma-separated for multiple users)
AUTHORIZED_USERS="123456789,987654321"

# Main admin user ID (for critical operations)
ADMIN_USER_ID="123456789"
```

**Optional Settings:**
```bash
# Group chat IDs (if you want to use bot in groups)
AUTHORIZED_GROUPS="-1001234567890,-1009876543210"

# Auto-update URL (if hosting your own modified version)
UPDATE_URL="https://raw.githubusercontent.com/yourusername/yourrepo/main/tgbot.sh"

# Monitoring thresholds
BATTERY_LOW_THRESHOLD=20
BATTERY_HIGH_THRESHOLD=90
DISK_USAGE_THRESHOLD=90
MEMORY_USAGE_THRESHOLD=90

# Notification preferences
SEND_STARTUP_NOTIFICATIONS=true
SEND_SHUTDOWN_NOTIFICATIONS=true
SEND_BATTERY_NOTIFICATIONS=true
SEND_SYSTEM_ALERTS=true
```

### 4. Group Chat Setup (Optional)

To use the bot in group chats:

1. **Add bot to group:**
   - Add your bot to the desired group chat
   - Make the bot an administrator with necessary permissions

2. **Get group chat ID:**
   - Add the bot to the group
   - Send a message mentioning the bot: `@yourbotname /start`
   - Check the logs: `sudo journalctl -u tgbot.service | grep "chat_id"`
   - Add the group ID to `AUTHORIZED_GROUPS` in config

3. **Configure group privacy (if needed):**
   - Message @BotFather
   - Send `/mybots` and select your bot
   - Go to Bot Settings → Group Privacy
   - Turn off privacy mode so bot can read all messages

## 🎮 Usage

### Basic Commands

**Terminal Commands:**
- Simply type any shell command to execute it
- `ls -la` - List files
- `cd /home/user` - Change directory  
- `top` - View running processes
- `clear` - Clear terminal session
- `exit` - End terminal session

**Built-in Bot Commands:**
- `/start` - Initialize bot
- `/help` - Show available commands
- `/screenshot` - Take a screenshot
- `/brightness 0.8` - Set brightness to 80%
- `/volume up` - Increase volume
- `/volume set 50` - Set volume to 50%
- `/sysinfo` - Show system information
- `/network` - Show network information
- `/update` - Update bot (admin only)

### File Operations

**Upload Files:**
- Send any file to the bot through Telegram
- Files are saved to `/tmp/tgbot/` directory
- Maximum file size: 50MB

**Download Files:**
- Use commands like `cat filename.txt` to view file contents
- Use `ls` to list available files
- Bot will send file contents as text or file attachment

### Interactive Sessions

The bot maintains persistent terminal sessions:
- Your working directory and environment variables persist
- You can navigate directories and the bot remembers your location
- Multiple users can have separate independent sessions
- Sessions reset when you send `clear` or `exit`

### Group Chat Usage

When used in group chats:
- All authorized users can send commands
- Bot responds to direct messages mentioning the bot
- Group admins can control bot permissions
- Separate sessions maintained per group

## 🛠️ Management

### Service Control

```bash
# Start the bot
tgbot start

# Stop the bot  
tgbot stop

# Restart the bot
tgbot restart

# View bot status
tgbot status

# View live logs
tgbot logs

# Test configuration
tgbot test

# Edit configuration
tgbot config
```

### Manual Service Control

```bash
# Using systemctl directly
sudo systemctl start tgbot.service
sudo systemctl stop tgbot.service
sudo systemctl restart tgbot.service
sudo systemctl status tgbot.service

# View logs
sudo journalctl -u tgbot.service -f
```

### Log Files

- **Main bot log**: `/var/log/tgbot.log`
- **System monitoring**: `/var/log/tgbot_monitor.log`  
- **Systemd journal**: `journalctl -u tgbot.service`

### Configuration Locations

- **Bot script**: `/opt/tgbot/tgbot.sh`
- **Configuration**: `/etc/tgbot/config.env`
- **Service file**: `/etc/systemd/system/tgbot.service`
- **Helper scripts**: `/opt/tgbot/`

## 🔒 Security Considerations

### Access Control
- **Always use user ID whitelisting** - Never rely on usernames alone
- **Limit authorized users** - Only add trusted user IDs
- **Use admin controls** - Restrict sensitive operations to admin users only
- **Monitor access logs** - Regularly check who is using the bot

### Network Security
- Bot communicates only with Telegram's official API servers
- All API calls use HTTPS encryption
- No incoming network ports opened on your system
- Bot token is stored securely in protected configuration file

### System Security
- Bot runs with appropriate user permissions
- File operations are sandboxed to specific directories
- Command execution uses secure subprocess handling
- Automatic session timeouts prevent resource abuse

### Best Practices
1. **Regularly update** the bot and system packages
2. **Monitor logs** for suspicious activity
3. **Use strong bot tokens** - regenerate if compromised
4. **Limit file upload directories** - don't allow uploads to system directories
5. **Review authorized users** periodically
6. **Enable system monitoring** to detect unusual activity

## 🔧 Troubleshooting

### Common Issues

**Bot not responding:**
```bash
# Check if service is running
tgbot status

# Check configuration
tgbot test

# View recent logs
tgbot logs

# Restart the bot
tgbot restart
```

**Permission errors:**
```bash
# Check file permissions
ls -la /etc/tgbot/config.env
ls -la /opt/tgbot/tgbot.sh

# Fix permissions if needed
sudo chmod 600 /etc/tgbot/config.env
sudo chmod +x /opt/tgbot/tgbot.sh
```

**Network connectivity issues:**
```bash
# Test internet connection
ping -c 4 api.telegram.org

# Test Telegram API
curl -s "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"

# Check firewall settings
sudo ufw status
```

**Screenshot not working:**
```bash
# Install screenshot tools
sudo apt-get install gnome-screenshot scrot imagemagick

# Set display environment
export DISPLAY=:0

# Test screenshot manually
scrot test.png
```

**Audio control not working:**
```bash
# Install audio tools
sudo apt-get install alsa-utils pulseaudio-utils

# Test audio control manually
amixer sset Master 50%
pactl set-sink-volume 0 50%
```

### Debug Mode

Enable detailed logging by editing the service file:
```bash
sudo systemctl edit tgbot.service
```

Add these lines:
```ini
[Service]
Environment=DEBUG=1
ExecStart=/opt/tgbot/tgbot.sh --daemon --debug
```

Then restart the service:
```bash
sudo systemctl daemon-reload
sudo systemctl restart tgbot.service
```

### Log Analysis

Check specific log patterns:
```bash
# Recent errors
sudo journalctl -u tgbot.service | grep -i error

# Authorization attempts  
sudo journalctl -u tgbot.service | grep -i "unauthorized"

# Command executions
sudo journalctl -u tgbot.service | grep -i "processing message"

# File operations
sudo journalctl -u tgbot.service | grep -i "file"
```

## 🔄 Updates and Maintenance

### Automatic Updates

The bot supports automatic updates via Telegram:
1. Send the updated script file to the bot
2. Reply with `/update` command
3. Bot will download, verify, and replace itself
4. Service restarts automatically with new version

### Manual Updates

```bash
# Stop the service
sudo systemctl stop tgbot.service

# Backup current version
sudo cp /opt/tgbot/tgbot.sh /opt/tgbot/tgbot.sh.backup

# Download new version
sudo wget -O /opt/tgbot/tgbot.sh https://github.com/yourusername/yourrepo/raw/main/tgbot.sh

# Set permissions
sudo chmod +x /opt/tgbot/tgbot.sh

# Test configuration
/opt/tgbot/tgbot.sh --test

# Start the service
sudo systemctl start tgbot.service
```

### System Maintenance

**Regular maintenance tasks:**

1. **Clean temporary files:**
   ```bash
   sudo find /tmp/tgbot -type f -mtime +7 -delete
   ```

2. **Rotate logs manually:**
   ```bash
   sudo logrotate -f /etc/logrotate.d/tgbot
   ```

3. **Update system packages:**
   ```bash
   sudo apt update && sudo apt upgrade
   ```

4. **Check disk space:**
   ```bash
   df -h
   du -sh /opt/tgbot /etc/tgbot /var/log/tgbot*
   ```

5. **Review authorized users:**
   ```bash
   grep "AUTHORIZED_USERS" /etc/tgbot/config.env
   ```

## 🧪 Advanced Configuration

### Custom Commands

Add custom commands by modifying the `process_message()` function in the main script:

```bash
# Add after existing case statements
"/mycommand")
    # Your custom command logic here
    send_message "$chat_id" "Custom command executed"
    ;;
```

### Environment Variables

Set additional environment variables in the service file:
```bash
sudo systemctl edit tgbot.service
```

Add:
```ini
[Service]
Environment=CUSTOM_VAR=value
Environment=PATH=/usr/local/bin:/usr/bin:/bin
```

### Monitoring Integration

Integrate with external monitoring systems:

**Nagios/Icinga:**
```bash
# Add to Nagios config
define service {
    service_description    Telegram Bot
    check_command         check_systemd_service!tgbot
    host_name            yourhost
}
```

**Prometheus:**
```bash
# Add to node_exporter textfile collector
echo "tgbot_status $(systemctl is-active tgbot.service | grep -c active)" > /var/lib/node_exporter/textfile_collector/tgbot.prom
```

### Network Configuration

**Proxy Support:**
Add to configuration file:
```bash
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=http://proxy.example.com:8080
```

**Custom API Server:**
For regions where Telegram is blocked:
```bash
API_BASE_URL="https://api.telegram.org"  # Change to alternative server
```

## 📋 System Requirements

### Minimum Requirements
- **OS**: Linux (any distribution with systemd)
- **RAM**: 512MB available
- **Disk**: 100MB free space
- **Network**: Internet connection for Telegram API
- **Permissions**: Root access for installation

### Tested Distributions
- ✅ Ubuntu 18.04, 20.04, 22.04
- ✅ Debian 9, 10, 11
- ✅ CentOS 7, 8
- ✅ RHEL 7, 8
- ✅ Fedora 34, 35, 36
- ✅ Arch Linux
- ✅ openSUSE Leap 15.x

### Required Packages
- `bash` (version 4.0+)
- `curl`
- `jq`
- `systemd`
- `coreutils`

### Optional Packages
- `gnome-screenshot` or `scrot` or `imagemagick` (for screenshots)
- `alsa-utils` (for audio control)
- `xrandr` (for brightness control)
- `bc` (for calculations)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

### Coding Standards

- Follow existing shell script style
- Add comments for complex functions
- Test on multiple Linux distributions
- Update documentation for new features
- Maintain backward compatibility

## 🐛 Bug Reports

When reporting bugs, please include:
- Linux distribution and version
- Bot version
- Complete error messages
- Steps to reproduce
- Relevant log entries
- Configuration (with sensitive data removed)

## 💡 Feature Requests

Suggestions for new features are welcome! Please provide:
- Clear description of the feature
- Use case explanation
- Any implementation ideas
- Examples from other tools (if applicable)

## 📞 Support

- **Documentation**: Check this README first
- **Issues**: Use GitHub issues for bug reports
- **Discussions**: Use GitHub discussions for questions
- **Security**: Email security issues privately

---

**⚠️ Security Notice**: This bot provides complete access to your system. Only authorize trusted users and regularly monitor access logs. Use strong bot tokens and keep them secure.

**🔄 Last Updated**: $(date +'%Y-%m-%d')
**📍 Version**: 1.0.0
'''

with open('README.md', 'w') as f:
    f.write(readme_content)

print("Comprehensive README.md created!")