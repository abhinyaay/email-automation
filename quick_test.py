#!/usr/bin/env python3
"""
Quick test script to verify Gmail connection
"""

import json
import smtplib
import ssl

def test_gmail_connection():
    """Test Gmail SMTP connection"""
    try:
        # Load config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        email = config['email']
        password = config['password']
        
        # Check if credentials are still default
        if email == 'your_email@gmail.com' or password == 'your_app_password':
            print("❌ Please update config.json with your actual Gmail credentials")
            print("   Edit the file and replace:")
            print('   "email": "your_email@gmail.com"')
            print('   "password": "your_app_password"')
            print('   "phone_number": "+91-XXXXXXXXXX"')
            return False
        
        print(f"📧 Testing connection for: {email}")
        
        # Test SMTP connection
        context = ssl.create_default_context()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls(context=context)
        server.login(email, password)
        server.quit()
        
        print("✅ Gmail connection successful!")
        print(f"🎉 You're ready to send emails!")
        
        # Show summary
        print(f"\n📊 Campaign Summary:")
        try:
            import pandas as pd
            df = pd.read_csv('hr_contacts.csv')
            print(f"   • {len(df)} HR contacts ready")
        except:
            print(f"   • HR contacts file ready")
        
        print(f"   • Daily limit: {config['daily_limit']} emails")
        print(f"   • Business hours: {config['business_hours_start']}:00-{config['business_hours_end']}:00")
        print(f"   • Delay between emails: {config['min_delay']}-{config['max_delay']} seconds")
        
        print(f"\n🚀 Ready to start! Run:")
        print(f"   python email_automation.py --batch-size 5")
        
        return True
        
    except FileNotFoundError:
        print("❌ config.json not found")
        return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON in config.json")
        return False
    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail authentication failed")
        print("💡 Check:")
        print("   • 2FA is enabled on Gmail")
        print("   • Using App Password (not regular password)")
        print("   • App password copied correctly (16 characters)")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Quick Gmail Connection Test")
    print("=" * 40)
    test_gmail_connection()
