#!/bin/bash
# read-only: P&L detail 12 months for the waste review (Wasted Money project)
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" report ProfitAndLossDetail 2025-11-01 2026-11-17 waste_pldetail_12m
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" report ProfitAndLoss 2025-11-01 2026-11-17 waste_pl_12m_monthly summarize_column_by=Month
