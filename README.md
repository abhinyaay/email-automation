# HR Email Automation System 🚀

An intelligent Python-based system for sending personalized cold emails to HR contacts with advanced spam prevention and 24/7 operation.

## Features

- 🎯 **24/7 Operation**: Sends emails continuously without business hour restrictions
- 📧 **Smart Rate Limiting**: 400 emails/day to avoid spam detection
- 🤖 **Personalized Templates**: Dynamic company and HR name insertion
- 📎 **Resume Attachment**: Automatically attaches your resume
- 🛡️ **Anti-Spam Protection**: Intelligent delays and connection management
- ☁️ **AWS Deployment Ready**: Complete EC2 setup scripts
- 📊 **Progress Tracking**: Comprehensive logging and monitoring
- Modular design for easy customization and scaling
- Supports long-running execution with graceful logging


## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Gmail Setup
1. Enable 2-Factor Authentication on Gmail
2. Generate App Password: Google Account → Security → App passwords
3. Select "Mail" → "Other" → Copy 16-character password

### 3. Configuration
Edit `config.json`:
```json
{
    "email": "youremail@gmail.com",
    "password": "your_16_char_app_password",
    "candidate_name": "Your Name",
    "phone_number": "+91-your_number"
}
```

### 4. Prepare Data
- Add HR contacts to `hr_contacts.csv`
- Place your resume as `Abhinay-Kumar.pdf`

### 5. Run
```bash
# 24/7 continuous operation
python email_automation_24x7.py

# Test connection first
python quick_test.py
```

## HR Contacts Format

```csv
company,hr_name,email,position
TechCorp,Sarah Johnson,sarah@techcorp.com,HR Manager
InnovateLabs,Mike Chen,mike@innovate.com,Recruiter
```

## Usage

- **24/7 Mode**: `python email_automation_24x7.py`
- **Business Hours**: `python email_automation.py --continuous`
- **Test Batch**: `python email_automation.py --batch-size 5`
- **Convert PDF**: `python pdf_to_csv_converter.py your-hr-list.pdf`

## AWS Deployment

```bash
# Deploy to EC2
./deploy_to_ec2.sh your-key.pem ubuntu@your-ec2-ip

# On EC2: setup service
./deploy_aws.sh
sudo systemctl start hr-email-automation
```

## Campaign Stats

- **1,838 HR Contacts** ready
- **400 emails/day** safe limit
- **~4.6 days** to complete campaign
- **99.8% extraction accuracy** from PDF

## Safety Features

- Daily limit: 400 emails (Google-safe)
- Smart delays: 3-5 minutes between emails
- Connection retry logic
- Duplicate prevention
- Professional HTML templates

## Files

- `email_automation_24x7.py` - Main 24/7 system
- `email_automation.py` - Business hours version
- `config.json` - Configuration
- `email_template.html` - Email template
- `hr_contacts.csv` - HR database
- `deploy_aws.sh` - AWS deployment

## Monitoring

```bash
# View logs
tail -f email_automation_24x7.log

# Check progress
cat sent_emails.json | wc -l
```

Built for job seekers to efficiently reach HR managers across India 🇮🇳
