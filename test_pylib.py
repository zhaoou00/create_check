import sys, os, csv, unittest
_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
sys.path.insert(0, _DIR)
from pylib import TextualNumber, CheckGenerator


class TestTextualNumber(unittest.TestCase):
    def setUp(self):
        self.tn = TextualNumber()

    def test_zero(self):
        self.assertEqual(self.tn.num_to_words(0), "zero")

    def test_ones(self):
        self.assertEqual(self.tn.num_to_words(7), "Seven")

    def test_teens(self):
        self.assertEqual(self.tn.num_to_words(15), "Fifteen")

    def test_tens(self):
        self.assertEqual(self.tn.num_to_words(42), "Forty-Two")

    def test_hundreds(self):
        self.assertEqual(self.tn.num_to_words(100), "One Hundred")
        self.assertEqual(self.tn.num_to_words(305), "Three Hundred and Five")

    def test_thousands(self):
        self.assertEqual(self.tn.num_to_words(1250), "One Thousand Two Hundred and Fifty")

    def test_out_of_range(self):
        self.assertIn("out of script range", self.tn.num_to_words(1000000000))

    def test_csv_constructor(self):
        t = TextualNumber("100.50")
        self.assertEqual(len(t.data), 1)
        self.assertIn("Rupees", t.data[0])
        self.assertIn("Paise", t.data[0])


class TestCheckGenerator(unittest.TestCase):
    def _make_check(self, **overrides):
        c = dict(routing_number='121000248', account_number='9876543210',
                 check_number='1001', pay_to='John Smith', amount=1250.75,
                 date='05/10/2026', from_name='Jane Doe',
                 from_address1='123 Main St', from_address2='NY, NY 10001',
                 bank_1='Chase Bank', bank_2='456 Park Ave',
                 bank_3='New York', bank_4='NY 10022', memo='Test memo')
        c.update(overrides)
        return c

    def test_add_valid(self):
        cg = CheckGenerator()
        self.assertTrue(cg.add_check(self._make_check()))
        self.assertEqual(len(cg.checks), 1)

    def test_add_missing_field(self):
        cg = CheckGenerator()
        bad = self._make_check()
        del bad['pay_to']
        self.assertFalse(cg.add_check(bad))

    def test_generate_pdf(self):
        cg = CheckGenerator()
        cg.add_check(self._make_check())
        cg.add_check(self._make_check(check_number='1002', amount=99.00, pay_to='Alice'))
        pdf_bytes = cg.print_checks()
        self.assertTrue(pdf_bytes[:5] == b'%PDF-')

    def test_generate_pdf_from_csv(self):
        """Same flow as checks.php — read input_php.csv and produce PDF."""
        csv_path = os.path.join(_DIR, 'input_php.csv')
        if not os.path.exists(csv_path):
            self.skipTest("input_php.csv not found")
        cg = CheckGenerator()
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                check = {}
                for k, v in row.items():
                    if k == 'routing_number:account_number':
                        parts = v.split(':')
                        check['routing_number'] = parts[0]
                        check['account_number'] = parts[1] if len(parts) > 1 else ''
                    else:
                        check[k] = v
                cg.add_check(check)
        out = os.path.join(_DIR, 'checks.pdf')
        cg.print_checks(output_path=out)
        self.assertTrue(os.path.exists(out))
        print(f"\n  -> PDF saved: {out}")


if __name__ == '__main__':
    unittest.main()
