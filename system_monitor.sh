#!/bin/bash

# ===================================================================
# System Monitor Script for Telegram Bot
# ===================================================================

CONFIG_FILE="/etc/tgbot/config.env"
LOG_FILE="/var/log/tgbot_monitor.log"

# Load configuration
if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
else
    echo "$(date): Configuration file not found: $CONFIG_FILE" >> "$LOG_FILE"
    exit 1
fi

# Telegram API URL
API_URL="https://api.telegram.org/bot${BOT_TOKEN}"

# Send notification function
send_notification() {
    local message="$1"
    local chat_id="${ADMIN_USER_ID}"

    if [[ -n "$chat_id" && -n "$BOT_TOKEN" ]]; then
        curl -s -X POST "${API_URL}/sendMessage"             -d "chat_id=${chat_id}"             -d "text=🚨 *System Alert*%0A${message}"             -d "parse_mode=MarkdownV2" > /dev/null
    fi

    echo "$(date): $message" >> "$LOG_FILE"
}

# Check disk usage
check_disk_usage() {
    local threshold=${DISK_USAGE_THRESHOLD:-90}

    while read -r filesystem size used avail capacity mountpoint; do
        # Skip header and special filesystems
        [[ "$filesystem" == "Filesystem" || "$filesystem" == *"tmpfs"* || "$filesystem" == *"devtmpfs"* ]] && continue

        # Extract numeric part of capacity
        local usage_percent=${capacity%\%}

        if [[ "$usage_percent" -gt "$threshold" ]]; then
            send_notification "⚠️ **Disk Usage Alert**%0AFilesystem: $filesystem%0AMountpoint: $mountpoint%0AUsage: $capacity%0AUsed: $used / $size"
        fi
    done < <(df -h)
}

# Check memory usage
check_memory_usage() {
    local threshold=${MEMORY_USAGE_THRESHOLD:-90}

    local memory_info=$(free | grep Mem)
    local total=$(echo $memory_info | awk '{print $2}')
    local used=$(echo $memory_info | awk '{print $3}')
    local usage_percent=$((used * 100 / total))

    if [[ "$usage_percent" -gt "$threshold" ]]; then
        local used_human=$(echo $memory_info | awk '{print $3}' | numfmt --to=iec-i --suffix=B)
        local total_human=$(echo $memory_info | awk '{print $2}' | numfmt --to=iec-i --suffix=B)
        send_notification "⚠️ **Memory Usage Alert**%0AUsage: ${usage_percent}%25%0AUsed: $used_human / $total_human"
    fi
}

# Check CPU temperature (if available)
check_cpu_temperature() {
    local temp_files=("/sys/class/thermal/thermal_zone0/temp" "/sys/devices/virtual/thermal/thermal_zone0/temp")
    local threshold=80000  # 80 degrees Celsius in millidegrees

    for temp_file in "${temp_files[@]}"; do
        if [[ -f "$temp_file" ]]; then
            local temp=$(cat "$temp_file")
            local temp_celsius=$((temp / 1000))

            if [[ "$temp" -gt "$threshold" ]]; then
                send_notification "🔥 **High CPU Temperature**%0ATemperature: ${temp_celsius}°C%0AThreshold: $((threshold / 1000))°C"
            fi
            break
        fi
    done
}

# Check for failed login attempts
check_failed_logins() {
    local failed_logins=$(journalctl --since="1 hour ago" | grep -i "failed\|failure" | grep -i "login\|ssh\|auth" | wc -l)

    if [[ "$failed_logins" -gt 10 ]]; then
        send_notification "🔐 **Security Alert**%0A$failed_logins failed login attempts in the last hour"
    fi
}

# Check system load
check_system_load() {
    local load_avg=$(uptime | awk -F'load average:' '{ print $2 }' | awk '{ print $1 }' | sed 's/,//')
    local cpu_cores=$(nproc)
    local load_threshold=$((cpu_cores * 2))  # Alert if load is 2x CPU cores

    # Convert load average to integer for comparison (multiply by 100)
    local load_int=$(echo "$load_avg * 100" | bc | cut -d. -f1)
    local threshold_int=$((load_threshold * 100))

    if [[ "$load_int" -gt "$threshold_int" ]]; then
        send_notification "📈 **High System Load**%0ALoad Average: $load_avg%0ACPU Cores: $cpu_cores%0AThreshold: $load_threshold"
    fi
}

# Check network connectivity
check_network() {
    if ! ping -c 1 -W 5 8.8.8.8 &> /dev/null; then
        send_notification "🌐 **Network Connectivity Lost**%0ACannot reach external servers"
    fi
}

# Check service status
check_critical_services() {
    local services=("ssh" "NetworkManager" "systemd-networkd")

    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            continue
        elif systemctl list-unit-files "$service.service" &>/dev/null; then
            send_notification "⚠️ **Service Down**%0AService: $service%0AStatus: $(systemctl is-active $service)"
        fi
    done
}

# Main monitoring function
run_monitoring() {
    echo "$(date): Starting system monitoring check" >> "$LOG_FILE"

    # Only run monitoring if notifications are enabled
    if [[ "${SEND_SYSTEM_ALERTS:-true}" == "true" ]]; then
        check_disk_usage
        check_memory_usage
        check_cpu_temperature
        check_system_load
        check_network
        check_critical_services
        check_failed_logins
    fi

    echo "$(date): System monitoring check completed" >> "$LOG_FILE"
}

# Check command line arguments
case "${1:-}" in
    "--disk")
        check_disk_usage
        ;;
    "--memory")
        check_memory_usage
        ;;
    "--temperature"|"--temp")
        check_cpu_temperature
        ;;
    "--load")
        check_system_load
        ;;
    "--network")
        check_network
        ;;
    "--services")
        check_critical_services
        ;;
    "--security")
        check_failed_logins
        ;;
    "--all"|"")
        run_monitoring
        ;;
    *)
        echo "System Monitor for Telegram Bot"
        echo "Usage: $0 [--disk|--memory|--temp|--load|--network|--services|--security|--all]"
        echo ""
        echo "Options:"
        echo "  --disk       Check disk usage"
        echo "  --memory     Check memory usage" 
        echo "  --temp       Check CPU temperature"
        echo "  --load       Check system load"
        echo "  --network    Check network connectivity"
        echo "  --services   Check critical services"
        echo "  --security   Check for failed logins"
        echo "  --all        Run all checks (default)"
        exit 0
        ;;
esac
