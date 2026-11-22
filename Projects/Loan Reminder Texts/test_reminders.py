#!/usr/bin/env python3
import os, sys, unittest
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reminder_core as r

TODAY = date(2026, 11, 18)
def row(t, cust, due, disp="ON LOAN", sms="SMS"):
    return {"Ticket Number": t, "Customer": cust, "Due Date": due, "Disposition": disp, "SMS": sms}
CONTACTS = {r.norm_name("Pat Example"): [{"phone": "(540) 555-0101", "dnt": False}],
            r.norm_name("Opt Out"): [{"phone": "540-555-0102", "dnt": True}],
            r.norm_name("John Smith"): [{"phone": "5405550103", "dnt": False}, {"phone": "5405550104", "dnt": False}]}

class T(unittest.TestCase):
    def plan(self, rows, sent=frozenset()):
        return r.build_plan("Culpeper", r.tickets_from_rows(rows), CONTACTS, TODAY, sent)
    def test_no_send_capability(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "reminder_core.py")) as fh: src = fh.read()
        for bad in ("urllib", "requests", "socket", "http.client", "subprocess", "webhook"):
            self.assertNotIn(bad, src)
    def test_bravo_schedule(self):
        # 11/18/2026 is a Wednesday
        texts, _ = self.plan([row("1", "Pat Example", "11/19/2026"), row("2", "Pat Example", "11/17/2026"), row("3", "Pat Example", "11/18/2026"), row("4", "Pat Example", "11/10/2026")])
        self.assertEqual(sorted(t["kind"] for t in texts), ["courtesy", "past_due"])
    def test_past_due_repeats_fridays_only(self):
        tk = r.tickets_from_rows([row("1", "Pat Example", "11/10/2026")])
        fri, _ = r.build_plan("Culpeper", tk, CONTACTS, date(2026, 11, 20)); thu, _ = r.build_plan("Culpeper", tk, CONTACTS, date(2026, 11, 19))
        self.assertEqual((len(fri), len(thu)), (1, 0))
        nxt, _ = r.build_plan("Culpeper", tk, CONTACTS, date(2026, 11, 27), frozenset(fri[0]["keys"]))
        self.assertEqual(len(nxt), 1)
    def test_layaway_schedule(self):
        d0 = date(2026, 11, 18)   # a Wednesday
        self.assertEqual([r.layaway_kind(date(2026, 11, 19), d0), r.layaway_kind(date(2026, 11, 17), d0), r.layaway_kind(date(2026, 11, 23), d0), r.layaway_kind(date(2026, 11, 13), d0)],
                         ["layaway_notice", "layaway_late", None, None])
        fri = date(2026, 11, 20)
        self.assertEqual([r.layaway_kind(date(2026, 11, 10), fri), r.layaway_kind(date(2026, 10, 1), fri)], ["layaway_late", None])
    def test_other_days_send_nothing(self):
        texts, skipped = self.plan([row("1", "Pat Example", "11/25/2026")])
        self.assertEqual((texts, skipped), ([], []))
    def test_items_collapse_and_tickets_combine(self):
        texts, _ = self.plan([row("1", "Pat Example", "11/19/2026"), row("1", "Pat Example", "11/19/2026"), row("2", "Pat Example", "11/19/2026")])
        self.assertEqual(len(texts), 1); self.assertIn("#1, #2", texts[0]["text"]); self.assertIn("loans", texts[0]["text"])
    def test_chekkit_optout_and_holds_skipped(self):
        texts, sk = self.plan([row("2", "Opt Out", "11/19/2026"),
                               row("3", "Pat Example", "11/19/2026", disp="POLICE LOAN HOLD"), row("4", "No Body", "11/19/2026")])
        self.assertEqual(texts, []); self.assertEqual(len(sk), 3)
    def test_bravo_dnt_flag_is_ignored_chekkit_decides(self):
        texts, sk = self.plan([row("1", "Pat Example", "11/19/2026", sms="DNT")])
        self.assertEqual(len(texts), 1); self.assertEqual(sk, [])
    def test_ambiguous_name_never_texted(self):
        texts, sk = self.plan([row("1", "John Smith", "11/19/2026")])
        self.assertEqual(texts, []); self.assertIn("2 phone numbers", sk[0]["reason"])
    def test_never_twice_and_extension_restarts(self):
        texts, _ = self.plan([row("1", "Pat Example", "11/19/2026")])
        again, sk = self.plan([row("1", "Pat Example", "11/19/2026")], sent=frozenset(texts[0]["keys"]))
        self.assertEqual(again, []); self.assertEqual(sk[0]["reason"], "already sent")
        self.assertNotIn("1|courtesy|2026-12-19", texts[0]["keys"])
    def test_stop_language_and_phone(self):
        texts, _ = self.plan([row("1", "Pat Example", "11/19/2026")])
        self.assertIn("STOP", texts[0]["text"]); self.assertEqual(texts[0]["phone"], "5405550101")

if __name__ == "__main__":
    unittest.main()
