#!/usr/bin/env python3
"""Tests for the eBay Desk core. Run: python3 test_desk.py   (no network, no eBay, no Bravo)."""
import os, sys, unittest
from datetime import datetime, timezone
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import desk_core as d

FX = os.path.join(HERE, "fixtures")
XML = open(os.path.join(FX, "get_orders_culpeper.xml")).read()
NOW = datetime(2026, 11, 18, 14, 0, tzinfo=timezone.utc)


class Offline(unittest.TestCase):
    def test_no_network_or_token_imports(self):
        src = open(os.path.join(HERE, "desk_core.py")).read()
        for bad in ("urllib", "requests", "socket", "http.client", "ebay_store_tokens", "ebay_common", "subprocess"):
            self.assertNotIn("import " + bad, src); self.assertNotIn("from " + bad, src)


class Codes(unittest.TestCase):
    def test_sku_wins(self):
        self.assertEqual(d.bravo_code("vap032222", "Apple iPad A2482"), "VAP032222")
    def test_title_code(self):
        self.assertEqual(d.bravo_code("", "Drill (VAP031234)"), "VAP031234")
    def test_model_numbers_are_not_codes(self):
        for t in ("iPad (A2482)", "Drill (DCD771)", "Tool (MT2500)", "Thing (2236)", "Serial (SN48849347C)"):
            self.assertEqual(d.bravo_code("", t), "", t)
    def test_junk_sku_ignored(self):
        self.assertEqual(d.bravo_code("SHELF-4", "Drill (VAP031234)"), "VAP031234")


class Money(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(d.money("$1,234.50"), 1234.5); self.assertEqual(d.money("(5.00)"), -5.0)
        self.assertEqual(d.money(""), 0.0); self.assertEqual(d.money("n/a"), 0.0)


class Orders(unittest.TestCase):
    def setUp(self):
        self.lines = d.parse_get_orders(XML, "Culpeper")
    def test_cancelled_and_unpaid_skipped(self):
        ids = {l["order_id"] for l in self.lines}
        self.assertNotIn("11-33333-33333", ids); self.assertNotIn("11-44444-44444", ids)
    def test_line_count_and_multiline_order(self):
        self.assertEqual(len(self.lines), 4)
        self.assertEqual(sum(1 for l in self.lines if l["order_id"] == "11-55555-55555"), 2)
    def test_ring_price_is_price_times_qty(self):
        l = [x for x in self.lines if x["item_id"] == "306000000006"][0]
        self.assertEqual(l["ring_price"], 25.00)
    def test_bad_ack_raises(self):
        with self.assertRaises(ValueError):
            d.parse_get_orders(XML.replace("<Ack>Success</Ack>", "<Ack>Failure</Ack>"), "Culpeper")


class Queue(unittest.TestCase):
    def setUp(self):
        self.lines = d.parse_get_orders(XML, "Culpeper")
        self.q = d.build_ring_queue(self.lines)
    def test_missing_number_flagged(self):
        r = [x for x in self.q if x["item_id"] == "306000000005"][0]
        self.assertEqual(r["state"], "needs_number")
    def test_repull_does_not_duplicate_or_reset(self):
        self.q[0]["state"] = "rung"
        q2 = d.build_ring_queue(self.lines, prior=self.q)
        self.assertEqual(len(q2), len(self.q))
        self.assertEqual(q2[0]["state"], "rung")


class Rung(unittest.TestCase):
    def setUp(self):
        q = d.build_ring_queue(d.parse_get_orders(XML, "Culpeper"))
        sold = d.load_bravo_sold([os.path.join(FX, "bravo_sold_CUL.csv")])
        self.c = {r["item_id"]: r for r in d.check_rung(q, sold, NOW)}
        self.sold = sold
    def test_rung_same_day(self):
        self.assertEqual(self.c["306000000001"]["state"], "rung")
        self.assertEqual(self.c["306000000001"]["price_gap"], 0.0)
    def test_old_bravo_sale_does_not_count(self):
        # Bravo shows VAP032222 sold 11/10, eBay order paid 11/16 -> not this sale, 45 h old -> not_rung
        self.assertEqual(self.c["306000000002"]["state"], "not_rung")
    def test_inside_24h_is_to_ring(self):
        self.assertEqual(self.c["306000000006"]["state"], "to_ring")
    def test_active_rows_ignored(self):
        self.assertNotIn("VAP030500", self.sold)
    def test_summary(self):
        s = d.store_summary(self.c.values())["Culpeper"]
        self.assertEqual((s["rung"], s["not_rung"], s["to_ring"], s["needs_number"]), (1, 1, 1, 1))
        self.assertEqual(s["not_rung_dollars"], 180.00)


class DoubleSell(unittest.TestCase):
    def test_plan_only_and_skips_ebay_sales(self):
        sold = d.load_bravo_sold([os.path.join(FX, "bravo_sold_CUL.csv")])
        active = {"Culpeper": [
            {"ItemID": "1", "Title": "Fender Squier (VAP039999)", "SKU": ""},
            {"ItemID": "2", "Title": "Drill (VAP031234)", "SKU": ""},
            {"ItemID": "3", "Title": "Ryobi saw (VAP030500)", "SKU": ""},
            {"ItemID": "4", "Title": "iPad (A2482)", "SKU": ""}]}
        plan = d.double_sell_plan(active, sold, ebay_sold_codes=["VAP031234"])
        self.assertEqual([p["item_id"] for p in plan], ["1"])
        self.assertIn("not sent", plan[0]["action"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
