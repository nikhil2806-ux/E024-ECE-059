"""Write evaluation-format quotation and fleet CSV files."""
import csv
from datetime import date

def write_outputs(output_dir, quotations, fleet_rows):
    output_dir.mkdir(parents=True, exist_ok=True)
    qfields=['request_id','pitch','cabinets','billable_sqft','rental_gross_rs','multiday_discount_rs','setup_rs','transport_rs','generator_rs','operator_rs','subtotal_rs','gst_rs','total_rs','availability','shortfall_cabinets']
    with open(output_dir/'quotations.csv','w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=qfields); w.writeheader()
        for q in quotations:
            w.writerow({'request_id':q.request_id,'pitch':q._pitch,'cabinets':q.cabinet_count,'billable_sqft':q.billable_area_sq_ft,'rental_gross_rs':q.rental_gross,'multiday_discount_rs':q.rental_discount,'setup_rs':q.setup,'transport_rs':q.transport,'generator_rs':q.generator,'operator_rs':q.operators,'subtotal_rs':q.pre_tax_total,'gst_rs':q.gst,'total_rs':q.grand_total,'availability':q.status,'shortfall_cabinets':int(q.shortfall or 0)})
    ffields=['date','pitch','cabinets_held','fleet_cabinets','free_cabinets']
    with open(output_dir/'fleet_usage.csv','w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=ffields); w.writeheader(); w.writerows(fleet_rows)
