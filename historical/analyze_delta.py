def get_month_idx(date_str):
    return int(date_str.split("-")[1]) - 1

with open("./historical/delta.csv", "r") as f:
    lines = f.readlines()
    yearly_stats = lines[1:367]

monthly_power_kwh = [[] for _ in range(12)]

for stats in yearly_stats:
    date, power = stats.split(",")
    month = get_month_idx(date)
    power = power.strip()

    if not power:
        continue

    monthly_power_kwh[month].append(float(power))

average_daily_power = [sum(powers) / len(powers) for powers in monthly_power_kwh]

total_power_kwh = 0

for stats in yearly_stats:
    date, power = stats.split(",")
    month = get_month_idx(date)
    power = power.strip()

    if not power:
        total_power_kwh += average_daily_power[month]
    else:
        total_power_kwh += float(power)

print(average_daily_power)
print(round(total_power_kwh, 3))