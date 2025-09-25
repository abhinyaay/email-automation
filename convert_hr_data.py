#!/usr/bin/env python3
"""
HR Data Converter
Helps convert HR contact data from various formats to the required CSV format
"""

import pandas as pd
import re
import json
from pathlib import Path

def extract_emails_from_text(text: str) -> list:
    """Extract email addresses from text using regex"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)

def extract_companies_from_text(text: str) -> list:
    """Extract potential company names from text"""
    # This is a basic implementation - you might need to adjust based on your data format
    lines = text.split('\n')
    companies = []
    
    for line in lines:
        line = line.strip()
        if line and not '@' in line and len(line) > 3:
            # Skip lines that look like headers or emails
            if not any(word in line.lower() for word in ['email', 'contact', 'phone', 'address']):
                companies.append(line)
    
    return companies

def manual_data_entry():
    """Interactive data entry for HR contacts"""
    contacts = []
    
    print("=== Manual HR Contact Entry ===")
    print("Enter HR contact details (press Enter with empty company name to finish):")
    
    while True:
        print(f"\n--- Contact {len(contacts) + 1} ---")
        company = input("Company name: ").strip()
        
        if not company:
            break
            
        hr_name = input("HR name (optional): ").strip() or "Hiring Manager"
        email = input("Email address: ").strip()
        position = input("Position (optional): ").strip() or "HR Representative"
        
        if email:
            contacts.append({
                'company': company,
                'hr_name': hr_name,
                'email': email,
                'position': position
            })
            print(f"✓ Added: {company} - {email}")
        else:
            print("⚠ Skipped (no email provided)")
    
    return contacts

def convert_excel_to_csv(excel_file: str, output_file: str = 'hr_contacts.csv'):
    """Convert Excel file to HR contacts CSV"""
    try:
        # Try to read Excel file
        df = pd.read_excel(excel_file)
        
        print(f"Excel file columns: {list(df.columns)}")
        print(f"First few rows:")
        print(df.head())
        
        # Try to map columns automatically
        column_mapping = {}
        
        for col in df.columns:
            col_lower = col.lower()
            if 'company' in col_lower or 'organization' in col_lower:
                column_mapping['company'] = col
            elif 'name' in col_lower and 'hr' in col_lower:
                column_mapping['hr_name'] = col
            elif 'email' in col_lower:
                column_mapping['email'] = col
            elif 'position' in col_lower or 'title' in col_lower or 'role' in col_lower:
                column_mapping['position'] = col
        
        print(f"\nAutomatic column mapping: {column_mapping}")
        
        # Allow manual column mapping
        print("\nColumn mapping (press Enter to keep automatic mapping):")
        for target_col in ['company', 'hr_name', 'email', 'position']:
            current = column_mapping.get(target_col, '')
            new_mapping = input(f"{target_col} -> {current} (new column name or Enter): ").strip()
            if new_mapping:
                column_mapping[target_col] = new_mapping
        
        # Create new DataFrame with mapped columns
        new_df = pd.DataFrame()
        
        for target_col, source_col in column_mapping.items():
            if source_col in df.columns:
                new_df[target_col] = df[source_col]
        
        # Fill missing required columns
        if 'company' not in new_df.columns:
            new_df['company'] = 'Unknown Company'
        if 'hr_name' not in new_df.columns:
            new_df['hr_name'] = 'Hiring Manager'
        if 'position' not in new_df.columns:
            new_df['position'] = 'HR Representative'
        
        # Remove rows without email
        if 'email' in new_df.columns:
            new_df = new_df.dropna(subset=['email'])
            new_df = new_df[new_df['email'].str.contains('@', na=False)]
        
        # Save to CSV
        new_df.to_csv(output_file, index=False)
        print(f"✓ Converted {len(new_df)} contacts to {output_file}")
        
        return new_df
        
    except Exception as e:
        print(f"Error converting Excel file: {e}")
        return None

def create_sample_data():
    """Create sample HR contacts for testing"""
    sample_contacts = [
        {
            'company': 'TechCorp Solutions',
            'hr_name': 'Sarah Johnson',
            'email': 'sarah.johnson@techcorp.com',
            'position': 'Senior HR Manager'
        },
        {
            'company': 'InnovateLabs',
            'hr_name': 'Mike Chen',
            'email': 'mike.chen@innovatelabs.com',
            'position': 'Talent Acquisition Lead'
        },
        {
            'company': 'DataDriven Inc',
            'hr_name': 'Emily Rodriguez',
            'email': 'emily.r@datadriven.com',
            'position': 'HR Business Partner'
        },
        {
            'company': 'CloudFirst Technologies',
            'hr_name': 'Hiring Manager',
            'email': 'careers@cloudfirst.com',
            'position': 'HR Representative'
        },
        {
            'company': 'StartupHub',
            'hr_name': 'Alex Kim',
            'email': 'alex@startuphub.io',
            'position': 'People Operations'
        }
    ]
    
    df = pd.DataFrame(sample_contacts)
    df.to_csv('hr_contacts_sample.csv', index=False)
    print(f"✓ Created sample data with {len(sample_contacts)} contacts in hr_contacts_sample.csv")
    return df

def main():
    print("=== HR Data Converter ===")
    print("Choose an option:")
    print("1. Convert Excel file to CSV")
    print("2. Manual data entry")
    print("3. Create sample data for testing")
    print("4. View existing HR contacts")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        excel_file = input("Enter Excel file path: ").strip()
        if Path(excel_file).exists():
            convert_excel_to_csv(excel_file)
        else:
            print(f"File not found: {excel_file}")
    
    elif choice == '2':
        contacts = manual_data_entry()
        if contacts:
            df = pd.DataFrame(contacts)
            df.to_csv('hr_contacts.csv', index=False)
            print(f"\n✓ Saved {len(contacts)} contacts to hr_contacts.csv")
    
    elif choice == '3':
        create_sample_data()
    
    elif choice == '4':
        csv_file = 'hr_contacts.csv'
        if Path(csv_file).exists():
            df = pd.read_csv(csv_file)
            print(f"\nCurrent HR contacts ({len(df)} entries):")
            print(df.to_string(index=False))
        else:
            print(f"No HR contacts file found: {csv_file}")
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
