#!/usr/bin/env python3
"""
Automatic PDF to CSV Converter for Structured HR Lists
Processes structured HR data without manual intervention
"""

import re
import pandas as pd
import pdfplumber
from pathlib import Path

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using pdfplumber"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def parse_structured_hr_data(text: str) -> list:
    """
    Parse structured HR data with columns: SNo, Name, Email, Title, Company
    """
    contacts = []
    lines = text.split('\n')
    
    # Skip header line
    data_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('SNo') and not line.startswith('Name'):
            data_lines.append(line)
    
    print(f"Processing {len(data_lines)} data lines...")
    
    for line_num, line in enumerate(data_lines, 1):
        # Extract email first (most reliable identifier)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, line, re.IGNORECASE)
        
        if emails:
            email = emails[0]
            
            # Remove the email from the line to parse other fields
            line_without_email = line.replace(email, '|EMAIL|')
            
            # Split the line and try to identify components
            parts = [part.strip() for part in line_without_email.split() if part.strip()]
            
            # Try to extract structured data
            sno = ""
            name = ""
            title = ""
            company = ""
            
            # Look for number at the beginning (SNo)
            if parts and parts[0].isdigit():
                sno = parts[0]
                parts = parts[1:]  # Remove SNo from parts
            
            # Find the email marker position to split before and after
            email_pos = -1
            for i, part in enumerate(parts):
                if part == '|EMAIL|':
                    email_pos = i
                    break
            
            if email_pos > 0:
                # Everything before email should be name + title
                before_email = parts[:email_pos]
                after_email = parts[email_pos+1:] if email_pos < len(parts)-1 else []
                
                # The company is usually after the email
                company = ' '.join(after_email) if after_email else "Unknown Company"
                
                # Name is usually the first 2-3 words before email
                if len(before_email) >= 2:
                    # Take first 2 words as name, rest as title
                    name = ' '.join(before_email[:2])
                    title = ' '.join(before_email[2:]) if len(before_email) > 2 else "HR Representative"
                elif len(before_email) == 1:
                    name = before_email[0]
                    title = "HR Representative"
                else:
                    name = "HR Manager"
                    title = "HR Representative"
            else:
                # Fallback parsing
                name = "HR Manager"
                title = "HR Representative"
                company = "Unknown Company"
            
            # Clean up the extracted data
            name = re.sub(r'^\d+\s*', '', name).strip()  # Remove leading numbers
            company = re.sub(r'^\d+\s*', '', company).strip()  # Remove leading numbers
            
            # Skip if email looks invalid
            if '@' in email and '.' in email.split('@')[1]:
                contact = {
                    'company': company if company != "Unknown Company" else f"Company_{line_num}",
                    'hr_name': name if name else "HR Manager",
                    'email': email,
                    'position': title if title else "HR Representative"
                }
                contacts.append(contact)
                
                if line_num <= 5:  # Show first 5 for verification
                    print(f"✓ Parsed: {contact['company']} | {contact['hr_name']} | {contact['email']}")
    
    return contacts

def save_contacts_to_csv(contacts: list, filename: str = 'hr_contacts.csv'):
    """Save contacts to CSV file"""
    if not contacts:
        print("❌ No contacts found to save!")
        return False
    
    # Remove duplicates based on email
    seen_emails = set()
    unique_contacts = []
    
    for contact in contacts:
        if contact['email'].lower() not in seen_emails:
            seen_emails.add(contact['email'].lower())
            unique_contacts.append(contact)
    
    df = pd.DataFrame(unique_contacts)
    df.to_csv(filename, index=False)
    
    print(f"✅ Saved {len(unique_contacts)} unique contacts to {filename}")
    print(f"   (Removed {len(contacts) - len(unique_contacts)} duplicates)")
    
    return True

def main():
    """Main conversion function"""
    pdf_file = "Company Wise HR Contacts - HR Contacts.pdf"
    
    print("=== Automatic PDF to CSV Converter ===")
    print(f"📄 Processing: {pdf_file}")
    
    # Check if file exists
    if not Path(pdf_file).exists():
        print(f"❌ File not found: {pdf_file}")
        return
    
    # Extract text
    print("🔍 Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_file)
    
    if not text.strip():
        print("❌ Could not extract text from PDF")
        return
    
    print(f"✅ Extracted {len(text):,} characters")
    
    # Show sample
    print("\n📋 Sample extracted text:")
    print("-" * 60)
    sample_lines = text.split('\n')[:10]
    for line in sample_lines:
        if line.strip():
            print(line.strip())
    print("-" * 60)
    
    # Parse contacts
    print("\n🔍 Parsing HR contacts...")
    contacts = parse_structured_hr_data(text)
    
    if not contacts:
        print("❌ No contacts found in the PDF")
        return
    
    print(f"✅ Found {len(contacts)} contacts")
    
    # Save to CSV
    print(f"\n💾 Saving to CSV...")
    if save_contacts_to_csv(contacts, 'hr_contacts.csv'):
        print(f"\n🎉 Conversion completed successfully!")
        
        # Show summary
        df = pd.read_csv('hr_contacts.csv')
        print(f"\n📊 Summary:")
        print(f"   Total contacts: {len(df)}")
        print(f"   Unique companies: {df['company'].nunique()}")
        print(f"   Sample entries:")
        print(df.head(3).to_string(index=False))
        
        print(f"\n✅ Next steps:")
        print(f"   1. Review the file: hr_contacts.csv")
        print(f"   2. Test the system: python test_system.py")
        print(f"   3. Update config.json with your Gmail credentials")
        print(f"   4. Start sending: python email_automation.py --batch-size 5")

if __name__ == "__main__":
    main()
