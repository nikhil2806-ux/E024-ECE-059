"""Date-by-date fleet availability and reservation handling."""
from collections import defaultdict
from datetime import timedelta


class FleetManager:
    def __init__(self, rate_card):
        # Fleet counts are stored per pitch/environment rate-card entry.
        self._capacity = {(pitch, environment): entry.fleet_cabinet_count
                          for (pitch, environment), entry in rate_card.items()}
        self._booked = defaultdict(int)

    @staticmethod
    def event_dates(request):
        return [request.start_date + timedelta(days=offset)
                for offset in range(request.days)]

    def check_and_reserve(self, request, cabinets):
        key = (request.pitch, request.environment)
        capacity = self._capacity[key]
        failures = []
        for event_date in self.event_dates(request):
            booked = self._booked[(key, event_date)]
            remaining = capacity - booked
            if cabinets > remaining:
                failures.append((event_date.isoformat(), cabinets - remaining))
        if failures:
            dates = ";".join(date for date, _ in failures)
            shortfall = ";".join(f"{date}:{count}" for date, count in failures)
            return False, dates, shortfall
        # Reserve only after every date passes, so a failed multi-day request
        # never consumes cabinets on any date.
        for event_date in self.event_dates(request):
            self._booked[(key, event_date)] += cabinets
        return True, "", ""
