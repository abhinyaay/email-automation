#!/bin/bash

# AWS EC2 Deployment Script for HR Email Automation
# This script sets up the email automation system on AWS EC2

echo "=== HR Email Automation AWS Deployment ==="

# Update system packages
echo "Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python 3.9+ and pip
echo "Installing Python and pip..."
sudo apt-get install python3 python3-pip python3-venv -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install cron supervisor nginx -y

# Create application directory
echo "Setting up application directory..."
APP_DIR="/home/ubuntu/hr-email-automation"
sudo mkdir -p $APP_DIR
sudo chown ubuntu:ubuntu $APP_DIR
cd $APP_DIR

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install pandas openpyxl schedule holidays

# Create systemd service file
echo "Creating systemd service..."
sudo tee /etc/systemd/system/hr-email-automation.service > /dev/null <<EOF
[Unit]
Description=HR Email Automation Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python email_automation.py --continuous
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create log rotation configuration
echo "Setting up log rotation..."
sudo tee /etc/logrotate.d/hr-email-automation > /dev/null <<EOF
$APP_DIR/email_automation.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

# Create monitoring script
echo "Creating monitoring script..."
tee $APP_DIR/monitor.sh > /dev/null <<'EOF'
#!/bin/bash

# Monitor HR Email Automation Service
LOG_FILE="/home/ubuntu/hr-email-automation/email_automation.log"
SERVICE_NAME="hr-email-automation"

# Check if service is running
if ! systemctl is-active --quiet $SERVICE_NAME; then
    echo "$(date): Service $SERVICE_NAME is not running. Restarting..." >> $LOG_FILE
    sudo systemctl restart $SERVICE_NAME
fi

# Check log file size (rotate if > 100MB)
if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(du -m "$LOG_FILE" | cut -f1)
    if [ $LOG_SIZE -gt 100 ]; then
        echo "$(date): Log file too large. Rotating..." >> $LOG_FILE
        sudo logrotate -f /etc/logrotate.d/hr-email-automation
    fi
fi

# Send daily status email (optional)
# You can implement this to get daily reports
EOF

chmod +x $APP_DIR/monitor.sh

# Add monitoring to crontab
echo "Setting up monitoring cron job..."
(crontab -l 2>/dev/null; echo "*/15 * * * * /home/ubuntu/hr-email-automation/monitor.sh") | crontab -

# Create backup script
echo "Creating backup script..."
tee $APP_DIR/backup.sh > /dev/null <<'EOF'
#!/bin/bash

BACKUP_DIR="/home/ubuntu/backups"
APP_DIR="/home/ubuntu/hr-email-automation"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup configuration and logs
tar -czf $BACKUP_DIR/hr-email-backup-$DATE.tar.gz \
    $APP_DIR/config.json \
    $APP_DIR/sent_emails.json \
    $APP_DIR/email_automation.log \
    $APP_DIR/hr_contacts.csv

# Keep only last 7 days of backups
find $BACKUP_DIR -name "hr-email-backup-*.tar.gz" -mtime +7 -delete

echo "$(date): Backup completed - hr-email-backup-$DATE.tar.gz"
EOF

chmod +x $APP_DIR/backup.sh

# Add backup to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/hr-email-automation/backup.sh") | crontab -

# Create security hardening script
echo "Creating security hardening script..."
tee $APP_DIR/secure.sh > /dev/null <<'EOF'
#!/bin/bash

# Basic security hardening for the email automation server

# Update firewall rules
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Secure SSH (disable password authentication, use key-based only)
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Install fail2ban
sudo apt-get install fail2ban -y

# Create fail2ban configuration for SSH
sudo tee /etc/fail2ban/jail.local > /dev/null <<EOL
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
EOL

sudo systemctl restart fail2ban

echo "Basic security hardening completed"
EOF

chmod +x $APP_DIR/secure.sh

echo "=== Deployment Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Copy your files to $APP_DIR:"
echo "   - email_automation.py"
echo "   - config.json (update with your credentials)"
echo "   - hr_contacts.csv"
echo "   - email_template.html"
echo "   - Abhinay-Kumar.pdf"
echo ""
echo "2. Update config.json with your Gmail credentials"
echo "3. Run security hardening: ./secure.sh"
echo "4. Start the service: sudo systemctl enable hr-email-automation && sudo systemctl start hr-email-automation"
echo "5. Check status: sudo systemctl status hr-email-automation"
echo "6. View logs: tail -f email_automation.log"
echo ""
echo "The service will automatically start on boot and restart if it crashes."
echo "Monitoring runs every 15 minutes, backups run daily at 2 AM."
