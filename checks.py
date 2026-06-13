import csv, os, sys
import tkinter as tk
from datetime import date

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
sys.path.insert(0, BASE_DIR)
from pylib import CheckGenerator

CSV_PATH = os.path.join(BASE_DIR, 'data', 'monthly_withdraw.csv')
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

# GUI for entering amounts
root = tk.Tk()
root.title("Check Amounts")

entries = []
for i, row in enumerate(rows):
    label = f"{row['from_name']} - {row.get('bank_1','')} (#{row['check_number']})"
    tk.Label(root, text=label, anchor='w').grid(row=i, column=0, sticky='w', padx=5, pady=2)
    entry = tk.Entry(root, width=10)
    entry.grid(row=i, column=1, padx=5, pady=2)
    entries.append(entry)

def generate():
    for i, entry in enumerate(entries):
        rows[i]['amount'] = entry.get().strip()
    # Save amounts back to CSV
    with open(CSV_PATH, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    root.destroy()

tk.Button(root, text="Generate PDF", command=generate).grid(row=len(rows), column=0, columnspan=2, pady=10)
root.mainloop()

SIGNATURES = {
    'Zhaoou Yu': os.path.join(BASE_DIR, 'data', 'zhaoou_signature.png'),
    'Kelly Ju': os.path.join(BASE_DIR, 'data', 'kelly_signature.png'),
    'ZOHL REALTY LLC': os.path.join(BASE_DIR, 'data', 'kelly_signature.png'),
}

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
    check['signature'] = SIGNATURES.get(row['from_name'], '')
    cg.add_check(check)

out = os.path.join(BASE_DIR, 'checks.pdf')
cg.print_checks(output_path=out, black_border=True)
print(f"PDF saved: {out}")
