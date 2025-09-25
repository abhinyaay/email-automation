#!/usr/bin/env python3
"""
Test the email template with sample data
"""

import json

def test_email_template():
    """Test the email template with sample data"""
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Load template
    with open('email_template.html', 'r') as f:
        template = f.read()
    
    # Sample HR contact data
    sample_contact = {
        'company': 'TechCorp Solutions',
        'hr_name': 'Sarah Johnson',
        'email': 'sarah.johnson@techcorp.com',
        'position': 'HR Manager'
    }
    
    # Personalize template
    personalized_content = template.format(
        company_name=sample_contact['company'],
        hr_name=sample_contact['hr_name'],
        candidate_name=config['candidate_name'],
        phone_number=config['phone_number'],
        email_address=config['email']
    )
    
    subject = f"Application for Developer Role – {config['candidate_name']}"
    
    print("📧 Email Template Test")
    print("=" * 50)
    print(f"Subject: {subject}")
    print("\nTo: sarah.johnson@techcorp.com")
    print("From: abhinyaay@gmail.com")
    print("\n" + "=" * 50)
    print("EMAIL CONTENT:")
    print("=" * 50)
    
    # Convert HTML to readable text for preview
    import re
    text_content = re.sub('<[^<]+?>', '', personalized_content)
    text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
    text_content = text_content.strip()
    
    print(text_content)
    
    print("\n" + "=" * 50)
    print("✅ Template test completed!")
    print("📎 Resume attachment: Abhinay-Kumar.pdf")
    print("\n💡 The actual email will be sent in HTML format with proper formatting.")

if __name__ == "__main__":
    test_email_template()
