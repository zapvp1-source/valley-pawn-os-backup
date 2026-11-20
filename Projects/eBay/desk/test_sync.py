#!/usr/bin/env python3
"""Tests for desk_sync.py. Run: python3 test_sync.py"""
import ast, os, unittest
from datetime import date
import desk_sync as ds
D = date(2026, 11, 19)
ACTIVE = {"Culpeper": [{"ItemID": "1", "SKU": "VP4033262", "Title": "Milwaukee M18"},
                       {"ItemID": "2", "SKU": "", "Title": "DeWalt Drill (DCD771) (VP4030001)"},
                       {"ItemID": "3", "SKU": "", "Title": "Apple iPhone (A2482)"}],
          "Roanoke": [{"ItemID": "9", "SKU": "ROA012528", "Title": "Guitar"}]}
def line(store="Culpeper", lid="L1", no="VP4033262", price=100.0, paid="2026-11-19T15:00:00+00:00"):
    return {"store": store, "line_id": lid, "bravo_no": no, "ring_price": price, "paid_utc": paid}
class T(unittest.TestCase):
    def test_offline(self):
        src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "desk_sync.py")).read()
        mods = {n.names[0].name.split(".")[0] for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Import)} | \
               {n.module.split(".")[0] for n in ast.walk(ast.parse(src)) if isinstance(n, ast.ImportFrom)}
        self.assertFalse(mods & {"urllib", "http", "requests", "socket", "ebay_common", "ebay_store_tokens", "subprocess"})
    def test_index_model_numbers_not_codes(self):
        idx, dup = ds.live_index(ACTIVE)
        self.assertEqual(set(idx), {"VP4033262", "VP4030001", "ROA012528"}); self.assertEqual(dup, [])
    def test_index_duplicate_dropped(self):
        a = {"Culpeper": [{"ItemID": "1", "SKU": "VP4033262"}, {"ItemID": "2", "SKU": "VP4033262"}]}
        idx, dup = ds.live_index(a); self.assertEqual(idx, {}); self.assertEqual(dup, ["VP4033262"])
    def test_takedown_counter_sale(self):
        idx, _ = ds.live_index(ACTIVE)
        p = ds.takedown_plan(idx, {"VP4033262": {"date": D, "price": 300}}, [], D)
        self.assertEqual([e["item_id"] for e in p["end"]], ["1"]); self.assertEqual(p["halt"], "")
    def test_takedown_skips_ebay_sale_and_already_ended(self):
        idx, _ = ds.live_index(ACTIVE); sold = {"VP4033262": {"date": D, "price": 300}, "ROA012528": {"date": D, "price": 5}}
        self.assertEqual(ds.takedown_plan(idx, sold, ["vp4033262"], D, ["ROA012528"])["end"], [])
    def test_takedown_ignores_old_and_future_and_unlisted(self):
        idx, _ = ds.live_index(ACTIVE)
        sold = {"VP4033262": {"date": date(2026, 11, 1), "price": 1}, "ROA012528": {"date": date(2026, 11, 20), "price": 1},
                "VAP099999": {"date": D, "price": 1}}
        self.assertEqual(ds.takedown_plan(idx, sold, [], D)["end"], [])
    def test_takedown_cap_halts(self):
        act = {"Culpeper": [{"ItemID": str(i), "SKU": "VP40%05d" % i} for i in range(11)]}
        idx, _ = ds.live_index(act); sold = {"VP40%05d" % i: {"date": D, "price": 1} for i in range(11)}
        p = ds.takedown_plan(idx, sold, [], D); self.assertEqual(p["end"], []); self.assertIn("cap", p["halt"]); self.assertEqual(len(p["held"]), 11)
    def test_ring_new(self):
        self.assertEqual(ds.ring_plan([line()], {})[0]["action"], "ring")
    def test_ring_already_in_bravo_not_rung_twice(self):
        r = ds.ring_plan([line()], {"VP4033262": {"date": D, "price": 100.0}})[0]
        self.assertEqual(r["action"], "verified"); self.assertEqual(r["price_gap"], 0)
    def test_ring_ledger_blocks_second_ring(self):
        self.assertEqual(ds.ring_plan([line()], {}, {"Culpeper|L1": "rung"})[0]["action"], "recheck")
    def test_ring_no_number_exception(self):
        self.assertEqual(ds.ring_plan([line(no="")], {})[0]["action"], "exception")
    def test_ring_counter_sold_first_exception(self):
        r = ds.ring_plan([line()], {"VP4033262": {"date": date(2026, 11, 17), "price": 90}})[0]
        self.assertEqual(r["action"], "exception"); self.assertIn("before the eBay sale", r["why"])
    def test_ring_evening_sale_uses_eastern_day(self):
        r = ds.ring_plan([line(paid="2026-11-20T02:30:00+00:00")], {"VP4033262": {"date": D, "price": 100}})[0]
        self.assertEqual(r["action"], "verified")
    def test_msg_auto(self):
        self.assertEqual(ds.classify_message("Is this still available?"), ("auto", "available"))
        self.assertEqual(ds.classify_message("How long does shipping take to Texas"), ("auto", "shipping"))
        self.assertEqual(ds.classify_message("what is your return policy"), ("auto", "returns"))
        self.assertEqual(ds.classify_message("Do you combine shipping?"), ("auto", "combine"))
    def test_msg_never_auto_on_offers_condition_orders(self):
        for m in ["Is this available? would you take $50", "what's your lowest", "does it work?", "any scratches",
                  "is it authentic", "is it 14k and how many grams", "where is my tracking", "can I pick up locally",
                  "available? call me at 540"]:
            self.assertEqual(ds.classify_message(m)[0], "draft", m)
        self.assertEqual(ds.classify_message("is this still available", has_order=True)[0], "draft")
    def test_msg_real_world_misfires_2026_11_19(self):
        for m in ["Can u do 390 + shipping?", "$200 and free shipping", "i'll go $200 and free shipping", "80 ?", "400", "Hey 25?",
                  "I would pay $60 for just the bow riser. This will save in shipping cost.", "Can you do 65", "maybe you can do 37? let me know.",
                  "I would like to ask when the item will be received by USPS, there hasn't been movement in a week",
                  "Haven't found the screw in the package. I missed the return date", "Can you send me a video of the switch",
                  "It's locked, what's the password?", "What would be the least that you would take for these?"]:
            self.assertEqual(ds.classify_message(m)[0], "draft", m)
        for m in ["Thank you.", "Ok", "Thanks i appreciate it", "Cheers bud. Great answer!"]:
            self.assertEqual(ds.classify_message(m)[0], "none", m)
        self.assertEqual(ds.classify_message("thanks, can you do 40?")[0], "draft")
    def test_msg_metal_price_and_unknown(self):
        self.assertEqual(ds.classify_message("how much is shipping price", is_precious_metal=True)[0], "draft")
        self.assertEqual(ds.classify_message("hello friend")[0], "draft")
        self.assertEqual(ds.classify_message("hello friend", store_open=False), ("auto", "after_hours"))
    def test_replies_never_invite_offers(self):
        for k in ds.TEMPLATES:
            r = ds.render_reply(k, {"free_shipping": True, "handling_days": 1, "return_days": 30}).lower()
            for bad in ("offer", "discount", "lower", "negotia", "best price"): self.assertNotIn(bad, r)
        self.assertIn("free", ds.render_reply("available", {"free_shipping": True}))
        self.assertIn("calculated", ds.render_reply("shipping", {"free_shipping": False, "handling_days": 2}))
    def test_shipping_rule(self):
        self.assertEqual(ds.shipping_mode("Video Game", 0.4), "free"); self.assertEqual(ds.shipping_mode("Jewelry", None), "free")
        self.assertEqual(ds.shipping_mode("Power Tool", 8), "calculated"); self.assertEqual(ds.shipping_mode("Guitar", None), "calculated")
        self.assertEqual(ds.shipping_mode("Video Game Console", 9), "calculated")
    def test_price_floor(self):
        f = ds.price_floor(20, 6); self.assertAlmostEqual(f - 0.15 * f - 0.40 - 6 - 1.5 - 20, 0, delta=0.02)
        self.assertGreater(ds.price_floor(20, 6, bravo_created=True), f)
    def test_gate(self):
        self.assertEqual(ds.listing_gate("PS5 game", "Video Game", 25, 5, 0.3)[1][0][:17], "single item under")
        self.assertTrue(ds.listing_gate("PS5 game lot of 4", "Video Game", 25, 5, 0.9, is_lot=True, label_cost=5)[0])
        self.assertFalse(ds.listing_gate("Glock 19 pistol", "Firearm", 400, 200, 2)[0])
        ok, why = ds.listing_gate("Ring", "Jewelry", 60, 55, 0.1, label_cost=5); self.assertFalse(ok); self.assertIn("under the floor", why[0])
        self.assertTrue(ds.listing_gate("DeWalt saw", "Power Tool", 120, 60, 12)[0])
if __name__ == "__main__":
    unittest.main(verbosity=1)
