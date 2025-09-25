#!/bin/bash

# HR Email Automation - EC2 Deployment Script
# Usage: ./deploy_to_ec2.sh your-key.pem ubuntu@your-ec2-ip

if [ $# -ne 2 ]; then
    echo "Usage: $0 <key-file.pem> <ubuntu@ec2-ip>"
    echo "Example: $0 my-key.pem ubuntu@3.25.123.45"
    exit 1
fi

KEY_FILE=$1
EC2_HOST=$2

echo "🚀 Deploying HR Email Automation to EC2..."
echo "Key file: $KEY_FILE"
echo "EC2 host: $EC2_HOST"

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ Key file not found: $KEY_FILE"
    exit 1
fi

# Set correct permissions for key file
chmod 400 "$KEY_FILE"

echo "📦 Uploading deployment package..."
scp -i "$KEY_FILE" hr-email-automation.tar.gz "$EC2_HOST":~/

echo "🔧 Setting up on EC2..."
ssh -i "$KEY_FILE" "$EC2_HOST" << 'EOF'
    # Update system
    sudo apt-get update -y
    
    # Install Python and dependencies
    sudo apt-get install python3 python3-pip python3-venv unzip -y
    
    # Extract files
    tar -xzf hr-email-automation.tar.gz
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install Python packages
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ Basic setup completed!"
    echo "📋 Next steps:"
    echo "1. Update config.json with your Gmail credentials"
    echo "2. Run the deployment script: chmod +x deploy_aws.sh && ./deploy_aws.sh"
    echo "3. Start the service: sudo systemctl start hr-email-automation"
EOF

echo "🎉 Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. SSH to your EC2: ssh -i $KEY_FILE $EC2_HOST"
echo "2. Update config.json with your Gmail credentials"
echo "3. Run: chmod +x deploy_aws.sh && ./deploy_aws.sh"
echo "4. Start service: sudo systemctl start hr-email-automation"
echo "5. Check status: sudo systemctl status hr-email-automation"
echo "6. View logs: tail -f email_automation.log"
