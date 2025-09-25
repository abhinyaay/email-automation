#!/usr/bin/env python3
"""
PDF to CSV Converter for HR Contacts
Extracts HR contact information from PDF files and converts to CSV format
"""

import re
import pandas as pd
import sys
from pathlib import Path

def extract_text_from_pdf_simple(pdf_path: str) -> str:
    """
    Extract text from PDF using PyPDF2 (fallback method)
    """
    try:
        import PyPDF2
        
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        return text
    except ImportError:
        print("PyPDF2 not installed. Install with: pip install PyPDF2")
        return ""
    except Exception as e:
        print(f"Error extracting text with PyPDF2: {e}")
        return ""

def extract_text_from_pdf_advanced(pdf_path: str) -> str:
    """
    Extract text from PDF using pdfplumber (preferred method)
    """
    try:
        import pdfplumber
        
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text
    except ImportError:
        print("pdfplumber not installed. Install with: pip install pdfplumber")
        return ""
    except Exception as e:
        print(f"Error extracting text with pdfplumber: {e}")
        return ""

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF using the best available method
    """
    # Try advanced method first
    text = extract_text_from_pdf_advanced(pdf_path)
    
    # Fallback to simple method
    if not text.strip():
        text = extract_text_from_pdf_simple(pdf_path)
    
    return text

def extract_emails_from_text(text: str) -> list:
    """Extract email addresses from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    return list(set(emails))  # Remove duplicates

def extract_companies_and_contacts(text: str) -> list:
    """
    Extract company names and contact information from text
    This function tries to parse common HR list formats
    """
    contacts = []
    lines = text.split('\n')
    
    # Common patterns for HR lists
    current_company = ""
    current_hr_name = ""
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Look for email addresses
        emails = extract_emails_from_text(line)
        
        if emails:
            email = emails[0]  # Take the first email found
            
            # Try to find company name in previous lines
            company = current_company
            hr_name = current_hr_name
            
            # Look back for company name
            for j in range(max(0, i-5), i):
                prev_line = lines[j].strip()
                if prev_line and not '@' in prev_line:
                    # Check if it looks like a company name
                    if any(keyword in prev_line.lower() for keyword in ['ltd', 'inc', 'corp', 'company', 'solutions', 'technologies', 'systems', 'services']):
                        company = prev_line
                        break
                    elif len(prev_line.split()) <= 4 and len(prev_line) > 10:  # Likely company name
                        company = prev_line
            
            # Look for HR name (usually appears near email)
            for j in range(max(0, i-3), min(len(lines), i+3)):
                check_line = lines[j].strip()
                if check_line and check_line != line and not '@' in check_line:
                    # Check if it looks like a person's name (2-3 words, proper case)
                    words = check_line.split()
                    if 2 <= len(words) <= 3 and all(word[0].isupper() for word in words if word):
                        hr_name = check_line
                        break
            
            # Default values if not found
            if not company:
                company = "Unknown Company"
            if not hr_name:
                hr_name = "Hiring Manager"
            
            contacts.append({
                'company': company,
                'hr_name': hr_name,
                'email': email,
                'position': 'HR Representative'
            })
            
            current_company = company
            current_hr_name = hr_name
    
    return contacts

def manual_review_and_edit(contacts: list) -> list:
    """
    Allow manual review and editing of extracted contacts
    """
    print(f"\n=== Review Extracted Contacts ({len(contacts)} found) ===")
    print("Review each contact and edit if needed (press Enter to keep, type new value to change)")
    
    reviewed_contacts = []
    
    for i, contact in enumerate(contacts):
        print(f"\n--- Contact {i+1} ---")
        print(f"Company: {contact['company']}")
        print(f"HR Name: {contact['hr_name']}")
        print(f"Email: {contact['email']}")
        print(f"Position: {contact['position']}")
        
        # Ask for confirmation or edits
        action = input("\nKeep this contact? (y/n/e for edit): ").lower().strip()
        
        if action == 'n':
            print("Skipping this contact...")
            continue
        elif action == 'e':
            # Edit mode
            new_company = input(f"Company [{contact['company']}]: ").strip()
            if new_company:
                contact['company'] = new_company
            
            new_hr_name = input(f"HR Name [{contact['hr_name']}]: ").strip()
            if new_hr_name:
                contact['hr_name'] = new_hr_name
            
            new_email = input(f"Email [{contact['email']}]: ").strip()
            if new_email:
                contact['email'] = new_email
            
            new_position = input(f"Position [{contact['position']}]: ").strip()
            if new_position:
                contact['position'] = new_position
        
        reviewed_contacts.append(contact)
        print("✓ Contact added")
    
    return reviewed_contacts

def save_to_csv(contacts: list, filename: str = 'hr_contacts.csv'):
    """Save contacts to CSV file"""
    if not contacts:
        print("No contacts to save!")
        return False
    
    df = pd.DataFrame(contacts)
    df.to_csv(filename, index=False)
    print(f"✅ Saved {len(contacts)} contacts to {filename}")
    return True

def install_pdf_dependencies():
    """Install required PDF processing libraries"""
    print("Installing PDF processing dependencies...")
    import subprocess
    import sys
    
    try:
        # Install pdfplumber (preferred)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"])
        print("✅ Installed pdfplumber")
    except:
        try:
            # Fallback to PyPDF2
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
            print("✅ Installed PyPDF2")
        except Exception as e:
            print(f"❌ Failed to install PDF libraries: {e}")
            return False
    
    return True

def main():
    """Main function"""
    print("=== PDF to CSV Converter for HR Contacts ===")
    
    # Check if PDF file is provided
    if len(sys.argv) < 2:
        pdf_file = input("Enter the path to your PDF file: ").strip()
    else:
        pdf_file = sys.argv[1]
    
    # Check if file exists
    if not Path(pdf_file).exists():
        print(f"❌ File not found: {pdf_file}")
        return
    
    # Check for PDF dependencies
    try:
        import pdfplumber
    except ImportError:
        try:
            import PyPDF2
        except ImportError:
            print("❌ PDF processing libraries not found.")
            install_deps = input("Install them now? (y/n): ").lower().strip()
            if install_deps == 'y':
                if not install_pdf_dependencies():
                    return
            else:
                print("Cannot proceed without PDF processing libraries.")
                return
    
    print(f"📄 Processing PDF file: {pdf_file}")
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_file)
    
    if not text.strip():
        print("❌ Could not extract text from PDF. The file might be:")
        print("   - Image-based (scanned) - try OCR tools")
        print("   - Password protected")
        print("   - Corrupted")
        return
    
    print(f"✅ Extracted {len(text)} characters of text")
    
    # Show sample text for verification
    print(f"\nSample extracted text (first 500 characters):")
    print("-" * 50)
    print(text[:500] + "..." if len(text) > 500 else text)
    print("-" * 50)
    
    # Ask if text looks correct
    proceed = input("\nDoes the extracted text look correct? (y/n): ").lower().strip()
    if proceed != 'y':
        print("Try a different PDF processing method or check your PDF file.")
        return
    
    # Extract contacts
    print("\n🔍 Extracting contact information...")
    contacts = extract_companies_and_contacts(text)
    
    if not contacts:
        print("❌ No email addresses found in the PDF.")
        print("💡 Make sure your PDF contains email addresses in text format.")
        
        # Offer manual entry
        manual = input("Would you like to enter contacts manually? (y/n): ").lower().strip()
        if manual == 'y':
            from convert_hr_data import manual_data_entry
            contacts = manual_data_entry()
    else:
        print(f"✅ Found {len(contacts)} potential contacts")
        
        # Show preview
        print("\nPreview of extracted contacts:")
        for i, contact in enumerate(contacts[:3]):
            print(f"{i+1}. {contact['company']} - {contact['hr_name']} - {contact['email']}")
        if len(contacts) > 3:
            print(f"... and {len(contacts) - 3} more")
        
        # Ask for manual review
        review = input("\nWould you like to review and edit the contacts? (y/n): ").lower().strip()
        if review == 'y':
            contacts = manual_review_and_edit(contacts)
    
    # Save to CSV
    if contacts:
        output_file = input(f"\nOutput filename [hr_contacts.csv]: ").strip()
        if not output_file:
            output_file = 'hr_contacts.csv'
        
        save_to_csv(contacts, output_file)
        
        print(f"\n🎉 Conversion complete!")
        print(f"📁 File saved: {output_file}")
        print(f"📊 Total contacts: {len(contacts)}")
        print(f"\nNext steps:")
        print(f"1. Review the CSV file: {output_file}")
        print(f"2. Run tests: python test_system.py")
        print(f"3. Start email automation: python email_automation.py --batch-size 5")
    else:
        print("❌ No contacts to save.")

if __name__ == "__main__":
    main()
