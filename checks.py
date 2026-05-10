import csv, os, sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pylib import CheckGenerator

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'monthly_withdraw.csv')
today = date.today().strftime('%-m/%-d/%Y') if os.name != 'nt' else date.today().strftime('%#m/%#d/%Y')

# Read, increment check_number, update date
rows = []
with open(CSV_PATH, newline='') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        row['check_number'] = str(int(row['check_number']) + 1)
        row['date'] = today
        rows.append(row)

# Write back
with open(CSV_PATH, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Updated {len(rows)} checks: check_number +1, date -> {today}")

# Generate PDF
cg = CheckGenerator()
for row in rows:
    if not row.get('amount', '').strip():
        continue
    check = {}
    for k, v in row.items():
        if k == 'routing_number:account_number':
            parts = v.split(':')
            check['routing_number'] = parts[0]
            check['account_number'] = parts[1] if len(parts) > 1 else ''
        else:
            check[k] = v
    cg.add_check(check)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'checks.pdf')
cg.print_checks(output_path=out, black_border=True)
print(f"PDF saved: {out}")
