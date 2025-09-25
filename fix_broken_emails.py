#!/usr/bin/env python3
"""
Fix broken emails from PDF parsing
Manual correction for the 7 corrupted email addresses
"""

import pandas as pd
import re

def fix_broken_emails():
    """Fix the 7 broken email addresses manually"""
    
    # Load the current CSV
    df = pd.read_csv('hr_contacts.csv')
    print(f"Current contacts: {len(df)}")
    
    # Manual fixes for the broken emails based on pattern analysis
    broken_contacts = [
        {
            'company': 'Excelencia Consulting',
            'hr_name': 'Gitanjali Venkatesh',
            'email': 'gitanjali.venkatesh@excelenciaconsulting.com',  # Fixed
            'position': 'Head of Talent Acquisition'
        },
        {
            'company': 'World Fashion Exchange',
            'hr_name': 'Jasmine Vaswani',
            'email': 'jasmine.vaswani@worldfashionexchange.com',  # Fixed
            'position': 'Chief Human Resources Officer (CHRO)'
        },
        {
            'company': 'Barry-Wehmiller Design Group',
            'hr_name': 'Lakshmi Radhakrishnan',
            'email': 'lakshmipriya.radhakrishnan@bwdesigngroup.com',  # Fixed
            'position': 'Director - HR'
        },
        # Note: Only showing first 3 - would need to manually analyze the PDF 
        # for the other 4 broken emails to reconstruct them properly
    ]
    
    # Add the fixed contacts
    for contact in broken_contacts:
        # Check if email already exists
        if not df[df['email'] == contact['email']].empty:
            print(f"⚠️  Email already exists: {contact['email']}")
            continue
            
        # Add to dataframe
        new_row = pd.DataFrame([contact])
        df = pd.concat([df, new_row], ignore_index=True)
        print(f"✅ Added: {contact['hr_name']} - {contact['email']}")
    
    # Save updated CSV
    df.to_csv('hr_contacts_fixed.csv', index=False)
    print(f"\n📊 Updated contacts: {len(df)}")
    print(f"💾 Saved to: hr_contacts_fixed.csv")
    
    return df

def extract_broken_emails_from_text():
    """
    Extract the exact broken lines from PDF to manually fix them
    """
    import pdfplumber
    
    print("=== Extracting Broken Email Lines ===")
    
    with pdfplumber.open("Company Wise HR Contacts - HR Contacts.pdf") as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    lines = text.split('\n')
    broken_lines = []
    
    # Find lines that contain partial emails or broken formatting
    for i, line in enumerate(lines):
        line = line.strip()
        if line and ('@ ' in line or ' @' in line or '.c om' in line or '. com' in line):
            broken_lines.append({
                'line_num': i,
                'content': line
            })
    
    print(f"Found {len(broken_lines)} potentially broken lines:")
    for item in broken_lines:
        print(f"Line {item['line_num']}: {item['content']}")
    
    return broken_lines

def main():
    """Main function"""
    print("=== Email Fixer ===")
    
    choice = input("1. Fix known broken emails\n2. Extract all broken lines for manual review\nChoice (1/2): ")
    
    if choice == '1':
        df = fix_broken_emails()
        
        # Ask if user wants to replace the main file
        replace = input(f"\nReplace hr_contacts.csv with fixed version? (y/n): ")
        if replace.lower() == 'y':
            df.to_csv('hr_contacts.csv', index=False)
            print("✅ Updated hr_contacts.csv")
    
    elif choice == '2':
        extract_broken_emails_from_text()
        print("\n💡 Review the broken lines above and manually add the correct emails to hr_contacts.csv")
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
