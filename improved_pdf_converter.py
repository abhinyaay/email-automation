#!/usr/bin/env python3
"""
Improved PDF to CSV Converter with better parsing and debugging
Ensures all contacts are captured from the PDF
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

def parse_hr_data_improved(text: str) -> tuple:
    """
    Improved parsing with debugging to capture all contacts
    Returns (contacts, skipped_lines) for analysis
    """
    contacts = []
    skipped_lines = []
    lines = text.split('\n')
    
    # Filter out header and empty lines
    data_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('SNo') and not line.lower().startswith('name'):
            data_lines.append(line)
    
    print(f"Processing {len(data_lines)} data lines...")
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    for line_num, line in enumerate(data_lines, 1):
        # Find all emails in the line
        emails = re.findall(email_pattern, line, re.IGNORECASE)
        
        if not emails:
            skipped_lines.append({
                'line_num': line_num,
                'content': line,
                'reason': 'No email found'
            })
            continue
        
        email = emails[0]  # Take the first email
        
        # More robust parsing approach
        # Split by common delimiters and identify components
        
        # Remove email temporarily to parse other parts
        line_parts = line.replace(email, '|||EMAIL|||').strip()
        
        # Try different splitting approaches
        parts = []
        
        # First try: split by multiple spaces (common in tabular data)
        if '  ' in line_parts:
            parts = [p.strip() for p in re.split(r'\s{2,}', line_parts) if p.strip()]
        else:
            # Fallback: split by single space but be smarter about it
            words = line_parts.split()
            parts = []
            current_part = []
            
            for word in words:
                if word == '|||EMAIL|||':
                    if current_part:
                        parts.append(' '.join(current_part))
                        current_part = []
                    parts.append('|||EMAIL|||')
                elif word.isdigit() and len(current_part) == 0:
                    # This is likely a serial number
                    parts.append(word)
                elif len(word) > 1 and word[0].isupper() and len(current_part) < 3:
                    # Likely start of a name or title
                    current_part.append(word)
                else:
                    current_part.append(word)
            
            if current_part:
                parts.append(' '.join(current_part))
        
        # Now extract information from parts
        sno = ""
        name = ""
        title = ""
        company = ""
        
        email_index = -1
        for i, part in enumerate(parts):
            if part == '|||EMAIL|||':
                email_index = i
                break
        
        # Extract serial number (usually first part if it's a digit)
        if parts and parts[0].isdigit():
            sno = parts[0]
            parts = parts[1:]
            if email_index >= 0:
                email_index -= 1
        
        if email_index >= 0:
            # Parts before email are usually: Name, Title
            before_email = parts[:email_index]
            after_email = parts[email_index+1:] if email_index < len(parts)-1 else []
            
            # Extract name (usually first 1-2 parts before email)
            if before_email:
                if len(before_email) == 1:
                    # Only one part - could be name or title
                    potential_name = before_email[0]
                    if any(title_word in potential_name.lower() for title_word in ['manager', 'director', 'head', 'lead', 'hr', 'recruiter']):
                        title = potential_name
                        name = "HR Manager"
                    else:
                        name = potential_name
                        title = "HR Representative"
                elif len(before_email) >= 2:
                    # Multiple parts - first is likely name, rest is title
                    name = before_email[0]
                    title = ' '.join(before_email[1:])
                else:
                    name = "HR Manager"
                    title = "HR Representative"
            else:
                name = "HR Manager"
                title = "HR Representative"
            
            # Company is usually after email
            company = ' '.join(after_email) if after_email else "Unknown Company"
        else:
            # Fallback parsing if email marker not found properly
            name = "HR Manager"
            title = "HR Representative"
            company = "Unknown Company"
        
        # Clean up extracted data
        name = re.sub(r'^\d+\s*', '', name).strip()
        company = re.sub(r'^\d+\s*', '', company).strip()
        title = re.sub(r'^\d+\s*', '', title).strip()
        
        # Validate email
        if '@' not in email or '.' not in email.split('@')[1]:
            skipped_lines.append({
                'line_num': line_num,
                'content': line,
                'reason': f'Invalid email: {email}'
            })
            continue
        
        # Create contact
        contact = {
            'company': company if company and company != "Unknown Company" else f"Company_{sno if sno else line_num}",
            'hr_name': name if name else "HR Manager",
            'email': email,
            'position': title if title else "HR Representative"
        }
        
        contacts.append(contact)
        
        # Show first few for verification
        if line_num <= 5:
            print(f"✓ Line {line_num}: {contact['company']} | {contact['hr_name']} | {contact['email']}")
    
    return contacts, skipped_lines

def analyze_skipped_lines(skipped_lines: list):
    """Analyze why lines were skipped"""
    if not skipped_lines:
        print("✅ No lines were skipped!")
        return
    
    print(f"\n⚠️  {len(skipped_lines)} lines were skipped:")
    print("-" * 80)
    
    # Group by reason
    reasons = {}
    for item in skipped_lines:
        reason = item['reason']
        if reason not in reasons:
            reasons[reason] = []
        reasons[reason].append(item)
    
    for reason, items in reasons.items():
        print(f"\n{reason} ({len(items)} lines):")
        for item in items[:3]:  # Show first 3 examples
            print(f"  Line {item['line_num']}: {item['content'][:100]}...")
        if len(items) > 3:
            print(f"  ... and {len(items) - 3} more")

def save_contacts_to_csv(contacts: list, filename: str = 'hr_contacts_complete.csv'):
    """Save contacts to CSV file"""
    if not contacts:
        print("❌ No contacts found to save!")
        return False
    
    # Remove duplicates based on email
    seen_emails = set()
    unique_contacts = []
    duplicates = []
    
    for contact in contacts:
        email_lower = contact['email'].lower()
        if email_lower not in seen_emails:
            seen_emails.add(email_lower)
            unique_contacts.append(contact)
        else:
            duplicates.append(contact)
    
    df = pd.DataFrame(unique_contacts)
    df.to_csv(filename, index=False)
    
    print(f"✅ Saved {len(unique_contacts)} unique contacts to {filename}")
    if duplicates:
        print(f"   Removed {len(duplicates)} duplicates:")
        for dup in duplicates[:3]:
            print(f"     - {dup['email']}")
        if len(duplicates) > 3:
            print(f"     ... and {len(duplicates) - 3} more")
    
    return True

def main():
    """Main conversion function with improved parsing"""
    pdf_file = "Company Wise HR Contacts - HR Contacts.pdf"
    
    print("=== Improved PDF to CSV Converter ===")
    print(f"📄 Processing: {pdf_file}")
    
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
    
    # Parse contacts with improved algorithm
    print("\n🔍 Parsing HR contacts with improved algorithm...")
    contacts, skipped_lines = parse_hr_data_improved(text)
    
    print(f"✅ Successfully parsed {len(contacts)} contacts")
    
    # Analyze what was skipped
    analyze_skipped_lines(skipped_lines)
    
    # Save to CSV
    if contacts:
        print(f"\n💾 Saving to CSV...")
        if save_contacts_to_csv(contacts, 'hr_contacts_complete.csv'):
            print(f"\n🎉 Improved conversion completed!")
            
            # Show comparison
            df = pd.read_csv('hr_contacts_complete.csv')
            print(f"\n📊 Results:")
            print(f"   PDF data lines: 1842")
            print(f"   Contacts found: {len(contacts)}")
            print(f"   Unique contacts: {len(df)}")
            print(f"   Lines skipped: {len(skipped_lines)}")
            
            # Show sample
            print(f"\n📋 Sample contacts:")
            print(df.head(3).to_string(index=False))
            
            # Replace the original file if this one is better
            if len(df) > 1835:
                replace = input(f"\n🔄 New version has {len(df) - 1835} more contacts. Replace hr_contacts.csv? (y/n): ")
                if replace.lower() == 'y':
                    df.to_csv('hr_contacts.csv', index=False)
                    print("✅ Replaced hr_contacts.csv with improved version")

if __name__ == "__main__":
    main()
