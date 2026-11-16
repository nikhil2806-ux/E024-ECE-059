"""Quotation calculations using the official sample-pack rounding conventions."""
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from .models import Quotation
ZERO=Decimal('0')
def money(x): return Decimal(x).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
def calculate_quotation(request, rate, fleet_manager):
    area=request.width_ft*request.height_ft
    cabinets=ceil(area/rate.cabinet_area_sq_ft)
    billable=Decimal(cabinets)*rate.cabinet_area_sq_ft
    gross=ZERO
    for i in range(request.days):
        day=request.start_date+timedelta(days=i)
        gross += billable*rate.rate_per_sq_ft_per_day*(Decimal('1.25') if day.weekday()>=5 else Decimal('1'))
    discount_rate=Decimal('0.20') if request.days>=8 else Decimal('0.10') if request.days>=4 else ZERO
    gross_line=money(gross); discount_line=money(gross*discount_rate)
    setup=Decimal('4000') if billable<=100 else Decimal('4000')+Decimal('35')*(billable-Decimal('100'))
    if request.environment=='OUTDOOR': setup *= Decimal('1.20')
    setup_line=money(setup)
    transport=ZERO
    if request.distance_km>15:
        transport=Decimal('45')*2*(request.distance_km-15)*(2 if billable>300 else 1)
    transport_line=money(transport)
    generator_line=money(Decimal('2500')*request.days if request.power_source=='GENERATOR' else ZERO)
    operator_count=ceil(billable/Decimal('150'))
    operator_line=money(Decimal(operator_count*1500*request.days))
    subtotal=gross_line-discount_line+setup_line+transport_line+generator_line+operator_line
    gst=money(subtotal*Decimal('0.18'))
    available,shortfall=fleet_manager.check_and_reserve(request,cabinets)
    return Quotation(request_id=request.request_id,client=request.client,status='AVAILABLE' if available else 'UNAVAILABLE',requested_area_sq_ft=area,cabinet_count=cabinets,billable_area_sq_ft=billable,rental_gross=gross_line,rental_discount=discount_line,rental_net=gross_line-discount_line,setup=setup_line,rigging=ZERO,transport=transport_line,generator=generator_line,operators_count=operator_count,operators=operator_line,pre_tax_total=subtotal,gst=gst,grand_total=subtotal+gst,affected_dates='',shortfall=str(shortfall))
