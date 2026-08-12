import sys
sys.path.insert(0, '/Users/joshuadavis/Documents/Claude/Scheduled/_shared')
from sheets_helper import SheetsClient

SID = '1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs'
c = SheetsClient()
meta = c._svc.spreadsheets().get(spreadsheetId=SID).execute()
props = meta['sheets'][0]['properties']
tab_id = props['sheetId']
old_title = props['title']

# 1) rename tab -> "Monthly"; 2) force column A (Month) to plain-text format
c._svc.spreadsheets().batchUpdate(spreadsheetId=SID, body={"requests":[
    {"updateSheetProperties":{"properties":{"sheetId":tab_id,"title":"Monthly"},"fields":"title"}},
    {"repeatCell":{
        "range":{"sheetId":tab_id,"startColumnIndex":0,"endColumnIndex":1},
        "cell":{"userEnteredFormat":{"numberFormat":{"type":"TEXT"}}},
        "fields":"userEnteredFormat.numberFormat"}}
]}).execute()
tab = "Monthly"

# 3) clear any data rows (remove the bad serial-date July row)
c._svc.spreadsheets().values().clear(spreadsheetId=SID, range=f"{tab}!A2:M1000").execute()

# 4) re-upsert July 2026 (Month now stays text)
row = {"Month":"2026-07",
       "WAY Transfers":10,"CUL Transfers":11,"HAR Transfers":1,"LEX Transfers":13,"ROA Transfers":8,"Total Transfers":43,
       "WAY Revenue":270,"CUL Revenue":255,"HAR Revenue":25,"LEX Revenue":345,"ROA Revenue":230,"Total Revenue":1125}
print('UPSERT:', c.upsert_by_key(SID, tab, "Month", [row]))
print('READBACK:', c.read(SID, f"{tab}!A1:M4"))
