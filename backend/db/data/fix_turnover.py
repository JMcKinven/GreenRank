#!/usr/bin/env python3

import csv

print("=" * 80)
print("FIXING TURNOVER UNITS IN companies.csv")
print("=" * 80)

input_file = 'companies.csv'
output_file = 'companies_fixed.csv'

# Read and fix the data
rows = []
with open(input_file, 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    rows.append(header)

    for row in reader:
        company_id = int(row[0])

        # Companies 275-300 have turnover in millions, convert to billions
        if company_id >= 275:
            try:
                turnover_millions = float(row[3])
                turnover_billions = turnover_millions / 1000.0
                row[3] = f"{turnover_billions:.5f}"  # Keep precision
                print(
                    f"Company {company_id:3d}: {row[1][:30]:30s} {turnover_millions:8.2f}M -> {turnover_billions:8.5f}B")
            except (ValueError, IndexError):
                print(f"Company {company_id:3d}: Skipping (no turnover data)")

        rows.append(row)

# Write fixed data
with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print("\n" + "=" * 80)
print(f"Fixed {len(rows) - 1} companies")
print(f"Output written to: {output_file}")
print("=" * 80)

# Verify a few examples
print("\nVerification - Last 10 companies:")
print("-" * 80)
for row in rows[-10:]:
    if row == header:
        continue
    company_id = row[0]
    name = row[1][:30]
    turnover = row[3]
    print(f"  {company_id:>3s}. {name:30s} £{turnover:>10s}B")

print("\nTo apply the fix:")
print("  mv /mnt/project/companies_fixed.csv /mnt/project/companies.csv")
print("=" * 80)