import xml.etree.ElementTree as ET
import csv
import re
import pandas as pd

# Parse the XML file
tree = ET.parse('sms_backup.xml')
root = tree.getroot()

# Define patterns to search for
patterns = [
    "HDFC Bank CREDIT Card xx3455",
    "HDFC Bank Card x3455",
    "ICICI Bank Acct XX646 debited"
]

# Extract lines matching the patterns
matching_lines = []
for sms in root.findall('sms'):
    body = sms.get('body')
    if body and any(pattern in body for pattern in patterns):
        matching_lines.append(body)
        

# Save matching lines to a file
with open('matching_lines.txt', 'w', encoding='utf-8') as f:
    for line in matching_lines:
        f.write(line + '\n')

# Extract lines with amount and date and save to CSV
output_data = []
# Extract additional details for HDFC and ICICI transactions
# Add a 'bank' column based on the body content
for sms in root.findall('sms'):
    body = sms.get('body')
    date = sms.get('date')
    if body and date:
        # Update regex pattern to handle ',' in big numbers while extracting amount
        match_amount = re.search(r'Rs.?([0-9,]+\.?[0-9]*)', body)
        if match_amount:
            # Remove commas from the extracted amount before processing
            amount = match_amount.group(1).replace(",", "")
            expense = None
            bank = None
            if "HDFC Bank CREDIT Card xx3455" in body or "HDFC Bank Card x3455" in body or "HDFC Bank Card 3455" in body:
                expense_match = re.search(r'at (.+?) on', body, re.IGNORECASE)
                print(expense_match)
                if expense_match:
                    expense = expense_match.group(1).strip()
                bank = "HDFC"
                # Ensure 'expense' is not None before checking for 'Brigade Gateway'
                if expense and "Brigade Gateway" in expense:
                    expense = expense.replace("Brigade Gateway", "AMAZON")
                output_data.append({
                'date': pd.to_datetime(pd.to_numeric(date), unit='ms').date(),
                'amount': amount,
                'expense': expense,
                'bank': bank
                })
            elif "ICICI Bank Acct XX646 debited" in body:
                # Update regex pattern to consider ';' or '&' before 'credited'
                expense_match = re.search(r'[;&](.+?)credited', body, re.IGNORECASE)
                print(expense_match)
                if expense_match:
                    expense = expense_match.group(1).strip()
                bank = "ICICI"
                if expense and "Acct XX701" in expense:
                    expense = expense.replace("Acct XX701", "BRIGADE SANTUARY")
                output_data.append({
                'date': pd.to_datetime(pd.to_numeric(date), unit='ms').date(),
                'amount': amount,
                'expense': expense,
                'bank': bank
                })

            

# Save extracted data to CSV
with open('amount_date.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['date', 'amount', 'expense', 'bank']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output_data)
