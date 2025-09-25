#!/usr/bin/env python3
"""
Test script for HR Email Automation System
Validates configuration and tests email functionality without sending actual emails
"""

import json
import os
import pandas as pd
from pathlib import Path
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def test_configuration():
    """Test if configuration file is properly set up"""
    print("=== Testing Configuration ===")
    
    config_file = 'config.json'
    if not os.path.exists(config_file):
        print("❌ config.json not found")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        required_fields = ['email', 'password', 'candidate_name']
        missing_fields = []
        
        for field in required_fields:
            if not config.get(field) or config[field] == f"your_{field}@gmail.com" or "XXXX" in str(config[field]):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Please update these fields in config.json: {missing_fields}")
            return False
        
        print("✅ Configuration file is properly set up")
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in config.json")
        return False
    except Exception as e:
        print(f"❌ Error reading config.json: {e}")
        return False

def test_hr_contacts():
    """Test if HR contacts file is properly formatted"""
    print("\n=== Testing HR Contacts ===")
    
    contacts_file = 'hr_contacts.csv'
    if not os.path.exists(contacts_file):
        print("❌ hr_contacts.csv not found")
        print("💡 Run: python convert_hr_data.py to create it")
        return False
    
    try:
        df = pd.read_csv(contacts_file)
        
        if df.empty:
            print("❌ HR contacts file is empty")
            return False
        
        # Check required columns
        if 'email' not in df.columns:
            print("❌ 'email' column not found in HR contacts")
            return False
        
        # Check for valid emails
        valid_emails = df['email'].str.contains('@', na=False).sum()
        
        print(f"✅ Found {len(df)} contacts with {valid_emails} valid emails")
        
        # Show sample
        print(f"Sample contacts:")
        print(df.head(3).to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading HR contacts: {e}")
        return False

def test_resume_file():
    """Test if resume file exists"""
    print("\n=== Testing Resume File ===")
    
    resume_file = 'Abhinay-Kumar.pdf'
    if not os.path.exists(resume_file):
        print(f"❌ Resume file not found: {resume_file}")
        print("💡 Place your resume PDF in the current directory")
        return False
    
    file_size = os.path.getsize(resume_file) / (1024 * 1024)  # MB
    print(f"✅ Resume file found: {resume_file} ({file_size:.1f} MB)")
    
    if file_size > 5:
        print("⚠ Warning: Resume file is quite large (>5MB). Consider compressing it.")
    
    return True

def test_email_template():
    """Test if email template exists and is valid"""
    print("\n=== Testing Email Template ===")
    
    template_file = 'email_template.html'
    if not os.path.exists(template_file):
        print(f"❌ Email template not found: {template_file}")
        return False
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Check for required placeholders
        required_placeholders = ['{company_name}', '{hr_name}', '{candidate_name}']
        missing_placeholders = []
        
        for placeholder in required_placeholders:
            if placeholder not in template:
                missing_placeholders.append(placeholder)
        
        if missing_placeholders:
            print(f"❌ Missing placeholders in template: {missing_placeholders}")
            return False
        
        print(f"✅ Email template is valid ({len(template)} characters)")
        return True
        
    except Exception as e:
        print(f"❌ Error reading email template: {e}")
        return False

def test_smtp_connection():
    """Test SMTP connection without sending emails"""
    print("\n=== Testing SMTP Connection ===")
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("Attempting to connect to Gmail SMTP...")
        
        context = ssl.create_default_context()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls(context=context)
        server.login(config['email'], config['password'])
        server.quit()
        
        print("✅ SMTP connection successful")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP Authentication failed")
        print("💡 Check your email and app password in config.json")
        print("💡 Make sure 2FA is enabled and you're using an app password")
        return False
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        return False

def test_dependencies():
    """Test if all required dependencies are installed"""
    print("\n=== Testing Dependencies ===")
    
    required_packages = [
        'pandas',
        'schedule',
        'holidays'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {missing_packages}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def run_dry_run():
    """Run a dry run of the email system"""
    print("\n=== Running Dry Run ===")
    
    try:
        from email_automation import EmailAutomationSystem
        
        # Initialize system
        email_system = EmailAutomationSystem()
        
        # Load contacts and template
        contacts_df = email_system.load_hr_contacts()
        template = email_system.load_email_template()
        
        if contacts_df.empty:
            print("❌ No contacts loaded")
            return False
        
        # Test personalization with first contact
        first_contact = contacts_df.iloc[0].to_dict()
        subject, personalized_content = email_system.personalize_email(template, first_contact)
        
        print(f"✅ Email personalization test successful")
        print(f"Sample subject: {subject}")
        print(f"Sample content length: {len(personalized_content)} characters")
        
        # Test timing
        is_business_hours = email_system.is_business_hours()
        print(f"✅ Business hours check: {'Yes' if is_business_hours else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dry run failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 HR Email Automation System - Test Suite")
    print("=" * 50)
    
    tests = [
        test_dependencies,
        test_configuration,
        test_hr_contacts,
        test_resume_file,
        test_email_template,
        test_smtp_connection,
        run_dry_run
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your system is ready to use.")
        print("\nNext steps:")
        print("1. Review your configuration one more time")
        print("2. Start with a small batch: python email_automation.py --batch-size 5")
        print("3. Monitor the logs: tail -f email_automation.log")
    else:
        print("⚠ Some tests failed. Please fix the issues above before running the system.")
        print("\nCommon fixes:")
        print("- Update config.json with your Gmail credentials")
        print("- Create hr_contacts.csv with your HR contacts")
        print("- Ensure your resume PDF is in the directory")
        print("- Install missing dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
