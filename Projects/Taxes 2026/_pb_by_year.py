import json, collections

with open("pb_bald_rock_orders.json", "r", encoding="utf-8") as f:
    orders = json.load(f)

by_year = collections.defaultdict(lambda: {"total": 0.0, "orders": 0, "items": 0})

for o in orders:
    date = o.get("date") or ""
    year = date[:4] if date else "UNKNOWN"
    by_year[year]["total"] += o.get("total", 0.0)
    by_year[year]["orders"] += 1
    by_year[year]["items"] += len(o.get("items", []))

print(f"{'Year':<8}{'Orders':<10}{'Items':<10}{'Total':>14}")
grand_total = 0.0
grand_orders = 0
for year in sorted(by_year.keys()):
    v = by_year[year]
    print(f"{year:<8}{v['orders']:<10}{v['items']:<10}{v['total']:>14,.2f}")
    grand_total += v["total"]
    grand_orders += v["orders"]
print(f"{'TOTAL':<8}{grand_orders:<10}{'':<10}{grand_total:>14,.2f}")

with open("pb_bald_rock_by_year.json", "w") as f:
    json.dump({y: v for y, v in sorted(by_year.items())}, f, indent=1)
print("\nWrote pb_bald_rock_by_year.json")
