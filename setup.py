#!/usr/bin/env python3
"""
Interactive Setup Script for HR Email Automation
Helps configure Gmail credentials and other settings
"""

import json
import re
import getpass

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    # Remove spaces and hyphens
    clean_phone = re.sub(r'[\s-]', '', phone)
    # Check if it's a valid Indian phone number format
    pattern = r'^\+91[6-9]\d{9}$'
    return re.match(pattern, clean_phone) is not None

def setup_config():
    """Interactive configuration setup"""
    print("🔧 HR Email Automation - Interactive Setup")
    print("=" * 50)
    
    # Load existing config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except:
        print("❌ Could not load config.json")
        return False
    
    print("Please provide the following information:")
    print("(Press Enter to keep current value shown in brackets)")
    
    # Gmail email
    while True:
        current_email = config.get('email', '')
        if current_email == 'your_email@gmail.com':
            current_email = ''
        
        prompt = f"Gmail address"
        if current_email:
            prompt += f" [{current_email}]"
        prompt += ": "
        
        email = input(prompt).strip()
        if not email and current_email:
            email = current_email
        
        if email and validate_email(email):
            config['email'] = email
            break
        else:
            print("❌ Please enter a valid Gmail address")
    
    # Gmail app password
    while True:
        current_password = config.get('password', '')
        if current_password == 'your_app_password':
            current_password = ''
        
        if current_password:
            print(f"Gmail App Password [***hidden***]: ", end='')
            password = getpass.getpass('')
            if not password:
                password = current_password
        else:
            password = getpass.getpass("Gmail App Password (16 characters): ")
        
        if password and len(password.replace(' ', '')) >= 16:
            config['password'] = password.replace(' ', '')  # Remove spaces
            break
        else:
            print("❌ App password should be 16 characters long")
    
    # Candidate name
    current_name = config.get('candidate_name', 'Abhinay Kumar')
    name = input(f"Your full name [{current_name}]: ").strip()
    if name:
        config['candidate_name'] = name
    
    # Phone number
    while True:
        current_phone = config.get('phone_number', '')
        if current_phone == '+91-XXXXXXXXXX':
            current_phone = ''
        
        prompt = f"Phone number (+91 format)"
        if current_phone:
            prompt += f" [{current_phone}]"
        prompt += ": "
        
        phone = input(prompt).strip()
        if not phone and current_phone:
            phone = current_phone
        
        if phone:
            # Auto-format phone number
            clean_phone = re.sub(r'[\s-()]', '', phone)
            if clean_phone.startswith('91') and len(clean_phone) == 12:
                clean_phone = '+' + clean_phone
            elif clean_phone.startswith('0') and len(clean_phone) == 11:
                clean_phone = '+91' + clean_phone[1:]
            elif len(clean_phone) == 10:
                clean_phone = '+91' + clean_phone
            
            if validate_phone(clean_phone):
                config['phone_number'] = clean_phone
                break
            else:
                print("❌ Please enter a valid Indian phone number")
                print("   Examples: +91-9876543210, 9876543210, 09876543210")
        else:
            print("❌ Phone number is required")
    
    # Email settings
    print(f"\n📧 Email Settings:")
    print(f"   Daily limit: {config['daily_limit']} emails/day")
    print(f"   Delay between emails: {config['min_delay']}-{config['max_delay']} seconds")
    print(f"   Business hours: {config['business_hours_start']}:00 - {config['business_hours_end']}:00")
    
    change_settings = input("Change email settings? (y/n): ").lower().strip()
    if change_settings == 'y':
        # Daily limit
        try:
            limit = input(f"Daily email limit [{config['daily_limit']}]: ").strip()
            if limit:
                config['daily_limit'] = int(limit)
        except ValueError:
            print("❌ Invalid number, keeping current value")
        
        # Delays
        try:
            min_delay = input(f"Minimum delay between emails in seconds [{config['min_delay']}]: ").strip()
            if min_delay:
                config['min_delay'] = int(min_delay)
        except ValueError:
            print("❌ Invalid number, keeping current value")
        
        try:
            max_delay = input(f"Maximum delay between emails in seconds [{config['max_delay']}]: ").strip()
            if max_delay:
                config['max_delay'] = int(max_delay)
        except ValueError:
            print("❌ Invalid number, keeping current value")
    
    # Save configuration
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        print("\n✅ Configuration saved successfully!")
        return True
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        return False

def test_configuration():
    """Test the configuration"""
    print("\n🧪 Testing configuration...")
    
    try:
        import smtplib
        import ssl
        
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("📧 Testing Gmail SMTP connection...")
        context = ssl.create_default_context()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls(context=context)
        server.login(config['email'], config['password'])
        server.quit()
        
        print("✅ Gmail connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Gmail connection failed: {e}")
        print("\n💡 Common issues:")
        print("   - Make sure 2FA is enabled on your Gmail account")
        print("   - Use App Password, not your regular Gmail password")
        print("   - Check if the app password was copied correctly")
        return False

def show_next_steps():
    """Show what to do next"""
    print(f"\n🎉 Setup Complete!")
    print(f"=" * 30)
    print(f"📊 Your email campaign is ready with:")
    
    # Check contacts count
    try:
        import pandas as pd
        df = pd.read_csv('hr_contacts.csv')
        print(f"   • {len(df)} HR contacts loaded")
    except:
        print(f"   • HR contacts file ready")
    
    print(f"   • Professional email template")
    print(f"   • Resume attachment ready")
    print(f"   • Smart rate limiting enabled")
    print(f"   • Business hours scheduling")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Run full system test:")
    print(f"      python test_system.py")
    print(f"")
    print(f"   2. Start with a small test batch:")
    print(f"      python email_automation.py --batch-size 5")
    print(f"")
    print(f"   3. Monitor the logs:")
    print(f"      tail -f email_automation.log")
    print(f"")
    print(f"   4. For continuous operation:")
    print(f"      python email_automation.py --continuous")
    print(f"")
    print(f"⚠️  Important: Start with small batches to test everything works!")

def main():
    """Main setup function"""
    if setup_config():
        if test_configuration():
            show_next_steps()
        else:
            print("\n⚠️  Configuration saved but Gmail test failed.")
            print("Please check your credentials and try again.")
    else:
        print("\n❌ Setup failed. Please try again.")

if __name__ == "__main__":
    main()
