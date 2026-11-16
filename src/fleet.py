"""Date-by-date fleet availability. Fleet limits are per pitch, not environment."""
from collections import defaultdict
from datetime import timedelta
class FleetManager:
    def __init__(self, rate_card):
        self._capacity = {pitch: entry.fleet_cabinet_count for pitch, entry in rate_card.items()}
        self._booked = defaultdict(int)
    @staticmethod
    def event_dates(request):
        return [request.start_date + timedelta(days=i) for i in range(request.days)]
    def check_and_reserve(self, request, cabinets):
        pitch = request.pitch
        capacity = self._capacity[pitch]
        shortfall = max((self._booked[(pitch, d)] + cabinets - capacity for d in self.event_dates(request)), default=0)
        if shortfall > 0: return False, shortfall
        for d in self.event_dates(request): self._booked[(pitch, d)] += cabinets
        return True, 0
    def usage_rows(self, rate_card, from_date, to_date):
        rows=[]; d=from_date
        while d <= to_date:
            for pitch in sorted(rate_card):
                held=self._booked[(pitch,d)]
                rows.append({"date":d.isoformat(),"pitch":pitch,"cabinets_held":held,"fleet_cabinets":self._capacity[pitch],"free_cabinets":self._capacity[pitch]-held})
            d += timedelta(days=1)
        return rows
