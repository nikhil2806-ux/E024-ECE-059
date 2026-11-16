"""Command-driven ECE-059 LED rental quotation engine."""
import argparse
from datetime import datetime
from pathlib import Path
from src.loader import load_rate_card, load_event_requests, InputDataError
from src.fleet import FleetManager
from src.quotation import calculate_quotation
from src.writer import write_outputs

def main():
    ap=argparse.ArgumentParser(description='ECE-059 LED Display and Signage Rental Quotation Engine')
    ap.add_argument('--rate-card',default='rate_card.csv')
    ap.add_argument('--requests',default='requests.csv')
    ap.add_argument('--commands',default='commands.txt')
    ap.add_argument('--output',default='output')
    a=ap.parse_args()
    try:
        # Interpret the supplied command file in order; load commands select the inputs.
        rate_path,request_path=a.rate_card,a.requests
        commands=[]
        with open(a.commands,encoding='utf-8-sig') as f:
            commands=[line.strip() for line in f if line.strip() and not line.lstrip().startswith('#')]
        for line in commands:
            parts=line.split('|')
            if parts[0]=='LOAD_RATE_CARD': rate_path=str(Path(a.commands).parent/parts[1])
            elif parts[0]=='LOAD_REQUESTS': request_path=str(Path(a.commands).parent/parts[1])
        rate_card=load_rate_card(rate_path)
        requests=load_event_requests(request_path,rate_card)
        fleet=FleetManager(rate_card); quotes=[]
        for req in requests:
            q=calculate_quotation(req,rate_card[req.pitch],fleet); q._pitch=req.pitch; quotes.append(q)
        start,end=datetime.strptime('2026-11-01','%Y-%m-%d').date(),datetime.strptime('2026-12-31','%Y-%m-%d').date()
        for line in commands:
            parts=line.split('|')
            if parts[0]=='PRINT_FLEET':
                start=datetime.strptime(parts[1],'%Y-%m-%d').date(); end=datetime.strptime(parts[2],'%Y-%m-%d').date()
        fleet_rows=fleet.usage_rows(rate_card,start,end)
        write_outputs(Path(a.output),quotes,fleet_rows)
    except (InputDataError,OSError,ValueError) as exc:
        print(f'Input/command error: {exc}')
        return 2
    print(f'Processed {len(requests)} request(s); generated {len(quotes)} quotation(s).')
    print(f'Outputs written to: {Path(a.output).resolve()}')
    return 0
if __name__=='__main__': raise SystemExit(main())
