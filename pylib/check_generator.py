import os
from pathlib import Path
from fpdf import FPDF
from .textualnumber import TextualNumber

FONT_DIR = str(Path(__file__).parent / "fonts")


class CheckGenerator:
    REQUIRED = ['routing_number', 'account_number', 'check_number',
                'pay_to', 'amount', 'date', 'from_name', 'from_address1',
                'from_address2', 'bank_1', 'bank_2', 'bank_3', 'bank_4', 'memo']

    def __init__(self):
        self.checks = []

    def add_check(self, check):
        missing = [f for f in self.REQUIRED if f not in check]
        if missing:
            print(f"Missing data for check: {missing}")
            return False
        self.checks.append(check)
        return True

    @staticmethod
    def _matchcase(name, s):
        """Return s capitalized to match name's first letter case."""
        if name and name[0].isupper():
            return s.capitalize() if ' ' not in s else s.title()
        return s.lower()

    def print_checks(self, output_path=None):
        # Layout constants (identical to PHP)
        page_w, page_h = 8.5, 11
        top_margin, left_margin = 0, 0
        columns, rows = 1, 3
        gutter = 3 / 16
        rx, ry = 1.4, 1.23
        label_h = 2.85 * ry
        label_w = 6 * rx
        cell_left, cell_top = 0.25, 0.25
        logo_width = 0.5

        pdf = FPDF('P', 'in', (page_w, page_h))
        pdf.add_font('Twcen', '', os.path.join(FONT_DIR, 'twcen.ttf'))
        pdf.add_font('Micr', '', os.path.join(FONT_DIR, 'micr.ttf'))
        pdf.add_font('CourierNew', '', os.path.join(FONT_DIR, 'courier.ttf'))
        pdf.set_margins(left_margin, top_margin)
        pdf.set_display_mode("fullpage", "continuous")
        pdf.add_page()

        for lpos, check in enumerate(self.checks):
            pos = lpos % (rows * columns)
            x = left_margin + ((pos % columns) * (label_w + gutter))
            y = top_margin + ((pos // columns) * label_h)

            # --- Check template ---
            pdf.set_font('Twcen', '', 11)

            # Check number
            pdf.set_xy(x + 5.25 * rx, y + 0.33 * ry)
            pdf.cell(1, 11 / 72, str(check['check_number']), align='R')

            # Logo
            logo_offset = 0
            if check.get('logo'):
                logo_offset = logo_width + 0.005
                pdf.image(check['logo'], x + cell_left, y + cell_top + 0.12 * ry, logo_width)

            # Name / address
            pdf.set_font('Twcen', '', 10)
            pdf.set_xy(x + cell_left + logo_offset, y + cell_top + 0.1 * ry)
            pdf.cell(2, 10 / 72, check['from_name'], new_x="LEFT", new_y="NEXT")
            pdf.set_font('Twcen', '', 7)
            pdf.cell(2, 7 / 72, check['from_address1'], new_x="LEFT", new_y="NEXT")
            pdf.cell(2, 7 / 72, check['from_address2'], new_x="LEFT", new_y="NEXT")

            pdf.set_font('Twcen', '', 7)

            # Date line
            pdf.line(x + 3.5 * rx, y + 0.58 * ry, x + 3.5 * rx + 1.2 * rx, y + 0.58 * ry)
            pdf.set_xy(x + 3.5 * rx, y + 0.48 * ry)
            pdf.cell(1, 7 / 72, self._matchcase(check['from_name'], "date"))

            # Pay to line
            pdf.line(x + cell_left, y + 1.1 * ry, x + cell_left + 4.1 * rx, y + 1.1 * ry)
            pdf.set_xy(x + cell_left, y + 0.88 * ry)
            pdf.multi_cell(0.6, 7 / 72, self._matchcase(check['from_name'], "pay to the order of"), align='L')

            # Amount box
            pdf.rect(x + 4.5 * rx, y + 0.83 * ry, 1.1 * rx, 0.25 * ry)

            # Dollars line
            pdf.line(x + cell_left, y + 1.5 * ry, x + cell_left + 5.37 * rx, y + 1.5 * ry)
            pdf.set_xy(x + cell_left + 4.37 * rx, y + 1.4 * ry)
            pdf.cell(1, 7 / 72, self._matchcase(check['from_name'], "dollars"), align='R')

            # Bank info
            pdf.set_xy(x + cell_left, y + 1.6 * ry)
            pdf.cell(2, 7 / 72, check['bank_1'], new_x="LEFT", new_y="NEXT")
            pdf.cell(2, 7 / 72, check['bank_2'], new_x="LEFT", new_y="NEXT")
            pdf.cell(2, 7 / 72, check['bank_3'], new_x="LEFT", new_y="NEXT")
            pdf.cell(2, 7 / 72, check['bank_4'], new_x="LEFT", new_y="NEXT")

            # Memo line
            pdf.line(x + cell_left, y + 2.225 * ry, x + cell_left + 2.9 * rx, y + 2.225 * ry)
            pdf.set_xy(x + cell_left, y + 2.125 * ry)
            pdf.cell(1, 7 / 72, self._matchcase(check['from_name'], "memo"))

            # Signature line
            pdf.line(x + 3.25 * rx, y + 2.225 * ry, x + 3.25 * rx + 2.375 * rx, y + 2.225 * ry)

            # --- Fill values ---
            pdf.set_font('CourierNew', '', 12)

            # Date value
            if check['date']:
                pdf.set_xy(x + 3.5 * rx + 0.3 * rx, y + 0.38 * ry)
                pdf.cell(1, 0.25, check['date'])

            # Pay to value
            if check['pay_to']:
                pdf.set_xy(x + cell_left + 0.5 * rx, y + 0.88 * ry)
                pdf.cell(1, 0.25, check['pay_to'])

            # Amount
            if check.get('amount') and float(check['amount']) > 0:
                amount = float(check['amount'])
                dollars = int(amount)
                cents = round((amount - dollars) * 100)
                tn = TextualNumber()
                dollars_str = tn.num_to_words(dollars)
                amt_string = "***" + dollars_str.capitalize() + " dollars"
                amt_string += f" and {cents}/100***" if cents > 0 else " and 00/100***"

                pdf.set_font('CourierNew', '', 12)
                pdf.set_xy(x + cell_left, y + 1.28 * ry)
                pdf.cell(1, 0.25, amt_string)

                amt = f"${amount:,.2f}"
                pdf.set_xy(x + 4.5 * rx + 0.06 * rx, y + 0.83 * ry)
                pdf.cell(1, 0.25, amt)

            # Memo value
            pdf.set_font('CourierNew', '', 12)
            pdf.set_xy(x + cell_left + 0.3 * rx, y + 2.02 * ry)
            pdf.cell(1, 0.25, check['memo'])

            # Routing / account (MICR line)
            pdf.set_font('Micr', '', 10)
            routing_str = check.get('codeline',
                f"t{check['routing_number']}t{check['account_number']}o{check['check_number']}")
            pdf.set_xy(x + cell_left, y + 2.47 * ry)
            pdf.cell(5, 10 / 72, routing_str)

            # Signature
            sig = check.get('signature', '')
            if sig.endswith('png'):
                pdf.image(sig, x + cell_left + 3.4 * rx, y + 1.88 * ry, 1.75 * rx)
            elif sig:
                pdf.set_font('Twcen', '', 10)
                pdf.set_xy(x + cell_left + 3.4 * rx, y + 2.01 * ry)
                pdf.cell(1, 0.25, sig)

            # Pre-authorized disclaimer
            if 'pre_auth' in check:
                pdf.set_font('Twcen', '', 6)
                pdf.set_xy(x + cell_left + 3.3 * rx, y + 2.155 * ry)
                pdf.cell(1, 0.25, "This check is pre-authorized by your depositor")

            # Page break
            if pos == (rows * columns - 1) and lpos != len(self.checks) - 1:
                pdf.add_page()

        if output_path:
            pdf.output(output_path)
        return pdf.output()
