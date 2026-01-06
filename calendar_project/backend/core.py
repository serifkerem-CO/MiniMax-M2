"""
Fractal 60-Base Time System
Combines 13-month calendar (28 days each) with 60-cycle system (12 Animals x 5 Elements)
"""

class FractalTimeSystem:
    def __init__(self):
        # 12 Animals (Chinese Zodiac)
        self.animals = [
            "Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
            "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"
        ]

        # 5 Elements
        self.elements = ["Wood", "Fire", "Earth", "Metal", "Water"]

        # 13 months, 28 days each = 364 days/year
        self.days_per_month = 28
        self.months_per_year = 13
        self.days_per_year = 364

        # Reference epoch: January 1, 2000 (Unix timestamp: 946684800)
        self.epoch = 946684800

    def get_60_cycle(self, index):
        """
        Returns the 60-cycle signature (Element + Animal)
        Based on Sexagenary cycle (Ganzhi)
        """
        cycle_pos = index % 60
        animal_idx = cycle_pos % 12
        element_idx = (cycle_pos // 2) % 5

        return {
            "animal": self.animals[animal_idx],
            "element": self.elements[element_idx],
            "cycle_position": cycle_pos
        }

    def timestamp_to_fractal(self, timestamp):
        """
        Converts Unix timestamp to Fractal Time format
        """
        seconds_since_epoch = int(timestamp - self.epoch)

        # Calculate days since epoch
        days_since_epoch = seconds_since_epoch // 86400

        # Calculate year, month, day in 13-month calendar
        year = 2000 + (days_since_epoch // self.days_per_year)
        day_of_year = days_since_epoch % self.days_per_year
        month = (day_of_year // self.days_per_month) + 1
        day = (day_of_year % self.days_per_month) + 1

        # Calculate time within the day
        seconds_in_day = seconds_since_epoch % 86400
        hour = seconds_in_day // 3600
        minute = (seconds_in_day % 3600) // 60
        second = seconds_in_day % 60

        # 60-based minute and second indices
        minute_idx = (hour * 60 + minute) % 1440  # Total minutes in a day
        second_idx = seconds_in_day

        return {
            "timestamp": timestamp,
            "fractal": {
                "year": {
                    "val": year,
                    "signature": self.get_60_cycle(year)  # Year Cycle
                },
                "month": {
                    "val": month,
                    "signature": self.get_60_cycle(month)  # Month Cycle (1-13)
                },
                "day": {
                    "val": day,
                    "signature": self.get_60_cycle(days_since_epoch)  # Daily Cycle
                },
                "minute": {
                    "val": minute_idx,
                    "signature": self.get_60_cycle(minute_idx)  # Minute Cycle
                },
                "second": {
                    "val": second_idx,
                    "signature": self.get_60_cycle(second_idx)  # Second Cycle
                }
            }
        }

# Test block
if __name__ == "__main__":
    fs = FractalTimeSystem()
    import time
    print(fs.timestamp_to_fractal(time.time()))
