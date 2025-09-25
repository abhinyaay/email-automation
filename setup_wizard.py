#!/usr/bin/env python3
"""
Non-interactive Setup Wizard for HR Email Automation
Creates a guided setup process that works in all environments
"""

import json
import os
import re
import smtplib
import ssl

def check_current_config():
    """Check current configuration status"""
    print("🔍 Checking current configuration...")
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        issues = []
        
        # Check email
        if config.get('email', '') in ['', 'your_email@gmail.com']:
            issues.append("❌ Gmail email address not set")
        else:
            print(f"✅ Gmail address: {config['email']}")
        
        # Check password
        if config.get('password', '') in ['', 'your_app_password']:
            issues.append("❌ Gmail app password not set")
        else:
            print(f"✅ Gmail app password: {'*' * len(config['password'])}")
        
        # Check phone
        if config.get('phone_number', '') in ['', '+91-XXXXXXXXXX']:
            issues.append("❌ Phone number not set")
        else:
            print(f"✅ Phone number: {config['phone_number']}")
        
        # Check other files
        if os.path.exists('hr_contacts.csv'):
            import pandas as pd
            df = pd.read_csv('hr_contacts.csv')
            print(f"✅ HR contacts: {len(df)} contacts loaded")
        else:
            issues.append("❌ HR contacts file missing")
        
        if os.path.exists('Abhinay-Kumar.pdf'):
            size = os.path.getsize('Abhinay-Kumar.pdf') / (1024 * 1024)
            print(f"✅ Resume file: {size:.1f} MB")
        else:
            issues.append("❌ Resume PDF missing")
        
        if os.path.exists('email_template.html'):
            print("✅ Email template ready")
        else:
            issues.append("❌ Email template missing")
        
        return issues, config
        
    except Exception as e:
        return [f"❌ Error reading config.json: {e}"], {}

def create_setup_template():
    """Create a template file for manual setup"""
    template = """# HR Email Automation - Configuration Template

## STEP 1: Get Gmail App Password
1. Go to: https://myaccount.google.com/security
2. Enable 2-Factor Authentication (if not already enabled)
3. Click "App passwords"
4. Select "Mail" → "Other" → Name: "HR Email Automation"  
5. Copy the 16-character password (example: abcd efgh ijkl mnop)

## STEP 2: Update config.json
Replace these 3 lines in config.json with your actual information:

FIND THIS:
    "email": "your_email@gmail.com",
    "password": "your_app_password",
    "phone_number": "+91-XXXXXXXXXX",

REPLACE WITH:
    "email": "youractual@gmail.com",
    "password": "abcdefghijklmnop",
    "phone_number": "+91-9876543210",

## STEP 3: Test Setup
After updating config.json, run:
    python setup_wizard.py

## STEP 4: Start Sending
    python email_automation.py --batch-size 5
"""
    
    with open('SETUP_TEMPLATE.txt', 'w') as f:
        f.write(template)
    
    print("📝 Created SETUP_TEMPLATE.txt with detailed instructions")

def test_gmail_connection(config):
    """Test Gmail SMTP connection"""
    try:
        email = config['email']
        password = config['password']
        
        print(f"🔗 Testing Gmail connection for: {email}")
        
        context = ssl.create_default_context()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls(context=context)
        server.login(email, password)
        server.quit()
        
        print("✅ Gmail connection successful!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print("❌ Gmail authentication failed!")
        print("💡 Common fixes:")
        print("   • Make sure 2-Factor Authentication is enabled")
        print("   • Use App Password, not your regular Gmail password")
        print("   • Check that app password is exactly 16 characters")
        print("   • Remove any spaces from the app password")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def validate_email_format(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone_format(phone):
    """Validate phone format"""
    # Remove spaces and hyphens
    clean = re.sub(r'[\s-]', '', phone)
    # Check Indian phone format
    return re.match(r'^\+91[6-9]\d{9}$', clean) is not None

def show_config_help():
    """Show detailed help for configuration"""
    print("\n📋 Configuration Help:")
    print("=" * 50)
    
    print("\n🔧 How to edit config.json:")
    print("1. Open config.json in any text editor")
    print("2. Find these 3 lines:")
    print('   "email": "your_email@gmail.com",')
    print('   "password": "your_app_password",')
    print('   "phone_number": "+91-XXXXXXXXXX",')
    
    print("\n3. Replace with your actual details:")
    print('   "email": "yourname@gmail.com",')
    print('   "password": "abcdefghijklmnop",')
    print('   "phone_number": "+91-9876543210",')
    
    print("\n📧 Gmail App Password Setup:")
    print("• Go to: https://myaccount.google.com/security")
    print("• Enable 2-Factor Authentication")
    print("• App passwords → Mail → Other → 'HR Email'")
    print("• Copy the 16-character password")
    
    print("\n📱 Phone Number Format:")
    print("• Must start with +91")
    print("• Examples: +91-9876543210, +919876543210")

def create_sample_config():
    """Create a sample configuration with comments"""
    sample_config = {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "email": "REPLACE_WITH_YOUR_EMAIL@gmail.com",
        "password": "REPLACE_WITH_16_CHAR_APP_PASSWORD",
        "candidate_name": "Abhinay Kumar",
        "phone_number": "REPLACE_WITH_+91_PHONE_NUMBER",
        "daily_limit": 500,
        "min_delay": 30,
        "max_delay": 120,
        "business_hours_start": 9,
        "business_hours_end": 18,
        "resume_path": "Abhinay-Kumar.pdf",
        "hr_contacts_file": "hr_contacts.csv",
        "email_template_file": "email_template.html",
        "sent_emails_log": "sent_emails.json",
        "country_code": "IN"
    }
    
    with open('config_sample.json', 'w') as f:
        json.dump(sample_config, f, indent=4)
    
    print("📝 Created config_sample.json as reference")

def main():
    """Main setup wizard"""
    print("🧙‍♂️ HR Email Automation - Setup Wizard")
    print("=" * 50)
    
    # Check current status
    issues, config = check_current_config()
    
    if not issues:
        print("\n🎉 Configuration looks complete!")
        
        # Test Gmail connection
        if test_gmail_connection(config):
            print("\n✅ All systems ready!")
            print("\n🚀 You can now start sending emails:")
            print("   python email_automation.py --batch-size 5")
            print("   tail -f email_automation.log")
            return
        else:
            print("\n⚠️  Gmail connection failed - check your credentials")
    
    else:
        print(f"\n⚠️  Found {len(issues)} configuration issues:")
        for issue in issues:
            print(f"   {issue}")
    
    # Create helpful files
    print(f"\n🛠️  Creating setup helpers...")
    create_setup_template()
    create_sample_config()
    show_config_help()
    
    print(f"\n📋 Next Steps:")
    print(f"1. Follow instructions in SETUP_TEMPLATE.txt")
    print(f"2. Edit config.json with your Gmail credentials")
    print(f"3. Run this script again: python setup_wizard.py")
    print(f"4. Start sending emails: python email_automation.py --batch-size 5")

if __name__ == "__main__":
    main()
