"""Generate blank checks with the original layout (3 per page, no black border).

Usage from the command line:
    python3 blank_checks.py 021200339 381048765055 --start 1001 --pages 10

Usage from Python:
    from blank_checks import make_blank_checks
    make_blank_checks('021200339', '381048765055', start=1001, pages=10)
"""
import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
from pylib import CheckGenerator

CHECKS_PER_PAGE = 3


def make_blank_checks(routing, account, start=1001, pages=10, bank='',
                      name='', address1='', address2='', output_path=None):
    """Write a PDF of blank checks numbered from `start`. Returns the output path."""
    count = pages * CHECKS_PER_PAGE
    end = start + count - 1
    if output_path is None:
        output_path = os.path.join(BASE_DIR, f'blank_checks_{account[-4:]}_{start}-{end}.pdf')

    cg = CheckGenerator()
    for n in range(start, end + 1):
        cg.add_check(dict(
            logo='', check_number=n,
            from_name=name, from_address1=address1, from_address2=address2,
            routing_number=routing, account_number=account,
            bank_1=bank, bank_2='', bank_3='', bank_4='',
            signature='', pay_to='', amount='', date='', memo='',
        ))
    cg.print_checks(output_path=output_path, black_border=False)
    print(f'Saved {count} blank checks ({start}-{end}, {pages} pages): {output_path}')
    return output_path


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Generate blank checks, 3 per page.')
    p.add_argument('routing')
    p.add_argument('account')
    p.add_argument('--start', type=int, default=1001, help='first check number (default 1001)')
    p.add_argument('--pages', type=int, default=10, help='number of pages (default 10)')
    p.add_argument('--bank', default='', help='bank name printed on the check')
    p.add_argument('--name', default='', help='account holder name')
    p.add_argument('--address1', default='')
    p.add_argument('--address2', default='')
    p.add_argument('-o', '--output', default=None)
    a = p.parse_args()
    make_blank_checks(a.routing, a.account, a.start, a.pages, a.bank,
                      a.name, a.address1, a.address2, a.output)
