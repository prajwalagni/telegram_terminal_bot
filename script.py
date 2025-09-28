# First, let's create the main telegram bot shell script
main_script = '''#!/bin/bash

# ===================================================================
# Telegram Terminal Bot - Complete Remote Access Shell Script
# ===================================================================
# Features:
# - Send/receive messages, files, and media via Telegram Bot API
# - Execute terminal commands with interactive support
# - Built-in system control features (screenshot, brightness, audio)
# - Group chat support with admin permissions
# - Auto-update mechanism via Telegram
# - System monitoring and notifications
# - Auto-start on boot/login
# ===================================================================

# Configuration
SCRIPT_VERSION="1.0.0"
SCRIPT_NAME="tgbot.sh"
CONFIG_FILE="/etc/tgbot/config.env"
LOG_FILE="/var/log/tgbot.log"
TEMP_DIR="/tmp/tgbot"
UPDATE_URL="https://raw.githubusercontent.com/yourusername/yourrepo/main/tgbot.sh"

# Load configuration
if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
else
    echo "$(date): Configuration file not found: $CONFIG_FILE" >> "$LOG_FILE"
    exit 1
fi

# Required variables (should be set in config.env):
# BOT_TOKEN="your_bot_token_here"
# AUTHORIZED_USERS="user_id1,user_id2,user_id3"  # Comma-separated
# AUTHORIZED_GROUPS="group_id1,group_id2"        # Comma-separated (optional)
# ADMIN_USER_ID="main_admin_user_id"             # For critical operations

# Telegram API URLs
API_URL="https://api.telegram.org/bot${BOT_TOKEN}"
FILE_API_URL="https://api.telegram.org/file/bot${BOT_TOKEN}"

# Create necessary directories
mkdir -p "$TEMP_DIR" "/etc/tgbot" "/var/log"

# ===================================================================
# Utility Functions
# ===================================================================

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

# Check if user is authorized
is_authorized() {
    local user_id="$1"
    local chat_id="$2"
    
    # Check individual user authorization
    if [[ "$AUTHORIZED_USERS" == *"$user_id"* ]]; then
        return 0
    fi
    
    # Check group authorization (if chat_id is negative, it\'s a group)
    if [[ "$chat_id" -lt 0 && -n "$AUTHORIZED_GROUPS" ]]; then
        if [[ "$AUTHORIZED_GROUPS" == *"$chat_id"* ]]; then
            return 0
        fi
    fi
    
    return 1
}

# Send message via Telegram
send_message() {
    local chat_id="$1"
    local text="$2"
    local parse_mode="${3:-}"
    
    local data="chat_id=${chat_id}&text=${text}"
    [[ -n "$parse_mode" ]] && data="${data}&parse_mode=${parse_mode}"
    
    curl -s -X POST "${API_URL}/sendMessage" -d "$data" > /dev/null
}

# Send file via Telegram
send_file() {
    local chat_id="$1"
    local file_path="$2"
    local caption="${3:-}"
    
    if [[ ! -f "$file_path" ]]; then
        send_message "$chat_id" "File not found: $file_path"
        return 1
    fi
    
    local file_size=$(stat -c%s "$file_path")
    if [[ $file_size -gt 52428800 ]]; then  # 50MB limit
        send_message "$chat_id" "File too large (>50MB): $(du -h "$file_path" | cut -f1)"
        return 1
    fi
    
    # Determine file type and API method
    local file_ext="${file_path##*.}"
    local method="sendDocument"
    local field="document"
    
    case "${file_ext,,}" in
        jpg|jpeg|png|gif|bmp)
            method="sendPhoto"
            field="photo"
            ;;
        mp4|avi|mkv|mov)
            method="sendVideo"
            field="video"
            ;;
        mp3|ogg|m4a|wav)
            method="sendAudio"
            field="audio"
            ;;
    esac
    
    local caption_param=""
    [[ -n "$caption" ]] && caption_param="-F caption=\"$caption\""
    
    eval curl -s -X POST "${API_URL}/${method}" \
        -F "chat_id=${chat_id}" \
        -F "${field}=@\"${file_path}\"" \
        ${caption_param} > /dev/null
}

# Download file from Telegram
download_file() {
    local file_id="$1"
    local save_path="$2"
    
    local file_info=$(curl -s "${API_URL}/getFile?file_id=${file_id}")
    local file_path=$(echo "$file_info" | jq -r '.result.file_path')
    
    if [[ "$file_path" != "null" ]]; then
        curl -s "${FILE_API_URL}/${file_path}" -o "$save_path"
        return 0
    else
        return 1
    fi
}

# ===================================================================
# Interactive Terminal Functions
# ===================================================================

# Handle interactive command execution
execute_interactive_command() {
    local chat_id="$1"
    local command="$2"
    local session_file="$TEMP_DIR/session_${chat_id}"
    
    # Create session file if it doesn\'t exist
    if [[ ! -f "$session_file" ]]; then
        echo "cd \"$HOME\"" > "$session_file"
        echo "export PS1=\"\\\\u@\\\\h:\\\\w\\\\$ \"" >> "$session_file"
    fi
    
    # Add command to session
    echo "$command" >> "$session_file"
    
    # Execute the session and capture output
    local output
    local exit_code
    
    # Use timeout to prevent hanging commands
    timeout 30s bash -i < "$session_file" > "$TEMP_DIR/output_${chat_id}" 2>&1
    exit_code=$?
    
    if [[ $exit_code -eq 124 ]]; then
        output="Command timed out after 30 seconds"
    else
        output=$(tail -n 50 "$TEMP_DIR/output_${chat_id}" 2>/dev/null || echo "No output")
    fi
    
    # Handle special commands
    case "$command" in
        "clear"|"cls")
            rm -f "$session_file"
            output="Terminal cleared"
            ;;
        "exit"|"quit")
            rm -f "$session_file" "$TEMP_DIR/output_${chat_id}"
            output="Session ended"
            ;;
    esac
    
    # Send output in chunks if too long
    local max_length=4000
    if [[ ${#output} -gt $max_length ]]; then
        local temp_file="$TEMP_DIR/long_output_${chat_id}.txt"
        echo "$output" > "$temp_file"
        send_file "$chat_id" "$temp_file" "Command output (file)"
        rm -f "$temp_file"
    else
        send_message "$chat_id" "\`\`\`
$output
\`\`\`" "MarkdownV2"
    fi
}

# ===================================================================
# Built-in Bot Commands
# ===================================================================

# Take screenshot
cmd_screenshot() {
    local chat_id="$1"
    local screenshot_file="$TEMP_DIR/screenshot_$(date +%s).png"
    
    # Try different screenshot tools
    if command -v gnome-screenshot &> /dev/null; then
        DISPLAY=:0 gnome-screenshot -f "$screenshot_file" 2>/dev/null
    elif command -v scrot &> /dev/null; then
        DISPLAY=:0 scrot "$screenshot_file" 2>/dev/null
    elif command -v import &> /dev/null; then
        DISPLAY=:0 import -window root "$screenshot_file" 2>/dev/null
    else
        send_message "$chat_id" "No screenshot tool available (gnome-screenshot, scrot, or imagemagick)"
        return 1
    fi
    
    if [[ -f "$screenshot_file" ]]; then
        send_file "$chat_id" "$screenshot_file" "Screenshot - $(date)"
        rm -f "$screenshot_file"
    else
        send_message "$chat_id" "Failed to capture screenshot"
    fi
}

# Control brightness
cmd_brightness() {
    local chat_id="$1"
    local level="$2"
    
    if [[ -z "$level" ]]; then
        send_message "$chat_id" "Usage: /brightness <0.1-1.0>\\nExample: /brightness 0.8"
        return
    fi
    
    # Get primary display
    local display=$(DISPLAY=:0 xrandr | grep " connected primary" | cut -d" " -f1)
    if [[ -z "$display" ]]; then
        display=$(DISPLAY=:0 xrandr | grep " connected" | head -1 | cut -d" " -f1)
    fi
    
    if [[ -n "$display" ]]; then
        DISPLAY=:0 xrandr --output "$display" --brightness "$level"
        send_message "$chat_id" "Brightness set to ${level} for display ${display}"
    else
        send_message "$chat_id" "No display found"
    fi
}

# Control volume
cmd_volume() {
    local chat_id="$1"
    local action="$2"
    local value="$3"
    
    case "$action" in
        "up")
            amixer sset Master 5%+ unmute &> /dev/null
            send_message "$chat_id" "Volume increased"
            ;;
        "down")
            amixer sset Master 5%- unmute &> /dev/null
            send_message "$chat_id" "Volume decreased"
            ;;
        "mute")
            amixer sset Master mute &> /dev/null
            send_message "$chat_id" "Volume muted"
            ;;
        "unmute")
            amixer sset Master unmute &> /dev/null
            send_message "$chat_id" "Volume unmuted"
            ;;
        "set")
            if [[ -n "$value" ]]; then
                amixer sset Master "${value}%" unmute &> /dev/null
                send_message "$chat_id" "Volume set to ${value}%"
            else
                send_message "$chat_id" "Usage: /volume set <0-100>"
            fi
            ;;
        *)
            send_message "$chat_id" "Usage: /volume <up|down|mute|unmute|set> [value]"
            ;;
    esac
}

# System information
cmd_sysinfo() {
    local chat_id="$1"
    local info=""
    
    info+="🖥️ *System Information*\\n"
    info+="• Hostname: $(hostname)\\n"
    info+="• OS: $(lsb_release -d 2>/dev/null | cut -f2 || echo "Unknown")\\n"
    info+="• Kernel: $(uname -r)\\n"
    info+="• Uptime: $(uptime -p 2>/dev/null || uptime | cut -d, -f1)\\n"
    info+="• Load: $(uptime | awk -F\'load average:\' \'{ print $2 }\')\\n"
    info+="• Memory: $(free -h | grep Mem | awk \'{print $3"/"$2}\')\\n"
    info+="• Disk: $(df -h / | tail -1 | awk \'{print $3"/"$2" ("$5" used)"}\')\\n"
    info+="• CPU: $(grep "model name" /proc/cpuinfo | head -1 | cut -d: -f2 | xargs)\\n"
    
    # Battery info (if available)
    if [[ -f /sys/class/power_supply/BAT0/capacity ]]; then
        local battery=$(cat /sys/class/power_supply/BAT0/capacity)
        local status=$(cat /sys/class/power_supply/BAT0/status)
        info+="• Battery: ${battery}% (${status})\\n"
    fi
    
    send_message "$chat_id" "$info" "MarkdownV2"
}

# Network information
cmd_network() {
    local chat_id="$1"
    local info=""
    
    info+="🌐 *Network Information*\\n"
    info+="• Public IP: $(curl -s ifconfig.me || echo "Unknown")\\n"
    info+="• Local IPs:\\n"
    
    # Get local IPs
    while read -r line; do
        [[ -n "$line" ]] && info+="  - $line\\n"
    done < <(ip -4 addr show | grep -oP "(?<=inet\\s)\\d+(\\.\\d+){3}" | grep -v "127.0.0.1")
    
    # WiFi info
    local wifi_info=$(iwgetid -r 2>/dev/null)
    if [[ -n "$wifi_info" ]]; then
        info+="• WiFi: $wifi_info\\n"
    fi
    
    send_message "$chat_id" "$info" "MarkdownV2"
}

# Update bot
cmd_update() {
    local chat_id="$1"
    
    # Only admin can update
    if [[ "$2" != "$ADMIN_USER_ID" ]]; then
        send_message "$chat_id" "❌ Only admin can update the bot"
        return
    fi
    
    send_message "$chat_id" "🔄 Updating bot..."
    
    # Download new version
    local temp_script="$TEMP_DIR/tgbot_new.sh"
    if curl -s "$UPDATE_URL" -o "$temp_script"; then
        # Verify it\'s a valid script
        if bash -n "$temp_script" 2>/dev/null; then
            # Replace current script
            cp "$temp_script" "$0"
            chmod +x "$0"
            send_message "$chat_id" "✅ Bot updated successfully. Restarting..."
            rm -f "$temp_script"
            exec "$0" "$@"
        else
            send_message "$chat_id" "❌ Downloaded script is invalid"
            rm -f "$temp_script"
        fi
    else
        send_message "$chat_id" "❌ Failed to download update"
    fi
}

# Help command
cmd_help() {
    local chat_id="$1"
    local help_text=""
    
    help_text+="🤖 *Telegram Terminal Bot Commands*\\n\\n"
    help_text+="*Built-in Commands:*\\n"
    help_text+="• \`/screenshot\` - Take a screenshot\\n"
    help_text+="• \`/brightness <0.1-1.0>\` - Adjust screen brightness\\n"
    help_text+="• \`/volume <up|down|mute|unmute|set> [value]\` - Control volume\\n"
    help_text+="• \`/sysinfo\` - Show system information\\n"
    help_text+="• \`/network\` - Show network information\\n"
    help_text+="• \`/update\` - Update bot (admin only)\\n"
    help_text+="• \`/help\` - Show this help\\n\\n"
    help_text+="*Terminal Commands:*\\n"
    help_text+="• Just type any shell command to execute it\\n"
    help_text+="• \`clear\` - Clear terminal session\\n"
    help_text+="• \`exit\` - End terminal session\\n\\n"
    help_text+="*File Operations:*\\n"
    help_text+="• Send files to upload them to the server\\n"
    help_text+="• Use commands like \`ls\`, \`cat\`, etc. to manage files\\n"
    
    send_message "$chat_id" "$help_text" "MarkdownV2"
}

# ===================================================================
# File Handling
# ===================================================================

handle_file() {
    local chat_id="$1"
    local file_id="$2"
    local file_name="$3"
    
    # Download the file
    local file_path="$TEMP_DIR/$file_name"
    if download_file "$file_id" "$file_path"; then
        # Check if it\'s an update request (reply to /update command)
        if [[ "$file_name" == *.sh ]]; then
            send_message "$chat_id" "Received script file. Reply with '/update' to update the bot."
        else
            send_message "$chat_id" "File downloaded: $file_path\\nSize: $(du -h "$file_path" | cut -f1)"
        fi
    else
        send_message "$chat_id" "Failed to download file"
    fi
}

# ===================================================================
# Message Processing
# ===================================================================

process_message() {
    local update="$1"
    
    # Parse update JSON
    local message=$(echo "$update" | jq -r '.message // .edited_message // empty')
    [[ -z "$message" || "$message" == "null" ]] && return
    
    local chat_id=$(echo "$message" | jq -r '.chat.id')
    local user_id=$(echo "$message" | jq -r '.from.id')
    local text=$(echo "$message" | jq -r '.text // empty')
    local username=$(echo "$message" | jq -r '.from.username // .from.first_name // "Unknown"')
    
    # Check authorization
    if ! is_authorized "$user_id" "$chat_id"; then
        log_message "Unauthorized access attempt from user $user_id ($username) in chat $chat_id"
        return
    fi
    
    log_message "Processing message from $username ($user_id) in chat $chat_id: $text"
    
    # Handle file uploads
    local document=$(echo "$message" | jq -r '.document // empty')
    if [[ -n "$document" && "$document" != "null" ]]; then
        local file_id=$(echo "$document" | jq -r '.file_id')
        local file_name=$(echo "$document" | jq -r '.file_name // "document"')
        handle_file "$chat_id" "$file_id" "$file_name"
        return
    fi
    
    # Handle text messages
    if [[ -n "$text" && "$text" != "null" ]]; then
        case "$text" in
            "/start")
                send_message "$chat_id" "🤖 Telegram Terminal Bot is ready!\\nType /help for available commands."
                ;;
            "/help")
                cmd_help "$chat_id"
                ;;
            "/screenshot")
                cmd_screenshot "$chat_id"
                ;;
            "/brightness"*)
                local brightness_value=$(echo "$text" | cut -d" " -f2)
                cmd_brightness "$chat_id" "$brightness_value"
                ;;
            "/volume"*)
                local volume_action=$(echo "$text" | cut -d" " -f2)
                local volume_value=$(echo "$text" | cut -d" " -f3)
                cmd_volume "$chat_id" "$volume_action" "$volume_value"
                ;;
            "/sysinfo")
                cmd_sysinfo "$chat_id"
                ;;
            "/network")
                cmd_network "$chat_id"
                ;;
            "/update")
                cmd_update "$chat_id" "$user_id"
                ;;
            *)
                # Execute as terminal command
                execute_interactive_command "$chat_id" "$text"
                ;;
        esac
    fi
}

# ===================================================================
# System Event Handlers
# ===================================================================

# Send system notification
send_system_notification() {
    local message="$1"
    local user_id="$ADMIN_USER_ID"
    
    if [[ -n "$user_id" ]]; then
        send_message "$user_id" "🖥️ *System Notification*\\n$message" "MarkdownV2"
    fi
    log_message "System notification: $message"
}

# Startup notification
send_startup_notification() {
    local user=$(whoami)
    local hostname=$(hostname)
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    send_system_notification "✅ User **$user** logged in to **$hostname** at $timestamp"
}

# Shutdown handler
handle_shutdown() {
    local hostname=$(hostname)
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    send_system_notification "🔄 System **$hostname** is shutting down at $timestamp"
}

# Battery monitoring
monitor_battery() {
    local battery_file="/sys/class/power_supply/BAT0/capacity"
    
    if [[ -f "$battery_file" ]]; then
        local battery_level=$(cat "$battery_file")
        local battery_status=$(cat "/sys/class/power_supply/BAT0/status")
        
        # Alert on low battery
        if [[ "$battery_level" -lt 20 && "$battery_status" == "Discharging" ]]; then
            send_system_notification "⚠️ **Low Battery Alert**\\nBattery level: ${battery_level}%\\nStatus: ${battery_status}"
        fi
        
        # Alert on high battery when charging
        if [[ "$battery_level" -gt 90 && "$battery_status" == "Charging" ]]; then
            send_system_notification "🔋 **Battery Full**\\nBattery level: ${battery_level}%\\nConsider unplugging charger"
        fi
    fi
}

# ===================================================================
# Main Loop
# ===================================================================

# Signal handlers
trap handle_shutdown SIGTERM SIGINT

# Main bot loop
main() {
    local offset=0
    
    # Send startup notification
    send_startup_notification
    
    # Start battery monitoring in background
    if [[ -f "/sys/class/power_supply/BAT0/capacity" ]]; then
        (
            while true; do
                monitor_battery
                sleep 300  # Check every 5 minutes
            done
        ) &
    fi
    
    log_message "Telegram bot started (PID: $$)"
    
    while true; do
        # Get updates from Telegram
        local response=$(curl -s "${API_URL}/getUpdates?offset=${offset}&timeout=30")
        
        # Check if response is valid JSON
        if ! echo "$response" | jq . >/dev/null 2>&1; then
            log_message "Invalid JSON response from Telegram API"
            sleep 5
            continue
        fi
        
        local ok=$(echo "$response" | jq -r '.ok')
        if [[ "$ok" != "true" ]]; then
            log_message "Telegram API error: $(echo "$response" | jq -r '.description')"
            sleep 5
            continue
        fi
        
        # Process each update
        local updates=$(echo "$response" | jq -c '.result[]')
        while IFS= read -r update; do
            [[ -n "$update" ]] && process_message "$update"
            
            # Update offset
            local update_id=$(echo "$update" | jq -r '.update_id')
            offset=$((update_id + 1))
        done <<< "$updates"
        
        # Small delay to prevent API hammering
        sleep 1
    done
}

# ===================================================================
# Service Management
# ===================================================================

# Install as systemd service
install_service() {
    local service_file="/etc/systemd/system/tgbot.service"
    
    cat > "$service_file" << EOF
[Unit]
Description=Telegram Terminal Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
ExecStart=$0 --daemon
Restart=always
RestartSec=10
Environment=DISPLAY=:0
Environment=HOME=/root

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable tgbot.service
    systemctl start tgbot.service
    
    echo "Service installed and started successfully"
}

# Uninstall systemd service
uninstall_service() {
    systemctl stop tgbot.service 2>/dev/null
    systemctl disable tgbot.service 2>/dev/null
    rm -f /etc/systemd/system/tgbot.service
    systemctl daemon-reload
    
    echo "Service uninstalled successfully"
}

# ===================================================================
# Script Entry Point
# ===================================================================

case "${1:-}" in
    "--daemon")
        main
        ;;
    "--install")
        install_service
        ;;
    "--uninstall")
        uninstall_service
        ;;
    "--test")
        echo "Testing bot configuration..."
        if [[ -z "$BOT_TOKEN" ]]; then
            echo "ERROR: BOT_TOKEN not set in config file"
            exit 1
        fi
        
        # Test API connection
        local me=$(curl -s "${API_URL}/getMe")
        if echo "$me" | jq -e '.ok' >/dev/null 2>&1; then
            local bot_name=$(echo "$me" | jq -r '.result.username')
            echo "SUCCESS: Connected to bot @$bot_name"
        else
            echo "ERROR: Failed to connect to Telegram API"
            exit 1
        fi
        ;;
    *)
        echo "Telegram Terminal Bot v${SCRIPT_VERSION}"
        echo "Usage: $0 [--daemon|--install|--uninstall|--test]"
        echo ""
        echo "Options:"
        echo "  --daemon     Run as daemon (main bot loop)"
        echo "  --install    Install as systemd service"
        echo "  --uninstall  Remove systemd service"
        echo "  --test       Test configuration"
        echo ""
        echo "Configuration file: $CONFIG_FILE"
        exit 0
        ;;
esac
'''

# Save the main script
with open('tgbot.sh', 'w') as f:
    f.write(main_script)

print("Main script 'tgbot.sh' created successfully!")