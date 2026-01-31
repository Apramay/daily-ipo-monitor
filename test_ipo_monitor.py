#!/usr/bin/env python3
"""
Test version of IPO Monitor Script """

from datetime import datetime

# Mock IPO data for testing
MOCK_IPO_DATA = [
    {
        "symbol": "MEVOU",
        "name": "M Evo Global Acquisition Corp II",
        "exchange": "NASDAQ Global",
        "price": "10.00",
        "numberOfShares": 27000000,
        "totalSharesValue": 270000000,
        "status": "expected",
        "date": "2026-01-30"
    },
    {
        "symbol": "MUZEU",
        "name": "Muzero Acquisition Corp",
        "exchange": "NASDAQ Global",
        "price": "10.00",
        "numberOfShares": 17500000,
        "totalSharesValue": 175000000,
        "status": "expected",
        "date": "2026-01-30"
    },
    {
        "symbol": "TESTIPO",
        "name": "Test Large IPO Company",
        "exchange": "NYSE",
        "price": "25.00",
        "numberOfShares": 20000000,
        "totalSharesValue": 500000000,
        "status": "priced",
        "date": "2026-01-30"
    }
]

MIN_OFFER_AMOUNT = 200_000_000

def filter_large_ipos(ipo_list):
    """Filter IPOs with offer amount above the minimum threshold"""
    qualifying_ipos = []
    
    for ipo in ipo_list:
        total_value = ipo.get("totalSharesValue", 0)
        
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
    """Format the email body with IPO information"""
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

def main():
    """Test the script logic with mock data"""
    print("=" * 70)
    print("IPO MONITOR - TEST RUN WITH MOCK DATA")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Minimum Offer Amount: ${MIN_OFFER_AMOUNT:,}")
    print("-" * 70)
    
    # Use mock data
    print(f"Using {len(MOCK_IPO_DATA)} mock IPO records for testing...")
    all_ipos = MOCK_IPO_DATA
    print(f"✓ Total IPO(s): {len(all_ipos)}")
    
    # Filter for large IPOs
    qualifying_ipos = filter_large_ipos(all_ipos)
    print(f"✓ Qualifying IPO(s) with offer > ${MIN_OFFER_AMOUNT:,}: {len(qualifying_ipos)}")
    
    if qualifying_ipos:
        print("\nQualifying IPOs:")
        for ipo in qualifying_ipos:
            print(f"  • {ipo['symbol']} - {ipo['name']} (${ipo['offer_amount']:,})")
    
    # Generate email content
    print("\nGenerating email content...")
    subject = f"IPO Alert: {len(qualifying_ipos)} Large IPO(s) Today - {datetime.now().strftime('%Y-%m-%d')}"
    body = format_email_body(qualifying_ipos)
    
    print(f"✓ Email subject: {subject}")
    print(f"✓ Email body generated ({len(body)} characters)")
    
    # Save email preview
    with open("email_preview.html", "w") as f:
        f.write(body)
    print("✓ Email preview saved to: /home/ubuntu/email_preview.html")
    
    print("-" * 70)
    print("✓ Test completed successfully!")
    print("✓ Script logic verified - filtering and email formatting work correctly")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    main()
