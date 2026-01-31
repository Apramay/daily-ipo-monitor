#!/usr/bin/env python3
"""
Daily IPO Monitor Script
"""

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

load_dotenv()


# Finnhub API Configuration
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")  
# Email Configuration
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"  # Gmail: smtp.gmail.com | Outlook: smtp-mail.outlook.com
SMTP_PORT = 587  

# IPO Filter Configuration
MIN_OFFER_AMOUNT = 200_000_000  # Minimum offer amount in USD (200 million)

def get_todays_ipos():
    """
    Fetch today's IPO data from Finnhub API
    Returns list of IPO events for today
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    url = "https://finnhub.io/api/v1/calendar/ipo"
    params = {
        "from": today,
        "to": today,
        "token": FINNHUB_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("ipoCalendar", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IPO data: {e}")
        return []

def filter_large_ipos(ipo_list):
    """
    Filter IPOs with offer amount above the minimum threshold
    Returns list of qualifying IPOs
    """
    qualifying_ipos = []
    
    for ipo in ipo_list:
        total_value = ipo.get("totalSharesValue", 0)
        
        # Filter for IPOs with offer amount above threshold
        if total_value and total_value >= MIN_OFFER_AMOUNT:
            qualifying_ipos.append({
                "symbol": ipo.get("symbol", "N/A"),
                "name": ipo.get("name", "N/A"),
                "exchange": ipo.get("exchange", "N/A"),
                "price": ipo.get("price", "N/A"),
                "shares": ipo.get("numberOfShares", "N/A"),
                "offer_amount": total_value,
                "status": ipo.get("status", "N/A"),
                "date": ipo.get("date", "N/A")
            })
    
    return qualifying_ipos

def format_email_body(ipos):
    """
    Format the email body with IPO information
    """
    today = datetime.now().strftime("%B %d, %Y")
    
    if not ipos:
        body = f"""
<html>
<body>
<h2>Daily IPO Monitor - {today}</h2>
<p>No U.S. IPOs with offer amounts above ${MIN_OFFER_AMOUNT:,} found for today.</p>
<p><em>This is an automated message from your IPO monitoring system.</em></p>
</body>
</html>
"""
        return body
    
    # Build table rows for each IPO
    rows = ""
    for ipo in ipos:
        rows += f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>{ipo['symbol']}</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{ipo['name']}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{ipo['exchange']}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">${ipo['price']}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{ipo['shares']:,}</td>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>${ipo['offer_amount']:,}</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{ipo['status']}</td>
        </tr>
"""
    
    body = f"""
<html>
<body>
<h2>Daily IPO Monitor - {today}</h2>
<p>Found <strong>{len(ipos)}</strong> U.S. IPO(s) with offer amounts above ${MIN_OFFER_AMOUNT:,}:</p>

<table style="border-collapse: collapse; width: 100%; margin-top: 20px;">
    <thead>
        <tr style="background-color: #4CAF50; color: white;">
            <th style="padding: 10px; border: 1px solid #ddd;">Ticker</th>
            <th style="padding: 10px; border: 1px solid #ddd;">Company Name</th>
            <th style="padding: 10px; border: 1px solid #ddd;">Exchange</th>
            <th style="padding: 10px; border: 1px solid #ddd;">Price</th>
            <th style="padding: 10px; border: 1px solid #ddd;">Shares</th>
            <th style="padding: 10px; border: 1px solid #ddd;">Offer Amount</th>
            <th style="padding: 10px; border: 1px solid #ddd;">Status</th>
        </tr>
    </thead>
    <tbody>
{rows}
    </tbody>
</table>

<p style="margin-top: 20px;"><strong>Summary of Tickers:</strong> {', '.join([ipo['symbol'] for ipo in ipos])}</p>

<p style="margin-top: 30px; color: #666;"><em>This is an automated message from your IPO monitoring system.</em></p>
</body>
</html>
"""
    return body

def send_email(subject, body):
    """
    Send email notification with IPO information
    """
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = subject
        
        # Attach HTML body
        html_part = MIMEText(body, "html")
        msg.attach(html_part)
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable TLS encryption
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✓ Email sent successfully to {EMAIL_ADDRESS}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("✗ Email authentication failed. Check your email address and password.")
        print("  For Gmail, make sure you're using an App Password, not your regular password.")
        return False
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        return False

def main():
    """
    Main execution function for the IPO Monitor
    """
    print("=" * 70)
    print("IPO MONITOR - Daily Check")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Minimum Offer Amount: ${MIN_OFFER_AMOUNT:,}")
    print("-" * 70)
    
    # 1. Fetching Data
    print("Fetching today's IPO data from Finnhub...")
    all_ipos = get_todays_ipos()
    print(f"✓ Found {len(all_ipos)} total IPO(s) for today")
    
    # 2. Filtering Logic
    print("Filtering for high-value listings...")
    qualifying_ipos = filter_large_ipos(all_ipos)
    print(f"✓ Found {len(qualifying_ipos)} IPO(s) with offer amount > ${MIN_OFFER_AMOUNT:,}")
    
    # 3. Displaying Results
    if qualifying_ipos:
        print("\nQualifying IPOs:")
        for ipo in qualifying_ipos:
            print(f"  • {ipo['symbol']} - {ipo['name']} (${ipo['offer_amount']:,})")
    
    # 4. Sending the Alert
    print("\nPreparing email notification...")
    subject = f"IPO Alert: {len(qualifying_ipos)} Large IPO(s) Today - {datetime.now().strftime('%Y-%m-%d')}"
    body = format_email_body(qualifying_ipos)
    
    success = send_email(subject, body)
    
    print("-" * 70)
    if success:
        print(f"✓ Email sent successfully to {EMAIL_ADDRESS}")
        print("✓ IPO monitoring completed successfully!")
    else:
        print("✗ IPO monitoring completed with errors.")
    print("=" * 70)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

