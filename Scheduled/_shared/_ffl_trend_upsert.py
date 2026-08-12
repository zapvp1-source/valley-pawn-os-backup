import sys
sys.path.insert(0, '/Users/joshuadavis/Documents/Claude/Scheduled/_shared')
from sheets_helper import SheetsClient

SID = '1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs'
c = SheetsClient()
meta = c._svc.spreadsheets().get(spreadsheetId=SID).execute()
tab = meta['sheets'][0]['properties']['title']
print('TAB:', tab)

# July 2026 (from today's verified pull)
row = {"Month":"2026-07",
       "WAY Transfers":10,"CUL Transfers":11,"HAR Transfers":1,"LEX Transfers":13,"ROA Transfers":8,"Total Transfers":43,
       "WAY Revenue":270,"CUL Revenue":255,"HAR Revenue":25,"LEX Revenue":345,"ROA Revenue":230,"Total Revenue":1125}
res = c.upsert_by_key(SID, tab, "Month", [row])
print('UPSERT:', res)
print('READBACK:', c.read(SID, f"{tab}!A1:M4"))
