import datetime
# Get the current date
current_date = datetime.date.today()

# Get the day of the week (0 = Monday, 6 = Sunday)
day_of_week = current_date.weekday()

print(day_of_week)  # Outputs 0 for Monday, 6 for Sunday