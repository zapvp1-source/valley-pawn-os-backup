# Bravo POS — Complete Screen & Report Map

_Generated 2026-09-30 22:55 by `bravo_map_compile.py` from BravoMapper's read-only crawl. Do not hand-edit; add human notes to the `bravo-context` skill instead._

**Status:** IN PROGRESS (resumes nightly) · 46 steps mapped · 1 steps could not be mapped · last crawler state: `2026-09-30 22:54:46 ABORT no-dashboard after S_Customers__Schedule_Mobile_Event`

Raw data: `output/bravo_map/` — `screens/` (full UI tree per screen), `shots/` (screenshots), `lists/` (report lists, Custom Reports criteria / columns / saved reports), `index.tsv`, `RUN_LOG.md`.

Store mapped: screens and reports are identical at all 5 stores (one Bravo build, one login).

## Dashboard

### Dashboard
_key `D_dashboard` · captured 2026-09-30 22:30:21 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/D_dashboard.png`

- **Menu items:** System
- **Buttons:** Minimize `Minimize-Restore`; Restore `Maximize-Restore`; Close; (no label) `PART_ExpandButton`; DevExpress.Xpf.Editors.DateEditButtonInfo `PART_Item`; (no label) `PART_Item`; Search; Fast Sale; (no label) `PART_Button`; Employee Activity; Locate Layaways; Layaways Overdue; Price Items; Locate Loan/Buy; Loans To Expire; Send Loan Notice; Loans to Retag; Police Export; Post to Accounting; Receive Batch; Web Fulfillment; Web In-Store Pickup; Locate Pending Payment; Web Payment Settlement; Web Returns; Web Offers; Web Feedbacks; (no label) `lblDevOrTest`
- **Fields:** BravoMaskedTextBox `txtFirstName`; BravoMaskedTextBox `PART_Editor`; BravoMaskedTextBox `txtLastName`; (no label) `txtPhone`; BravoDateEdit `bmtbDateOfBirth`; BravoDateEdit `PART_Editor`; BravoMaskedTextBox `bmtbBusinessName`; PopupBaseEdit `PART_Editor`
- **Labels:** Search; Fast Sale; Reporting Pro POWERED BY Bravo; Employee Activity; Store KPIs; eCommerce Metrics; Company KPIs; Locate Layaways; Layaways Overdue; Price Items; 247; Locate Loan/Buy; Loans To Expire; 115; Send Loan Notice; Loans to Retag; Police Export; 20; Post to Accounting; 24; Receive Batch; Web Fulfillment; Web In-Store Pickup; Locate Pending Payment; Web Payment Settlement; Web Returns; Web Offers; Web Feedbacks; FREE1; Solution Center; Support Inbox; Lock Session; Logout; Chat with Agent
- **Options:** (no label) `GMIntakeButton`; Jewelry `JewelryIntakeButton`; (no label) `InventoryLookupButton`
- **Links:** Solution Center; Support Inbox; Lock Session; Logout; Chat with Agent

## Modules (right sidebar)

### Module: Customers
_key `M_Customers` · captured 2026-09-30 22:31:44 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/M_Customers.png`

- **Labels:** Schedule an event to send a mobile message to all customers; Done; Review Duplicates; 28; Custom Reports; Print List; Mark Customer Contacted; Send Mobile Message; Schedule Mobile Event; Layouts; Name; Saved Layouts; Delete Layout; Save; Show summary panel; Name `PART_Content`; Phone `PART_Content`; Address `PART_Content`; E-Mail `PART_Content`; Total Sales `PART_Content`; Total Buys `PART_Content`; Total Loans `PART_Content`; MobilePawn `PART_Content`; SMS `PART_Content`
- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Custom Reports; Print List; Mark Customer Contacted; Send Mobile Message; Schedule Mobile Event; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Options:** Review Duplicates `btnReviewDuplicates`
- **Fields:** BravoMaskedTextBox; BravoComboBox
- **Checkboxes:** Show summary panel
- **Grid columns:** FullName; PublicPhone; FullAddress; Email; TotalSales; TotalBuys; TotalLoans; BuyaMobileColumnSortOrder; SmsAbilityStatus

#### Customers > Custom Reports
_key `S_Customers__Custom_Reports` · captured 2026-09-30 22:51:50 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Customers__Custom_Reports.png`

- **Fields:** BravoMaskedTextBox `BoxReportName`; BravoComboBox `BoxColumns`; BravoComboBox `BoxIsShared`; BravoComboBox; BravoComboBox `BoxSelectCriteria`; BravoMaskedTextBox
- **Buttons:** Save; New Report; Delete Report; Cancel; (no label) `HeaderSite`; Done `btnDone`; Custom Reports; Print List; Mark Customer Contacted; Send Mobile Message; Schedule Mobile Event; Delete Layout; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Save; Max rows; New Report; Delete Report; Ok; Cancel; Done; Review Duplicates; 28; Custom Reports; Print List; Mark Customer Contacted; Send Mobile Message; Schedule Mobile Event; Layouts; Name; Saved Layouts; Delete Layout; Show summary panel; Name `PART_Content`; Phone `PART_Content`; Address `PART_Content`; E-Mail `PART_Content`; Total Sales `PART_Content`; Total Buys `PART_Content`; Total Loans `PART_Content`; MobilePawn `PART_Content`; SMS `PART_Content`
- **Options:** Review Duplicates `btnReviewDuplicates`
- **Checkboxes:** Show summary panel
- **Grid columns:** FullName; PublicPhone; FullAddress; Email; TotalSales; TotalBuys; TotalLoans; BuyaMobileColumnSortOrder; SmsAbilityStatus

- **Columns available (16):** SHARED GLOBALLY | Active Customers 2022; Chekkit Invites; SHARED GLOBALLY | Customer Address Check; SHARED GLOBALLY | Active Customers 2023; SHARED GLOBALLY | Customers First Time In; SHARED GLOBALLY | Active Customers 2024; SHARED GLOBALLY | Demographics Report; Constant Contact; SHARED COMPANY-WIDE | Chekkit Invites 2; SHARED COMPANY-WIDE | Chekkit Invites 1; SHARED COMPANY-WIDE | Loan Totals; SHARED COMPANY-WIDE | Sales Totals; SHARED COMPANY-WIDE | Constant Contact; SHARED COMPANY-WIDE | Email; SHARED COMPANY-WIDE | Chekkit Invites; SHARED COMPANY-WIDE | Email Monthly
- **Filter criteria available (57):** Address Line 1; Address Line 2; Alert; All Transactions Blocked; Birth State or Country; Birthday; Build; Business Name; Buys Activity; City; Complexion; Country; E-Mail; Employer; Eye Color; FFL Expiration Date; FFL Number; First Name; First Time In; Hair Color; Has Main Photo; Height; Home Phone; Invalid Address; Last Contact; Last Name; Last Time In; Loans Activity; Maternal Surname; Middle Name; Mobile; MobilePawn Activation Date; Note; Occupation; Omni-Channel; Personal ID Number; Preferred Language; Race; Referral Source; Sales Activity; Scars/Marks/Tattoos; Sex; State Abbreviation; State/Province; Store; Suffix; Tax Exempt - Other; Tax Exempt Certificate; Total Buys; Total Loans; Total Rentals; Total Sales; Transacted Between; Type; Weight; Work Phone; Zip Code
- **Saved reports (35):** <new report>; SHARED GLOBALLY | Active Customers 2022; SHARED GLOBALLY | Active Customers 2023; SHARED GLOBALLY | Active Customers 2024; SHARED GLOBALLY | Active Customers 2025; SHARED COMPANY-WIDE | ALL EMAILS; SHARED GLOBALLY | Amazon Customers; SHARED GLOBALLY | Birthday Range; SHARED GLOBALLY | Buya Customers; SHARED COMPANY-WIDE | Chekkit Inactives; SHARED COMPANY-WIDE | Chekkit Invites 2; SHARED COMPANY-WIDE | Claude Forfeiture Winback Comparison; SHARED COMPANY-WIDE | Claude Top Loan Customers; SHARED COMPANY-WIDE | Claude Top Sales Customers; SHARED GLOBALLY | Company Branded Site Customers; Constant Contact; SHARED GLOBALLY | Core Customer Identifiers for Marketing; SHARED GLOBALLY | Customer Engagement and Behavior; SHARED GLOBALLY | Customer Search (Last Time In); SHARED GLOBALLY | Customers First Time In; SHARED GLOBALLY | Customers with Buy Tickets; SHARED GLOBALLY | Customers with Loan & Buy tickets; SHARED GLOBALLY | Customers with Loan Tickets; SHARED GLOBALLY | Customers with Sale Transactions; SHARED GLOBALLY | Demographics Report; SHARED GLOBALLY | eBay Customers; SHARED COMPANY-WIDE | Email Monthly Pull; SHARED GLOBALLY | In-Store Customers; SHARED GLOBALLY | Loan/Buy History for Marketing; SHARED COMPANY-WIDE | Monthly Email Pull; SHARED GLOBALLY | Sales History for Marketing Report; SHARED GLOBALLY | SMS ready customers for AUTO kind for 1 year; SHARED GLOBALLY | Transactions Done (Marketing Messages); SHARED GLOBALLY | UsedGuns.com Customers; SHARED GLOBALLY | Vendor Search

#### Customers > Mark Customer Contacted
_key `S_Customers__Mark_Customer_Contacted` · captured 2026-09-30 22:53:12 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Customers__Mark_Customer_Contacted.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Custom Reports; Print List; Mark Customer Contacted; Send Mobile Message; Schedule Mobile Event; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Done; Review Duplicates; 28; Custom Reports; Print List; Mark Customer Contacted; Send Mobile Message; Schedule Mobile Event; Layouts; Name; Saved Layouts; Delete Layout; Save; Show summary panel; Name `PART_Content`; Phone `PART_Content`; Address `PART_Content`; E-Mail `PART_Content`; Total Sales `PART_Content`; Total Buys `PART_Content`; Total Loans `PART_Content`; MobilePawn `PART_Content`; SMS `PART_Content`
- **Options:** Review Duplicates `btnReviewDuplicates`
- **Fields:** BravoMaskedTextBox; BravoComboBox
- **Checkboxes:** Show summary panel
- **Grid columns:** FullName; PublicPhone; FullAddress; Email; TotalSales; TotalBuys; TotalLoans; BuyaMobileColumnSortOrder; SmsAbilityStatus


#### Customers > Schedule Mobile Event
_key `S_Customers__Schedule_Mobile_Event` · captured 2026-09-30 22:53:39 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Customers__Schedule_Mobile_Event.png`

- **Labels:** Add new event; Edit Recurrence; Recurring event sent to all mobile enabled customers; Store.SMSFriendlyName; Store.Phone; Customer.FirstName; Customer.LastName; Birthday; Store Anniversary; Loan Courtesy Reminder; Make Recurring; Single Loan Courtesy Reminder; Multiple Loan Courtesy Reminder; Layaway Notice; Single Layaway Notice; Multiple Layaway Notice; Loan Past Due (Due Date); Single Loan Past Due Reminder; Multiple Loan Past Due Reminder; MobilePawn Layaway Notice; Ok; Cancel; Done; Review Duplicates; 28; Custom Reports; Print List; Mark Customer Contacted; Send Mobile Message; Schedule Mobile Event; Layouts; Name; Saved Layouts; Delete Layout; Save; Show summary panel; Name `PART_Content`; Phone `PART_Content`; Address `PART_Content`; E-Mail `PART_Content` … +5 more
- **Fields:** BravoMaskedTextBox; BravoComboBox; BravoSpinEdit; BravoSpinEdit `PART_Editor`
- **Buttons:** Store.SMSFriendlyName; Store.Phone; Customer.FirstName; Customer.LastName; (no label) `PART_SpinUpButton`; (no label) `PART_SpinDownButton`; Single Loan Courtesy Reminder; Multiple Loan Courtesy Reminder; Single Layaway Notice; Multiple Layaway Notice; Single Loan Past Due Reminder; Multiple Loan Past Due Reminder; Cancel; (no label) `HeaderSite`; Done `btnDone`; Custom Reports; Print List; Mark Customer Contacted; Send Mobile Message; Schedule Mobile Event; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Options:** Review Duplicates `btnReviewDuplicates`
- **Checkboxes:** Show summary panel
- **Grid columns:** FullName; PublicPhone; FullAddress; Email; TotalSales; TotalBuys; TotalLoans; BuyaMobileColumnSortOrder; SmsAbilityStatus


- **Action controls recorded but deliberately NOT clicked (write/transaction actions):** Done; Print List; Send Mobile Message; Delete Layout; Save; Review Duplicates; Show summary panel

### Module: Inventory
_key `M_Inventory` · captured 2026-09-30 22:30:31 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/M_Inventory.png`

- **Labels:** Inventory waiting to be reviewed and priced for sale; Done; Print Tags; 46; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; No Image Available; Number; Quality; Tag Description; Location; Tag Type; Web; MSRP; Price; Cost; Sale Price; Quantity; Max Discount; Manufacturer/Model; Serial Number; Price Guide Report; Edit Item … +16 more
- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Print Tags; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; (no label) `PageUp`; (no label) `PageDown`; Price Guide Report; Edit Item; Item Detail; Edit; Accept; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`; Delete Layout; Save
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox; BravoMaskedTextBox `bmtbCost`; Quantity; SpinEdit
- **Grid columns:** InventoryNumber; StatusCode; Category; UnpricedItemType; Description; ItemCost; StatusDate
- **Checkboxes:** Show summary panel

#### Inventory > Accept
_key `S_Inventory__Accept` · captured 2026-09-30 22:47:19 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Accept.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Print Tags; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; Price Guide Report; Edit Item; Item Detail; Edit; Accept; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`; Delete Layout; Save
- **Labels:** Done; Print Tags; 46; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; No Image Available; Number; Quality; Tag Description; Location; Tag Type; Web; MSRP; Price; Cost; Sale Price; Quantity; Max Discount; Manufacturer/Model; Serial Number; Price Guide Report; Edit Item; Item Detail … +15 more
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox; BravoMaskedTextBox `bmtbCost`; Quantity; SpinEdit
- **Grid columns:** InventoryNumber; StatusCode; Category; UnpricedItemType; Description; ItemCost; StatusDate
- **Checkboxes:** Show summary panel


#### Inventory > Combine
_key `S_Inventory__Combine` · captured 2026-09-30 22:46:26 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Combine.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Print Tags; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; Price Guide Report; Edit Item; Item Detail; Edit; Accept; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`; Delete Layout; Save
- **Labels:** Done; Print Tags; 46; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; No Image Available; Number; Quality; Tag Description; Location; Tag Type; Web; MSRP; Price; Cost; Sale Price; Quantity; Max Discount; Manufacturer/Model; Serial Number; Price Guide Report; Edit Item; Item Detail … +15 more
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox; BravoMaskedTextBox `bmtbCost`; Quantity; SpinEdit
- **Grid columns:** InventoryNumber; StatusCode; Category; UnpricedItemType; Description; ItemCost; StatusDate
- **Checkboxes:** Show summary panel


#### Inventory > Confiscate Item
_key `S_Inventory__Confiscate_Item` · captured 2026-09-30 22:43:10 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Confiscate_Item.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Print Tags; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; (no label) `PageUp`; (no label) `PageDown`; Price Guide Report; Edit Item; Item Detail; Edit; Accept; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`; Delete Layout; Save
- **Labels:** Done; Print Tags; 46; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; No Image Available; Number; Quality; Tag Description; Location; Tag Type; Web; MSRP; Price; Cost; Sale Price; Quantity; Max Discount; Manufacturer/Model; Serial Number; Price Guide Report; Edit Item; Item Detail … +15 more
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox; BravoMaskedTextBox `bmtbCost`; Quantity; SpinEdit
- **Grid columns:** InventoryNumber; StatusCode; Category; UnpricedItemType; Description; ItemCost; StatusDate
- **Checkboxes:** Show summary panel


#### Inventory > Convert To SKU
_key `S_Inventory__Convert_To_SKU` · captured 2026-09-30 22:44:39 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Convert_To_SKU.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Print Tags; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; (no label) `PageUp`; (no label) `PageDown`; Price Guide Report; Edit Item; Item Detail; Edit; Accept; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`; Delete Layout; Save
- **Labels:** Done; Print Tags; 46; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; No Image Available; Number; Quality; Tag Description; Location; Tag Type; Web; MSRP; Price; Cost; Sale Price; Quantity; Max Discount; Manufacturer/Model; Serial Number; Price Guide Report; Edit Item; Item Detail … +15 more
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox; BravoMaskedTextBox `bmtbCost`; Quantity; SpinEdit
- **Grid columns:** InventoryNumber; StatusCode; Category; UnpricedItemType; Description; ItemCost; StatusDate
- **Checkboxes:** Show summary panel


#### Inventory > Cost Adjustment
_key `S_Inventory__Cost_Adjustment` · captured 2026-09-30 22:42:16 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Cost_Adjustment.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Print Tags; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; (no label) `PageUp`; (no label) `PageDown`; Price Guide Report; Edit Item; Item Detail; Edit; Accept; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`; Delete Layout; Save
- **Labels:** Done; Print Tags; 46; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; No Image Available; Number; Quality; Tag Description; Location; Tag Type; Web; MSRP; Price; Cost; Sale Price; Quantity; Max Discount; Manufacturer/Model; Serial Number; Price Guide Report; Edit Item; Item Detail … +15 more
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox; BravoMaskedTextBox `bmtbCost`; Quantity; SpinEdit
- **Grid columns:** InventoryNumber; StatusCode; Category; UnpricedItemType; Description; ItemCost; StatusDate
- **Checkboxes:** Show summary panel


#### Inventory > Custom Reports
_key `S_Inventory__Custom_Reports` · captured 2026-09-30 22:40:29 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Custom_Reports.png`

- **Fields:** BravoMaskedTextBox `BoxReportName`; BravoComboBox `BoxColumns`; BravoComboBox `BoxIsShared`; BravoComboBox; BravoComboBox `BoxSelectCriteria`; BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoMaskedTextBox `bmtbCost`; Quantity; SpinEdit
- **Buttons:** Save; New Report; Delete Report; Cancel; (no label) `HeaderSite`; Done `btnDone`; Print Tags; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; Price Guide Report; Edit Item; Item Detail; Edit; Accept; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`; Delete Layout
- **Labels:** Save; Initial rows; Sort By; New Report; Delete Report; Ok; Cancel; Done; Print Tags; 46; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; No Image Available; Number; Quality; Tag Description; Location; Tag Type; Web; MSRP; Price; Cost; Sale Price … +21 more
- **Grid columns:** InventoryNumber; StatusCode; Category; UnpricedItemType; Description; ItemCost; StatusDate
- **Checkboxes:** Show summary panel

- **Columns available (0):** (none captured)
- **Filter criteria available (54):** Additional Information; Age; Authentic-Diamond Jewelry; Authentic-Stone Jewelry; Barcode; Buya Delivery Amount; Category; Chain Length; Cost; Customer; Date to Inventory; Description; eBay Delivery Option; Firearm Action; Firearm Caliber; For Sale Online; Full Description; Image Kind; Inventory Age; Inventory Number; Invoice #; Last Priced By; Last Sold By; Last Sold Price; Last Sold To; Last Ticket Number; Location; Metal Purity; Metal Type/Color; Metal Weight; Mfg/Model; Owner Applied Number; Price; Price Time; Quality; Reference Number; Sale Price; Serial Number; SKU; SKU Number; SKU Quantity; Source; Split From; Status; Status Date; Store; Total Diamond Size; Total Jewelry Weight; Total Stone Size; Type; Vendor; Web Delivery Option; Web Platform; Web Price
- **Saved reports (0):** (none captured)

#### Inventory > Inventory Markdown
_key `S_Inventory__Inventory_Markdown` · captured 2026-09-30 22:45:05 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Inventory_Markdown.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Print Tags; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; (no label) `PageUp`; (no label) `PageDown`; Price Guide Report; Edit Item; Item Detail; Edit; Accept; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`; Delete Layout; Save
- **Labels:** Done; Print Tags; 46; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; No Image Available; Number; Quality; Tag Description; Location; Tag Type; Web; MSRP; Price; Cost; Sale Price; Quantity; Max Discount; Manufacturer/Model; Serial Number; Price Guide Report; Edit Item; Item Detail … +15 more
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox; BravoMaskedTextBox `bmtbCost`; Quantity; SpinEdit
- **Grid columns:** InventoryNumber; StatusCode; Category; UnpricedItemType; Description; ItemCost; StatusDate
- **Checkboxes:** Show summary panel


#### Inventory > Item Detail
_key `S_Inventory__Item_Detail` · captured 2026-09-30 22:46:52 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Item_Detail.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Print Tags; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; Price Guide Report; Edit Item; Item Detail; Edit; Accept; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`; Delete Layout; Save
- **Labels:** Done; Print Tags; 46; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; No Image Available; Number; Quality; Tag Description; Location; Tag Type; Web; MSRP; Price; Cost; Sale Price; Quantity; Max Discount; Manufacturer/Model; Serial Number; Price Guide Report; Edit Item; Item Detail … +15 more
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox; BravoMaskedTextBox `bmtbCost`; Quantity; SpinEdit
- **Grid columns:** InventoryNumber; StatusCode; Category; UnpricedItemType; Description; ItemCost; StatusDate
- **Checkboxes:** Show summary panel


#### Inventory > Item History
_key `S_Inventory__Item_History` · captured 2026-09-30 22:41:50 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Item_History.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Print Tags; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; (no label) `PageUp`; (no label) `PageDown`; Price Guide Report; Edit Item; Item Detail; Edit; Accept; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`; Delete Layout; Save
- **Labels:** Done; Print Tags; 46; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; No Image Available; Number; Quality; Tag Description; Location; Tag Type; Web; MSRP; Price; Cost; Sale Price; Quantity; Max Discount; Manufacturer/Model; Serial Number; Price Guide Report; Edit Item; Item Detail … +15 more
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox; BravoMaskedTextBox `bmtbCost`; Quantity; SpinEdit
- **Grid columns:** InventoryNumber; StatusCode; Category; UnpricedItemType; Description; ItemCost; StatusDate
- **Checkboxes:** Show summary panel


#### Inventory > Lost or Damaged
_key `S_Inventory__Lost_or_Damaged` · captured 2026-09-30 22:42:43 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Lost_or_Damaged.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Print Tags; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; (no label) `PageUp`; (no label) `PageDown`; Price Guide Report; Edit Item; Item Detail; Edit; Accept; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`; Delete Layout; Save
- **Labels:** Done; Print Tags; 46; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; No Image Available; Number; Quality; Tag Description; Location; Tag Type; Web; MSRP; Price; Cost; Sale Price; Quantity; Max Discount; Manufacturer/Model; Serial Number; Price Guide Report; Edit Item; Item Detail … +15 more
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox; BravoMaskedTextBox `bmtbCost`; Quantity; SpinEdit
- **Grid columns:** InventoryNumber; StatusCode; Category; UnpricedItemType; Description; ItemCost; StatusDate
- **Checkboxes:** Show summary panel


#### Inventory > Physical Inventory Audit
_key `S_Inventory__Physical_Inventory_Audit` · captured 2026-09-30 22:39:59 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Physical_Inventory_Audit.png`

- **Labels:** Adjust the snapshot due to daily activity; Done; Add New Session; View Session; Cancel Session; Reconcile; Close Session; Show Prior Sessions; Print List; Adjust Snapshot; Refresh; Name `PART_Content`; Status `PART_Content`; Date `PART_Content`; Created By `PART_Content`; Created Date `PART_Content`
- **Buttons:** Done `btnDone`; Add New Session; View Session; Cancel Session; Reconcile; Close Session; Show Prior Sessions; Print List; Adjust Snapshot; Refresh
- **Grid columns:** Entity.Name; Entity.StatusCode; Entity.StatusDate; Entity.Creator.DisplayAlias; Entity.CreateDate


#### Inventory > Place on eBay Auction
_key `S_Inventory__Place_on_eBay_Auction` · captured 2026-09-30 22:43:37 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Place_on_eBay_Auction.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Print Tags; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; (no label) `PageUp`; (no label) `PageDown`; Price Guide Report; Edit Item; Item Detail; Edit; Accept; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`; Delete Layout; Save
- **Labels:** Done; Print Tags; 46; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; No Image Available; Number; Quality; Tag Description; Location; Tag Type; Web; MSRP; Price; Cost; Sale Price; Quantity; Max Discount; Manufacturer/Model; Serial Number; Price Guide Report; Edit Item; Item Detail … +15 more
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox; BravoMaskedTextBox `bmtbCost`; Quantity; SpinEdit
- **Grid columns:** InventoryNumber; StatusCode; Category; UnpricedItemType; Description; ItemCost; StatusDate
- **Checkboxes:** Show summary panel


#### Inventory > Police Hold
_key `S_Inventory__Police_Hold` · captured 2026-09-30 22:45:32 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Police_Hold.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Print Tags; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; (no label) `PageUp`; (no label) `PageDown`; Price Guide Report; Edit Item; Item Detail; Edit; Accept; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`; Delete Layout; Save
- **Labels:** Done; Print Tags; 46; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; No Image Available; Number; Quality; Tag Description; Location; Tag Type; Web; MSRP; Price; Cost; Sale Price; Quantity; Max Discount; Manufacturer/Model; Serial Number; Price Guide Report; Edit Item; Item Detail … +15 more
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox; BravoMaskedTextBox `bmtbCost`; Quantity; SpinEdit
- **Grid columns:** InventoryNumber; StatusCode; Category; UnpricedItemType; Description; ItemCost; StatusDate
- **Checkboxes:** Show summary panel


#### Inventory > Product Lead Gen
_key `S_Inventory__Product_Lead_Gen` · captured 2026-09-30 22:45:58 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Product_Lead_Gen.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Print Tags; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; Price Guide Report; Edit Item; Item Detail; Edit; Accept; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`; Delete Layout; Save
- **Labels:** Done; Print Tags; 46; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; No Image Available; Number; Quality; Tag Description; Location; Tag Type; Web; MSRP; Price; Cost; Sale Price; Quantity; Max Discount; Manufacturer/Model; Serial Number; Price Guide Report; Edit Item; Item Detail … +15 more
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox; BravoMaskedTextBox `bmtbCost`; Quantity; SpinEdit
- **Grid columns:** InventoryNumber; StatusCode; Category; UnpricedItemType; Description; ItemCost; StatusDate
- **Checkboxes:** Show summary panel


#### Inventory > Recombine Item
_key `S_Inventory__Recombine_Item` · captured 2026-09-30 22:44:13 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Recombine_Item.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Print Tags; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; (no label) `PageUp`; (no label) `PageDown`; Price Guide Report; Edit Item; Item Detail; Edit; Accept; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`; Delete Layout; Save
- **Labels:** Done; Print Tags; 46; Scrap Refining Process; Stock Management; Print List; Transfer Inventory; Physical Inventory Audit; Custom Reports; Item History; Cost Adjustment; Lost or Damaged; Write off Item; Confiscate Item; Place on eBay Auction; Recombine Item; Convert To SKU; Inventory Markdown; Police Hold; Product Lead Gen; Combine; Process; No Image Available; Number; Quality; Tag Description; Location; Tag Type; Web; MSRP; Price; Cost; Sale Price; Quantity; Max Discount; Manufacturer/Model; Serial Number; Price Guide Report; Edit Item; Item Detail … +15 more
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox; BravoMaskedTextBox `bmtbCost`; Quantity; SpinEdit
- **Grid columns:** InventoryNumber; StatusCode; Category; UnpricedItemType; Description; ItemCost; StatusDate
- **Checkboxes:** Show summary panel


#### Inventory > Stock Management
_key `S_Inventory__Stock_Management` · captured 2026-09-30 22:39:28 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Inventory__Stock_Management.png`

- **Labels:** Print or save data shown in the grid; Done; Add Receiving; Edit Receiving; Print Receiving; Print List; Custom Reports; SKU Levels; Number:; Order Date; Shipping Terms; Payment Terms; Ordered Date; Expected Date; Shipping Note; General Note; Total Qty; Total Cost; Shipping; Other (+/-); Discount; Tax; Pre-Payment; Total; Invoice Number; Invoice Date; Vendor View; Filter by:; Items:  50; Layouts; Name; Saved Layouts; Delete Layout; Save; Show summary panel; Number `PART_Content`; Vendor `PART_Content`; Status `PART_Content`; Status Date `PART_Content`; Created By `PART_Content` … +2 more
- **Buttons:** Done `btnDone`; Add Receiving; Edit Receiving; Print Receiving; Print List; Custom Reports; SKU Levels; Vendor View; (no label) `HeaderSite`; Delete Layout; Save; Show more `ViewNextButton`
- **Fields:** BravoMaskedTextBox; BravoComboBox
- **Tabs:** (no label) `BravoTabItem`
- **Checkboxes:** Show summary panel
- **Grid columns:** Number; Customer.BusinessName; StatusCode; DisplayStatusDate; Employee.DisplayAlias


- **Action controls recorded but deliberately NOT clicked (write/transaction actions):** Done; Print Tags; Scrap Refining Process; Print List; Transfer Inventory; Write off Item; Process; Price Guide Report; Edit Item; Edit; Delete Layout; Save; Show summary panel

### Module: Layaways
_key `M_Layaways` · captured 2026-09-30 22:31:20 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/M_Layaways.png`

- **Labels:** Past Payment Due Date; Cancel; Save; All Active; Contacted But No Activity; No Payment in 30 days; Review Pending Changes; Custom Reports; No Image Available; Layaway Number:; Tag Description:; Location:; Item Number:; Sale Price:; Tax:; Layaway Amount:; Balance:; Quantity:; Term:; Payment Promise:; Start Date:; Due Date:; Last Payment:; Next Due:; Customer:; Last Contact for this layaway:; Notes; Price Guide; Customer View; Layouts; Name; Saved Layouts; Delete Layout; Show summary panel; Layaway Number `PART_Content`; Status `PART_Content`; Age `PART_Content`; Last Payment `PART_Content`; Next Due `PART_Content`; Due Date `PART_Content` … +5 more
- **Buttons:** (no label) `HeaderSite`; Cancel `btnCancel`; Save `btnSave`; Custom Reports; Price Guide; Customer View; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Options:** Layaways Overdue; Past Payment Due Date; All Active; Contacted But No Activity; No Payment in 30 days; Review Pending Changes; Locate Layaways
- **Fields:** BravoComboBox `EdtLocation`; BravoComboBox `PART_Editor`; BravoMaskedTextBox; BravoComboBox
- **Checkboxes:** Show summary panel
- **Grid columns:** LayawayNumber; Status; Age; LastPayment; NextDue; DueDate; Customer; LastContact; Quantity; BuyaMobileColumnSortOrder; SmsAbilityStatus

#### Layaways > Custom Reports
_key `S_Layaways__Custom_Reports` · captured 2026-09-30 22:50:23 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Layaways__Custom_Reports.png`

- **Fields:** BravoMaskedTextBox `BoxReportName`; BravoComboBox `BoxColumns`; BravoComboBox `BoxIsShared`; BravoComboBox; BravoComboBox `BoxSelectCriteria`; BravoComboBox `EdtLocation`; BravoComboBox `PART_Editor`; BravoMaskedTextBox
- **Buttons:** Save; (no label) `ButtonRemove`; New Report; Delete Report; Cancel; (no label) `HeaderSite`; Cancel `btnCancel`; Save `btnSave`; Custom Reports; Price Guide; Customer View; Delete Layout; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Save; Max rows; Active Layaways; New Report; Delete Report; Ok; Cancel; Past Payment Due Date; All Active; Contacted But No Activity; No Payment in 30 days; Review Pending Changes; Custom Reports; No Image Available; Layaway Number:; Tag Description:; Location:; Item Number:; Sale Price:; Tax:; Layaway Amount:; Balance:; Quantity:; Term:; Payment Promise:; Start Date:; Due Date:; Last Payment:; Next Due:; Customer:; Last Contact for this layaway:; Notes; Price Guide; Customer View; Layouts; Name; Saved Layouts; Delete Layout; Show summary panel; Layaway Number `PART_Content` … +10 more
- **Options:** Layaways Overdue; Past Payment Due Date; All Active; Contacted But No Activity; No Payment in 30 days; Review Pending Changes; Locate Layaways
- **Checkboxes:** Show summary panel
- **Grid columns:** LayawayNumber; Status; Age; LastPayment; NextDue; DueDate; Customer; LastContact; Quantity; BuyaMobileColumnSortOrder; SmsAbilityStatus

- **Columns available (0):** (none captured)
- **Filter criteria available (33):** Age; Amount; Associate; Balance Due; Category; Chain Length; Commission Associates; Customer; Due Date; Firearm Action; Firearm Caliber; First Payment Due; Image Kind; Inventory Age; Item Cost; Item Number; Kind; Last Contact; Last Payment Date; Layaway Number; Location; Mfg/Model; MobilePawn Activation Date; Needs Location; Next Due; SKU; SKU Quantity; Start Date; Status; Status Date; Tag Description; Total Jewelry Weight; Total Paid
- **Saved reports (0):** (none captured)

#### Layaways > Customer View
_key `S_Layaways__Customer_View` · captured 2026-09-30 22:51:25 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Layaways__Customer_View.png`

- **Buttons:** (no label) `HeaderSite`; Cancel `btnCancel`; Save `btnSave`; Custom Reports; Price Guide; Customer View; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Cancel; Save; Past Payment Due Date; All Active; Contacted But No Activity; No Payment in 30 days; Review Pending Changes; Custom Reports; No Image Available; Layaway Number:; Tag Description:; Location:; Item Number:; Sale Price:; Tax:; Layaway Amount:; Balance:; Quantity:; Term:; Payment Promise:; Start Date:; Due Date:; Last Payment:; Next Due:; Customer:; Last Contact for this layaway:; Notes; Price Guide; Customer View; Layouts; Name; Saved Layouts; Delete Layout; Show summary panel; Layaway Number `PART_Content`; Status `PART_Content`; Age `PART_Content`; Last Payment `PART_Content`; Next Due `PART_Content`; Due Date `PART_Content` … +5 more
- **Options:** Layaways Overdue; Past Payment Due Date; All Active; Contacted But No Activity; No Payment in 30 days; Review Pending Changes; Locate Layaways
- **Fields:** BravoComboBox `EdtLocation`; BravoComboBox `PART_Editor`; BravoMaskedTextBox; BravoComboBox
- **Checkboxes:** Show summary panel
- **Grid columns:** LayawayNumber; Status; Age; LastPayment; NextDue; DueDate; Customer; LastContact; Quantity; BuyaMobileColumnSortOrder; SmsAbilityStatus


- **Action controls recorded but deliberately NOT clicked (write/transaction actions):** Cancel; Save; Price Guide; Delete Layout; Layaways Overdue; Past Payment Due Date; All Active; Contacted But No Activity; No Payment in 30 days; Review Pending Changes; Locate Layaways; Show summary panel

### Module: Loans/Buys
_key `M_Loans_Buys` · captured 2026-09-30 22:30:56 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/M_Loans_Buys.png`

- **Labels:** Loans on Notice; Cancel; Save; All Active; Contacted But No Activity; 221; Review Pending Changes; Pick Up; Custom Reports; View Police Export; Process; No Image Available; Number; Tag Description; Location; Amount; Qty; Manufacturer/Model; Serial Number; Price Guide Report; Notes; Item Detail; Customer View; Layouts; Name; Saved Layouts; Delete Layout; Show summary panel; Ticket Number `PART_Content`; Disposition `PART_Content`; Disposition Date `PART_Content`; Age `PART_Content`; Due Date `PART_Content`; Pull Date `PART_Content`; Customer `PART_Content`; Last Contact `PART_Content`; Create Date `PART_Content`; MobilePawn `PART_Content`; SMS `PART_Content`
- **Buttons:** (no label) `HeaderSite`; Cancel `btnCancel`; Save `btnSave`; Pick Up; Custom Reports `btnAdHoc`; View Police Export; Process; Price Guide Report; Item Detail; Customer View; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Options:** Loans To Expire; Send Loan Notice; Loans on Notice; Loans to Retag; All Active; Contacted But No Activity; Review Pending Changes; Locate Loan/Buy
- **Fields:** BravoMaskedTextBox; BravoComboBox
- **Checkboxes:** Show summary panel
- **Grid columns:** TicketNumber; Disposition; DispositionDate; Age; DueDate; PullDate; Customer; LastContact; PawnDate; BuyaMobileColumnSortOrder; SmsAbilityStatus

#### Loans/Buys > Custom Reports
_key `S_Loans_Buys__Custom_Reports` · captured 2026-09-30 22:48:13 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Loans_Buys__Custom_Reports.png`

- **Fields:** BravoMaskedTextBox `BoxReportName`; BravoComboBox `BoxColumns`; BravoComboBox `BoxIsShared`; BravoComboBox; BravoComboBox `BoxSelectCriteria`; BravoMaskedTextBox
- **Buttons:** Save; (no label) `ButtonRemove`; New Report; Delete Report; Cancel; (no label) `HeaderSite`; Cancel `btnCancel`; Save `btnSave`; Pick Up; Custom Reports `btnAdHoc`; View Police Export; Process; Price Guide Report; Item Detail; Customer View; Delete Layout; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Save; Initial rows; Sort By; Active Loans and Buys; New Report; Delete Report; Ok; Cancel; Loans on Notice; All Active; Contacted But No Activity; 221; Review Pending Changes; Pick Up; Custom Reports; View Police Export; Process; No Image Available; Number; Tag Description; Location; Amount; Qty; Manufacturer/Model; Serial Number; Price Guide Report; Notes; Item Detail; Customer View; Layouts; Name; Saved Layouts; Delete Layout; Show summary panel; Ticket Number `PART_Content`; Disposition `PART_Content`; Disposition Date `PART_Content`; Age `PART_Content`; Due Date `PART_Content`; Pull Date `PART_Content` … +5 more
- **Options:** Loans To Expire; Send Loan Notice; Loans on Notice; Loans to Retag; All Active; Contacted But No Activity; Review Pending Changes; Locate Loan/Buy
- **Checkboxes:** Show summary panel
- **Grid columns:** TicketNumber; Disposition; DispositionDate; Age; DueDate; PullDate; Customer; LastContact; PawnDate; BuyaMobileColumnSortOrder; SmsAbilityStatus

- **Columns available (10):** SHARED GLOBALLY | Specific Firearm, Search; SHARED GLOBALLY | Specific Firearm Search; SHARED GLOBALLY | Trade In View; SHARED GLOBALLY | Z-Bravo Regulation Escalation; SHARED GLOBALLY | Active Loan/Buys Summary; SHARED GLOBALLY | High Dollar Loan Demographic; SHARED COMPANY-WIDE | Claude Forfeiture Winback; SHARED COMPANY-WIDE | Full description and cost; SHARED COMPANY-WIDE | Pawn Walk; SHARED COMPANY-WIDE | FDP
- **Filter criteria available (39):** Age; Associate; Category; Chain Length; Create Date; Customer; Disposition; Disposition Date; Due Date; Firearm Action; Firearm Caliber; Image Kind; Last Contact; Last Mobile Courtesy Date; Last Notice Sent Date; Last Payment; Loan Amount; Location; Mfg/Model; MLA Relevant; MobilePawn Activation Date; Needs Location; Notice Date; Owner Applied Number; Past Due Age; Printed; Pull Date; Quality; Quantity; Requires Notice; Requires Retag; Serial Number; Status; Status Date; Tag Description; Ticket Amount; Ticket Kind; Ticket Number; Total Jewelry Weight
- **Saved reports (40):** <new report>; SHARED COMPANY-WIDE | 75 Days Past Due; SHARED GLOBALLY | Buy tickets by Amount; SHARED COMPANY-WIDE | Claude Buy Reviews; SHARED COMPANY-WIDE | Claude First Payment Default; SHARED COMPANY-WIDE | Claude Forfeiture Winback; SHARED COMPANY-WIDE | Claude Loan Portfolio 2026; SHARED COMPANY-WIDE | Claude Loan Reviews; SHARED COMPANY-WIDE | Claude Low Dollar Buys; SHARED COMPANY-WIDE | Claude Low Dollar Loans; SHARED COMPANY-WIDE | Claude Pawn Walks; SHARED GLOBALLY | Disposition by Date; SHARED GLOBALLY | Expired Loans now in Inventory; SHARED COMPANY-WIDE | jewelry; SHARED GLOBALLY | Loan Walk; SHARED GLOBALLY | Loan Walk (Expired); SHARED COMPANY-WIDE | Loan/Buy Review; SHARED GLOBALLY | Loans By Amount; SHARED COMPANY-WIDE | past 75 days; SHARED COMPANY-WIDE | Past due loans; Object_Layout: 00000000-0000-0000-0000-000000000000 (Detached); Object_Layout: a6a598a2-eca6-4f36-b41b-a0512a5a6267 (Unchanged); Object_Layout: e7afda30-1015-4f96-a0b9-36f15d1b6ef7 (Unchanged); Object_Layout: 87e0dcbd-5e1e-43ab-ad08-3663ae23b6f5 (Unchanged); Object_Layout: 5dd01dbf-fe16-4ca3-ab35-b6ae261a35eb (Unchanged); Object_Layout: 91e589c5-4cbe-476d-babd-922fcff31598 (Unchanged); Object_Layout: 087343ad-8cc9-4eb0-bcc2-3c9163204826 (Unchanged); Object_Layout: 13e772da-d7f5-4d8f-8eb8-662b24b2eafa (Unchanged); Object_Layout: e5fbedc9-d8a0-4093-8a3b-8643430404e1 (Unchanged); Object_Layout: 09fcba2c-6bf9-4c3c-a858-4abb0e276fe0 (Unchanged); Object_Layout: 9311fe9f-55a4-422f-aa1c-dd869548bd95 (Unchanged); Object_Layout: 350d7c5d-bf6b-46ac-b20b-ead4a2ff256a (Unchanged); Object_Layout: 3bb2db87-251b-4a5d-bc73-f2048f7ac4a8 (Unchanged); Object_Layout: 09356081-7d99-4b44-be17-f11e63999310 (Unchanged); Object_Layout: 1d1071f5-9998-422e-b4b4-a28e31f02e63 (Unchanged); Object_Layout: 6119fbf0-2e8b-479f-bd43-79899333a78c (Unchanged); Object_Layout: d1f16ac7-8317-4048-8f6d-51d8f7942bac (Unchanged); Object_Layout: 581351eb-7b9d-448e-9a56-9a5ac2dd196e (Unchanged); Object_Layout: f7f8fbee-bb3d-4cb8-9b0e-8c9ec4d3c760 (Unchanged); Object_Layout: 0d2af1f0-dd74-45ac-8994-7e69f4c2c9d6 (Unchanged)

#### Loans/Buys > Customer View
_key `S_Loans_Buys__Customer_View` · captured 2026-09-30 22:49:57 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Loans_Buys__Customer_View.png`

- **Buttons:** (no label) `HeaderSite`; Cancel `btnCancel`; Save `btnSave`; Pick Up; Custom Reports `btnAdHoc`; View Police Export; Process; Price Guide Report; Item Detail; Customer View; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Cancel; Save; Loans on Notice; All Active; Contacted But No Activity; 221; Review Pending Changes; Pick Up; Custom Reports; View Police Export; Process; No Image Available; Number; Tag Description; Location; Amount; Qty; Manufacturer/Model; Serial Number; Price Guide Report; Notes; Item Detail; Customer View; Layouts; Name; Saved Layouts; Delete Layout; Show summary panel; Ticket Number `PART_Content`; Disposition `PART_Content`; Disposition Date `PART_Content`; Age `PART_Content`; Due Date `PART_Content`; Pull Date `PART_Content`; Customer `PART_Content`; Last Contact `PART_Content`; Create Date `PART_Content`; MobilePawn `PART_Content`; SMS `PART_Content`
- **Options:** Loans To Expire; Send Loan Notice; Loans on Notice; Loans to Retag; All Active; Contacted But No Activity; Review Pending Changes; Locate Loan/Buy
- **Fields:** BravoMaskedTextBox; BravoComboBox
- **Checkboxes:** Show summary panel
- **Grid columns:** TicketNumber; Disposition; DispositionDate; Age; DueDate; PullDate; Customer; LastContact; PawnDate; BuyaMobileColumnSortOrder; SmsAbilityStatus


#### Loans/Buys > Item Detail
_key `S_Loans_Buys__Item_Detail` · captured 2026-09-30 22:49:31 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Loans_Buys__Item_Detail.png`

- **Buttons:** (no label) `HeaderSite`; Cancel `btnCancel`; Save `btnSave`; Pick Up; Custom Reports `btnAdHoc`; View Police Export; Process; Price Guide Report; Item Detail; Customer View; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Cancel; Save; Loans on Notice; All Active; Contacted But No Activity; 221; Review Pending Changes; Pick Up; Custom Reports; View Police Export; Process; No Image Available; Number; Tag Description; Location; Amount; Qty; Manufacturer/Model; Serial Number; Price Guide Report; Notes; Item Detail; Customer View; Layouts; Name; Saved Layouts; Delete Layout; Show summary panel; Ticket Number `PART_Content`; Disposition `PART_Content`; Disposition Date `PART_Content`; Age `PART_Content`; Due Date `PART_Content`; Pull Date `PART_Content`; Customer `PART_Content`; Last Contact `PART_Content`; Create Date `PART_Content`; MobilePawn `PART_Content`; SMS `PART_Content`
- **Options:** Loans To Expire; Send Loan Notice; Loans on Notice; Loans to Retag; All Active; Contacted But No Activity; Review Pending Changes; Locate Loan/Buy
- **Fields:** BravoMaskedTextBox; BravoComboBox
- **Checkboxes:** Show summary panel
- **Grid columns:** TicketNumber; Disposition; DispositionDate; Age; DueDate; PullDate; Customer; LastContact; PawnDate; BuyaMobileColumnSortOrder; SmsAbilityStatus


#### Loans/Buys > Pick Up
_key `S_Loans_Buys__Pick_Up` · captured 2026-09-30 22:47:45 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/S_Loans_Buys__Pick_Up.png`

- **Buttons:** (no label) `HeaderSite`; Cancel `btnCancel`; Save `btnSave`; Pick Up; Custom Reports `btnAdHoc`; View Police Export; Process; Price Guide Report; Item Detail; Customer View; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Cancel; Save; Loans on Notice; All Active; Contacted But No Activity; 221; Review Pending Changes; Pick Up; Custom Reports; View Police Export; Process; No Image Available; Number; Tag Description; Location; Amount; Qty; Manufacturer/Model; Serial Number; Price Guide Report; Notes; Item Detail; Customer View; Layouts; Name; Saved Layouts; Delete Layout; Show summary panel; Ticket Number `PART_Content`; Disposition `PART_Content`; Disposition Date `PART_Content`; Age `PART_Content`; Due Date `PART_Content`; Pull Date `PART_Content`; Customer `PART_Content`; Last Contact `PART_Content`; Create Date `PART_Content`; MobilePawn `PART_Content`; SMS `PART_Content`
- **Options:** Loans To Expire; Send Loan Notice; Loans on Notice; Loans to Retag; All Active; Contacted But No Activity; Review Pending Changes; Locate Loan/Buy
- **Fields:** BravoMaskedTextBox; BravoComboBox
- **Checkboxes:** Show summary panel
- **Grid columns:** TicketNumber; Disposition; DispositionDate; Age; DueDate; PullDate; Customer; LastContact; PawnDate; BuyaMobileColumnSortOrder; SmsAbilityStatus


- **Action controls recorded but deliberately NOT clicked (write/transaction actions):** Cancel; Save; View Police Export; Process; Price Guide Report; Delete Layout; Loans To Expire; Send Loan Notice; Loans on Notice; Loans to Retag; All Active; Contacted But No Activity; Review Pending Changes; Locate Loan/Buy; Show summary panel

### Module: Lost or Damaged Items
_key `M_Lost_or_Damaged_Items` · captured 2026-09-30 22:33:47 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/M_Lost_or_Damaged_Items.png`

- **Buttons:** Cancel `btnCancel`; Save `btnSave`; Lost Stolen or Damaged Report; Item History Report; Write off Item; Confiscate Item; Import List
- **Labels:** Cancel; Save; Lost Stolen or Damaged Report; Item History Report; Write off Item; Confiscate Item; Import List; Event Number:; Status:; Create Date:; Note; Number `PART_Content`; Status `PART_Content`; Description `PART_Content`; Item Description; Cause / Reason; Resolution; Resolution Transaction Number
- **Fields:** BravoMaskedTextBox; BravoComboBox `bcbCauseReason`; BravoComboBox `ddResolution`
- **Grid columns:** Number; Status; Description

- **Action controls recorded but deliberately NOT clicked (write/transaction actions):** Cancel; Save; Write off Item; Import List

### Module: System Configuration
_key `M_System_Configuration` · captured 2026-09-30 22:34:13 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/M_System_Configuration.png`

- **Buttons:** Done `btnDone`; Add Employee; Agreements; Show inactive items; (no label) `Expander`; Edit; Browse...
- **Labels:** Done; Add Employee; Agreements; Show inactive items; VALPAW Company `txt`; Stores `txt`; CUL `txt`; HAR `txt`; LEX `txt`; ROA `txt`; WAY `txt`; Mobile Devices `txt`; Edit; Store Name; Print Code; Short Name; Street Address; Street Address 2; City; State/Province; Zip/Postal Code; Country; Logo; Browse...; County; Phone; Fax; GL Store Number; FFL Number; FFL Business Name; E-Mail Address; Latitude (+N -S); Longitude (-W +E); Region; VA REGION; Store Hours; Configured Tax Authorities; County - WAYNESBORO CITY, VA, US
- **Tabs:** ConfigInfoTab `BravoTabItemConfigInfoTab`; Configuration `BravoTabItem`; Payment Processors `BravoTabItem0`; Regulatory `BravoTabItem1`; Transaction `BravoTabItem2`; Storage Locations `BravoTabItem3`; Estimator `BravoTabItem4`; Calendar `BravoTabItem4`; Web `BravoTabItem0`; eBay `BravoTabItem1`
- **Fields:** BravoMaskedTextBox `txtName`; BravoMaskedTextBox `txtPrintCode`; BravoMaskedTextBox `txtShortName`; BravoMaskedTextBox; BravoMaskedTextBox `CityEditor`; BravoComboBox `StateSelector`; BravoMaskedTextBox `ZipCodeEditor`; BravoComboBox; BravoMaskedTextBox `CountyEditor`

- **Action controls recorded but deliberately NOT clicked (write/transaction actions):** Done; Add Employee; Agreements; Show inactive items; Edit; Browse...; Item: (ZTI.Bravo.Operations.Views.Items.ConfigTree.ConfigCompanyObject); Children: 2; Item: (ZTI.Bravo.Operations.Views.Items.ConfigTree.ConfigStoreObjectGroup); Children: 5; Item: (ZTI.Bravo.Operations.Views.Items.ConfigTree.ConfigStoreObject); Children: 2; Item: (ZTI.Bravo.Operations.Views.Items.ConfigTree.ConfigMobileDeviceObjectGroup); Children: 1

### Module: Transactions
_key `M_Transactions` · captured 2026-09-30 22:34:40 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/M_Transactions.png`

- **Buttons:** Cancel `btnCancel`; Save `btnSave`; Use Expected Values
- **Labels:** Cancel; Save; Use Expected Values; Employee; Open Amount; Previous Close Amount; Short Amount; Cash `PART_Content`; Count `PART_Content`; Amount `PART_Content`; Tender `PART_Content`; Expected `PART_Content`; Variance `PART_Content`; $0.00; $0.00 `overAmount`
- **Fields:** BravoMaskedTextBox `boxEmployee`; BravoMaskedTextBox `boxOpenCloseAmnt`; BravoMaskedTextBox
- **Grid columns:** Multiplier; Count; Amount; Tender.DisplayDescription; Expected; ActualCount; LocalizedActualAmount; OverShort

- **Action controls recorded but deliberately NOT clicked (write/transaction actions):** Cancel; Save

### Module: Void/View Transactions
_key `M_Void_View_Transactions` · captured 2026-09-30 22:32:06 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/M_Void_View_Transactions.png`

- **Buttons:** Done `btnDone`; View; Find Transaction; Print List; Custom Reports
- **Labels:** Done; View; Find Transaction; Print List; Custom Reports; Store; VALLEY PAWN - WAYNESBORO; Business Date; Workstation; Employee; Till Session; Transaction `PART_Content`; Time `PART_Content`; Alias `PART_Content`; Workstation `PART_Content`; Type `PART_Content`; Void `PART_Content`
- **Fields:** BravoDateEdit; BravoComboBox; TextEdit
- **Grid columns:** PrintNumber; RowData.Row.TxnEndTime; Session.Employee.DisplayAlias; Session.Workstation.Name; TenderTypeText

- **Action controls recorded but deliberately NOT clicked (write/transaction actions):** Done; Print List

### Module: Web Auctions
_key `M_Web_Auctions` · captured 2026-09-30 22:33:01 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/M_Web_Auctions.png`

- **Labels:** Auctions where the item was sold but the customer never paid; Done; Active; Unsold (Last 90 days); Sold - Awaiting Payment; Sold - Awaiting Shipment; Sold - Expired (Last 90 days); Ended Listings (Last 90 days); Closed (Last 90 days); Auctions with questions; Listing Errors (last 90 days); View Auction Item; View Auction on eBay; View Web Order; Cancel Auction; Relist Auction; View Related Auctions; Print List; Custom Reports; View eBay Errors; Active:; eBay; Buya; Layouts; Name; Saved Layouts; Delete Layout; Save; Show summary panel; Web Title `PART_Content`; Inventory Number `PART_Content`; Status `PART_Content`; Status Date `PART_Content`; Start Price `PART_Content`; Buy It Now Price `PART_Content`; Reserve Price `PART_Content`; Start Date `PART_Content`; End Date `PART_Content`; Time Left `PART_Content`; Winner `PART_Content`
- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; View Auction Item; View Auction on eBay; View Web Order; Cancel Auction; Relist Auction; View Related Auctions; Print List; Custom Reports; View eBay Errors; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Options:** Active; Unsold (Last 90 days); Sold - Awaiting Payment; Sold - Awaiting Shipment; Sold - Expired (Last 90 days); Ended Listings (Last 90 days); Closed (Last 90 days); Auctions with questions; Listing Errors (last 90 days); Ebay; Buya
- **Fields:** BravoMaskedTextBox; BravoComboBox
- **Checkboxes:** Show summary panel
- **Grid columns:** ItemMerch.WebDesc; ItemMerch.InventoryNumber; EBayListing.StatusCode; EBayListing.StatusDate; EBayListing.StartingPrice; EBayListing.BuyItNowPrice; EBayListing.ReservePrice; EBayListing.StartTime; EBayListing.EndTime; TimeLeft; EBayListing.Winner

- **Action controls recorded but deliberately NOT clicked (write/transaction actions):** Done; Cancel Auction; Print List; Delete Layout; Save; Active; Unsold (Last 90 days); Sold - Awaiting Payment; Sold - Awaiting Shipment; Sold - Expired (Last 90 days); Ended Listings (Last 90 days); Closed (Last 90 days); Auctions with questions; Listing Errors (last 90 days); Ebay; Buya; Show summary panel

### Module: eBay Listings
_key `M_eBay_Listings` · captured 2026-09-30 22:33:23 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/M_eBay_Listings.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Place on eBay; Relist; Don't Show; View Listing on eBay; Cancel; Print List; Custom Reports; Item History; Estimator; Item Detail; Price Guide; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Done; All Available; Can Be Relisted; Pending Review; All Active; Sold Awaiting Payment; Sold Awaiting Shipment; Ended Listings (Last 90 days); Closed (Last 90 days); Listings with Questions; Place on eBay; Relist; Don't Show; View Listing on eBay; Cancel; Print List; Custom Reports; Item History; No Image Available; Number; Quality; Tag Description; Price; Cost; Global Shipping; Category; eBay Category; Location; eBay Advanced Item Specifics; Estimator; Item Detail; Notes; Price Guide; Layouts; Name; Saved Layouts; Delete Layout; Save; Show summary panel; Status `PART_Content` … +3 more
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox
- **Checkboxes:** Show summary panel
- **Grid columns:** StatusCode; Category; WebSalePrice; TagDescription

- **Action controls recorded but deliberately NOT clicked (write/transaction actions):** Done; Cancel; Print List; Price Guide; Delete Layout; Save; ZTI.Bravo.EBayIntegration.Views.EBayListingManagementViewModel+EBayListingManagementFilterInfo; Show summary panel

### Module: eCommerce
_key `M_eCommerce` · captured 2026-09-30 22:32:32 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/M_eCommerce.png`

- **Labels:** Direct Store Payments that are Past Due; Done; Complete In-Store Pickup; Locate In-Store Pickup; Pending Web Fulfillments; Pending Web Transactions; Custom Reports; Print List; Item History; Print Order; Cancel Order; Mark Customer Contacted; Order Number; Order Date; Promise Date; Order Status; Shipping Method; Ship Complete; Sale Amount; Shipping Amount; Sales Tax Amount; Total Amount; Total Charged; Payment Method; Payment Contact; Shipping Information; Phone Number; Comments; Details; Web Item View; Customer View; Layouts; Name; Saved Layouts; Delete Layout; Save; Show summary panel; Order Source `PART_Content`; Order Number `PART_Content`; Customer `PART_Content` … +5 more
- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Custom Reports; Print List; Item History; Print Order; Cancel Order; Mark Customer Contacted; Details; Web Item View; Customer View; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Options:** Complete In-Store Pickup; Locate In-Store Pickup; Pending Web Fulfillments; Web Payment Settlement; Pending Web Transactions; Web Returns; Web Offers
- **Fields:** BravoMaskedTextBox; BravoDateEdit; BravoComboBox; (no label) `PART_Editor`
- **Checkboxes:** Show summary panel
- **Dropdowns:** SearchComboBox
- **Grid columns:** Web_Order.SourceName; Web_Order.PrintNumber; Web_Order.Customer.FullName; Web_Order.OrderTime.Date; Item_Merch.InventoryNumber; SaleAmt; Web_Order.AgeHours; Item_Merch.Location.Name; Web_Order.FraudFlag; Web_Order_Item.Web_Order.SourceName; PrintNumber; Customer.FullName; RmaTime.Date; StatusCode; TotalAmt; Item_Merch.TagDesc; ResponseCode; OfferTime.Date; Item_Merch.ItemCost; Item_Merch.ItemPrice; OfferAmt; DiscountPct; AgeHours

- **Action controls recorded but deliberately NOT clicked (write/transaction actions):** Done; Print List; Print Order; Cancel Order; Delete Layout; Save; Complete In-Store Pickup; Locate In-Store Pickup; Pending Web Fulfillments; Web Payment Settlement; Pending Web Transactions; Web Returns; Web Offers; Show summary panel

## Reports

All reports (0): 

## Dashboard task tiles

### Dashboard tile: Layaways Overdue
_key `T_Layaways_Overdue` · captured 2026-09-30 22:36:05 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/T_Layaways_Overdue.png`

- **Buttons:** (no label) `HeaderSite`; Cancel `btnCancel`; Save `btnSave`; Layaway History; Layaway Journal; Mark Customer Contacted; Create Notice; Send Mobile Notice; Send Mobile Message; Activate MobilePawn; Custom Reports; Print List; Print Call List; Expire Layaway; Reprint Label; Expire All; Process; (no label) `PART_MoveFirstButton`; (no label) `PART_MovePreviousButton`; (no label) `PART_MoveNextButton`; (no label) `PART_MoveLastButton`; Price Guide; Customer View; Delete Layout; Save; FilterButton; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Cancel; Save; Past Payment Due Date; All Active; Contacted But No Activity; No Payment in 30 days; Review Pending Changes; Layaway History; Layaway Journal; Mark Customer Contacted; Create Notice; Send Mobile Notice; Send Mobile Message; Activate MobilePawn; Custom Reports; Print List; Print Call List; Expire Layaway; Reprint Label; Expire All; Process; Actual; Stock; Layaway Number:; VAP00060841-02; Tag Description:; APPLE LAPTOP MACBOOK AIR 13-INCH; Location:; Item Number:; VAP015710; Sale Price:; $400.00; Tax:; $21.20; Layaway Amount:; $421.20; Balance:; $291.20; Quantity:; Term: … +34 more
- **Options:** Layaways Overdue; Past Payment Due Date; All Active; Contacted But No Activity; No Payment in 30 days; Review Pending Changes; Locate Layaways
- **Fields:** BravoComboBox `EdtLocation`; BravoComboBox `PART_Editor`; BravoMaskedTextBox; BravoComboBox; TextEdit
- **Checkboxes:** Show summary panel
- **Grid columns:** LayawayNumber; Status; LastPayment; DueDate; Customer; LastContact; Age; PullDate; BuyaMobileColumnSortOrder; SmsAbilityStatus
- **Dropdowns:** FilterDropDown

### Dashboard tile: Loans To Expire
_key `T_Loans_To_Expire` · captured 2026-09-30 22:36:51 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/T_Loans_To_Expire.png`

- **Buttons:** (no label) `HeaderSite`; Cancel `btnCancel`; Save `btnSave`; Pick Up; Custom Reports `btnAdHoc`; Print List; Loan History; Loan Journal; Mark Customer Contacted; Send Mobile Courtesy Reminder; Send Mobile Message; Expire Loan `btnExpireLoan`; Place on Hold `btnPlaceOnHold`; Expire All; Reprint; Print Label; View Police Export; Lost or Damaged `btnLostOrDamaged`; Calculate Amount Due `btnCalculateAmntDue`; Process; (no label) `PART_MoveFirstButton`; (no label) `PART_MovePreviousButton`; (no label) `PART_MoveNextButton`; (no label) `PART_MoveLastButton`; Price Guide Report; Item Detail; Customer View; Delete Layout; Save; FilterButton; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Cancel; Save; Loans on Notice; All Active; Contacted But No Activity; 221; Review Pending Changes; Pick Up; Custom Reports; Print List; Loan History; Loan Journal; Mark Customer Contacted; Send Mobile Courtesy Reminder; Send Mobile Message; Expire Loan; Place on Hold; Expire All; Reprint; Print Label; View Police Export; Lost or Damaged; Calculate Amount Due; Process; Actual; Stock; Number; Tag Description; Location; Amount; Qty; Manufacturer/Model; Customer:; SABRINA DENISE PATTERSON; Last Contact for this ticket:; By MOBILEPAWN MESSAGE on 9/25/2026; Price Guide Report; Notes; Item Detail; Customer View … +16 more
- **Options:** Loans To Expire; Send Loan Notice; Loans on Notice; Loans to Retag; All Active; Contacted But No Activity; Review Pending Changes; Locate Loan/Buy
- **Fields:** BravoMaskedTextBox; BravoComboBox `EdtLocation`; BravoComboBox `PART_Editor`; BravoComboBox; TextEdit; TextEdit `PART_Editor`
- **Checkboxes:** Show summary panel
- **Grid columns:** TicketNumber; Disposition; DispositionDate; DueDate; PullDate; Customer; LastContact; Age; BuyaMobileColumnSortOrder; SmsAbilityStatus
- **Dropdowns:** FilterDropDown

### Dashboard tile: Locate Layaways
_key `T_Locate_Layaways` · captured 2026-09-30 22:35:38 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/T_Locate_Layaways.png`

- **Labels:** A1; A2; A3; A4; A5; A6; A7; A8; A9; A10; Cancel; Save; Past Payment Due Date; All Active; Contacted But No Activity; No Payment in 30 days; Review Pending Changes; Layaway History; Layaway Journal; Mark Customer Contacted; Send Mobile Message; Activate MobilePawn; Custom Reports; Print List; Print Call List; Expire Layaway; Reprint Label; Process; Actual; Stock; Layaway Number:; VAP00075511-01; Tag Description:; HISENSE FLAT PANEL TV 58R6E3; Location:; Item Number:; VAP032275; Sale Price:; $139.99; Tax: … +40 more
- **Buttons:** (no label) `HeaderSite`; Cancel `btnCancel`; Save `btnSave`; Layaway History; Layaway Journal; Mark Customer Contacted; Send Mobile Message; Activate MobilePawn; Custom Reports; Print List; Print Call List; Expire Layaway; Reprint Label; Process; (no label) `PART_MoveFirstButton`; (no label) `PART_MovePreviousButton`; (no label) `PART_MoveNextButton`; (no label) `PART_MoveLastButton`; Price Guide; Customer View; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Options:** Layaways Overdue; Past Payment Due Date; All Active; Contacted But No Activity; No Payment in 30 days; Review Pending Changes; Locate Layaways
- **Fields:** BravoComboBox `EdtLocation`; BravoComboBox `PART_Editor`; BravoMaskedTextBox; BravoComboBox; TextEdit; TextEdit `PART_Editor`
- **Checkboxes:** Show summary panel
- **Grid columns:** LayawayNumber; Status; LastPayment; NextDue; DueDate; Customer; Associate; Age; BuyaMobileColumnSortOrder; SmsAbilityStatus

### Dashboard tile: Locate Loan/Buy
_key `T_Locate_Loan_Buy` · captured 2026-09-30 22:36:28 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/T_Locate_Loan_Buy.png`

- **Buttons:** (no label) `HeaderSite`; Cancel `btnCancel`; Save `btnSave`; Pick Up; Custom Reports `btnAdHoc`; View Police Export; Process; Price Guide Report; Item Detail; Customer View; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Cancel; Save; Loans on Notice; All Active; Contacted But No Activity; 221; Review Pending Changes; Pick Up; Custom Reports; View Police Export; Process; No Image Available; Number; Tag Description; Location; Amount; Qty; Manufacturer/Model; Serial Number; Price Guide Report; Notes; Item Detail; Customer View; Locate Loan/Buy:; Layouts; Name; Saved Layouts; Delete Layout; Show summary panel; Ticket Number `PART_Content`; Disposition `PART_Content`; Disposition Date `PART_Content`; Due Date `PART_Content`; Pull Date `PART_Content`; Customer `PART_Content`; Associate `PART_Content`; Age `PART_Content`; MobilePawn `PART_Content`; SMS `PART_Content`
- **Options:** Loans To Expire; Send Loan Notice; Loans on Notice; Loans to Retag; All Active; Contacted But No Activity; Review Pending Changes; Locate Loan/Buy
- **Fields:** BravoMaskedTextBox; BravoComboBox
- **Checkboxes:** Show summary panel
- **Grid columns:** TicketNumber; Disposition; DispositionDate; DueDate; PullDate; Customer; Associate; Age; BuyaMobileColumnSortOrder; SmsAbilityStatus

### Dashboard tile: Locate Pending Payment
_key `T_Locate_Pending_Payment` · captured 2026-09-30 22:37:19 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/T_Locate_Pending_Payment.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Place on eBay; Relist; Don't Show; View Listing on eBay; Cancel; Print List; Custom Reports; Item History; Estimator; Item Detail; Price Guide; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Done; All Available; Can Be Relisted; Pending Review; All Active; Sold Awaiting Payment; Sold Awaiting Shipment; Ended Listings (Last 90 days); Closed (Last 90 days); Listings with Questions; Place on eBay; Relist; Don't Show; View Listing on eBay; Cancel; Print List; Custom Reports; Item History; No Image Available; Number; Quality; Tag Description; Price; Cost; Global Shipping; Category; eBay Category; Location; eBay Advanced Item Specifics; Estimator; Item Detail; Notes; Price Guide; Locate Pending Payment:; Layouts; Name; Saved Layouts; Delete Layout; Save; Show summary panel … +4 more
- **Fields:** BravoMaskedTextBox; BravoComboBox `Editor`; LookUpEdit; BravoComboBox
- **Checkboxes:** Show summary panel
- **Grid columns:** StatusCode; Category; WebSalePrice; TagDescription

### Dashboard tile: Web Feedbacks
_key `T_Web_Feedbacks` · captured 2026-09-30 22:39:01 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/T_Web_Feedbacks.png`

- **Buttons:** Done `btnDone`; Print List; Cancel; Leave Feedback; Web Order View; Web Item View; Customer View
- **Labels:** Done; Pending Requests; Expired Requests; Left Feedbacks; Print List; Customer Name; Tag Description; Type; Rating; Comment; Really nice to meet you – Please come back and shop with us!; You are a good negotiator, we appreciate your business.; Cancel; Leave Feedback; Web Order View; Web Item View; Customer View; Type `PART_Content`; Request Time `PART_Content`
- **Options:** Pending Requests; Expired Requests; Left Feedbacks; Great Customer – Fast Payment –  Highly Recommend - Please come back and shop with us!; Really nice to meet you – Please come back and shop with us!; One of the best customers to deal with, come back and shop with us!; You are a good negotiator, we appreciate your business.; Best BUYA customer, highly recommend this shopper. Please come back and shop with us!
- **Fields:** BravoMaskedTextBox; BravoComboBox
- **Grid columns:** Entity.Type; Entity.RequestTime

### Dashboard tile: Web Fulfillment
_key `T_Web_Fulfillment` · captured 2026-09-30 22:37:41 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/T_Web_Fulfillment.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Custom Reports; Print List; Item History; Print Order; Cancel Order; Mark Customer Contacted; Details; Web Item View; Customer View; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Done; Complete In-Store Pickup; Locate In-Store Pickup; Pending Web Fulfillments; Pending Web Transactions; Custom Reports; Print List; Item History; Print Order; Cancel Order; Mark Customer Contacted; Order Number; Order Date; Promise Date; Order Status; Shipping Method; Ship Complete; Sale Amount; Shipping Amount; Sales Tax Amount; Total Amount; Total Charged; Payment Method; Payment Contact; Shipping Information; Phone Number; Comments; Details; Web Item View; Customer View; Pending Web Fulfillments:; Layouts; Name; Saved Layouts; Delete Layout; Save; Show summary panel; Order Source `PART_Content`; Order Number `PART_Content`; Customer `PART_Content` … +5 more
- **Options:** Complete In-Store Pickup; Locate In-Store Pickup; Pending Web Fulfillments; Web Payment Settlement; Pending Web Transactions; Web Returns; Web Offers
- **Fields:** BravoMaskedTextBox; BravoDateEdit; BravoComboBox; (no label) `PART_Editor`
- **Checkboxes:** Show summary panel
- **Dropdowns:** SearchComboBox
- **Grid columns:** Web_Order.SourceName; Web_Order.PrintNumber; Web_Order.Customer.FullName; Web_Order.OrderTime.Date; Item_Merch.InventoryNumber; SaleAmt; Web_Order.AgeHours; Item_Merch.Location.Name; Web_Order.FraudFlag; Web_Order_Item.Web_Order.SourceName; PrintNumber; Customer.FullName; RmaTime.Date; StatusCode; TotalAmt; Item_Merch.TagDesc; ResponseCode; OfferTime.Date; Item_Merch.ItemCost; Item_Merch.ItemPrice; OfferAmt; DiscountPct; AgeHours

### Dashboard tile: Web In-Store Pickup
_key `T_Web_In_Store_Pickup` · captured 2026-09-30 22:38:08 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/T_Web_In_Store_Pickup.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Custom Reports; Print List; Item History; Print Order; Cancel Order; Mark Customer Contacted; Details; Web Item View; Customer View; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Done; Complete In-Store Pickup; Locate In-Store Pickup; Pending Web Fulfillments; Pending Web Transactions; Custom Reports; Print List; Item History; Print Order; Cancel Order; Mark Customer Contacted; Order Number; Order Date; Promise Date; Order Status; Shipping Method; Ship Complete; Sale Amount; Shipping Amount; Sales Tax Amount; Total Amount; Total Charged; Payment Method; Payment Contact; Shipping Information; Phone Number; Comments; Details; Web Item View; Customer View; Locate In-Store Pickup:; Layouts; Name; Saved Layouts; Delete Layout; Save; Show summary panel; Order Source `PART_Content`; Order Number `PART_Content`; Customer `PART_Content` … +5 more
- **Options:** Complete In-Store Pickup; Locate In-Store Pickup; Pending Web Fulfillments; Web Payment Settlement; Pending Web Transactions; Web Returns; Web Offers
- **Fields:** BravoMaskedTextBox; BravoDateEdit; BravoComboBox; (no label) `PART_Editor`
- **Checkboxes:** Show summary panel
- **Dropdowns:** SearchComboBox
- **Grid columns:** Web_Order.SourceName; Web_Order.PrintNumber; Web_Order.Customer.FullName; Web_Order.OrderTime.Date; Item_Merch.InventoryNumber; SaleAmt; Web_Order.AgeHours; Item_Merch.Location.Name; Web_Order.FraudFlag; Web_Order_Item.Web_Order.SourceName; PrintNumber; Customer.FullName; RmaTime.Date; StatusCode; TotalAmt; Item_Merch.TagDesc; ResponseCode; OfferTime.Date; Item_Merch.ItemCost; Item_Merch.ItemPrice; OfferAmt; DiscountPct; AgeHours

### Dashboard tile: Web Offers
_key `T_Web_Offers` · captured 2026-09-30 22:38:34 · Bravo     2026.6.0.79     VALLEY PAWN - WAYNESBORO (WAY)_
Screenshot: `output/bravo_map/shots/T_Web_Offers.png`

- **Buttons:** (no label) `HeaderSite`; Done `btnDone`; Negotiator; Custom Reports; Print List; Item History; Print Order; Offer History; Customer View; Delete Layout; Save; (no label) `DecreaseLarge`; (no label) `IncreaseLarge`
- **Labels:** Done; Complete In-Store Pickup; Locate In-Store Pickup; Pending Web Fulfillments; Pending Web Transactions; Negotiator; Custom Reports; Print List; Item History; Print Order; No Image Available; Number; Quality; Web Title; Location; Tag Type; Web; MSRP; Price; Cost; Offer; Response; Status; Counter; Web Price; Quantity; Max Discount %; Manufacturer/Model; Serial Number; Buyer Comment; Seller Comment; Offer History; Customer View; Web Offers:; Layouts; Name; Saved Layouts; Delete Layout; Save; Show summary panel … +11 more
- **Options:** Complete In-Store Pickup; Locate In-Store Pickup; Pending Web Fulfillments; Web Payment Settlement; Pending Web Transactions; Web Returns; Web Offers
- **Fields:** BravoMaskedTextBox; SpinEdit; BravoComboBox; (no label) `PART_Editor`
- **Grid columns:** Web_Order.SourceName; Web_Order.PrintNumber; Web_Order.Customer.FullName; Web_Order.OrderTime.Date; Item_Merch.InventoryNumber; SaleAmt; Web_Order.AgeHours; Item_Merch.Location.Name; Web_Order.FraudFlag; Web_Order_Item.Web_Order.SourceName; PrintNumber; Customer.FullName; RmaTime.Date; StatusCode; TotalAmt; Item_Merch.TagDesc; ResponseCode; OfferTime.Date; Item_Merch.ItemCost; Item_Merch.ItemPrice; OfferAmt; DiscountPct; AgeHours
- **Checkboxes:** Show summary panel
- **Dropdowns:** SearchComboBox

## Could not be mapped automatically (needs one supervised look)

- `R__tree` (failed 1x)

## Run history

- 2026-09-30 16:35 skipped: Bravo never idle before the deadline
- 2026-09-30 22:55 mode=full end='2026-09-30 22:54:46 ABORT no-dashboard after S_Customers__Schedule_Mobile_Event' steps_done_total=46 (+46 this run) failed_keys=1 health=PASS CUL
