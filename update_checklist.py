#!/usr/bin/env python3
"""
Single Source of Truth Checklist Manager for JalurKilat.
Updates both JalurKilat_Go_Live_Checklist.xlsx and JalurKilat_Go_Live_Checklist.csv,
and keeps formatting, colors, and timestamps in sync.
"""

import sys
import os
import csv
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
XLSX_PATH = os.path.join(BASE_DIR, "JalurKilat_Go_Live_Checklist.xlsx")
CSV_PATH = os.path.join(BASE_DIR, "JalurKilat_Go_Live_Checklist.csv")

STATUS_COLORS = {
    "Done": {"bg": "DCFCE7", "fg": "166534", "bold": True},       # Green
    "In Progress": {"bg": "DBEAFE", "fg": "1E40AF", "bold": True},# Blue
    "Pending": {"bg": "F8FAFC", "fg": "64748B", "bold": False},   # Gray
    "Blocked": {"bg": "FEE2E2", "fg": "991B1B", "bold": True}     # Red
}

def update_task_status(task_id, new_status, notes=None):
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found.")
        sys.exit(1)

    # 1. Update CSV
    rows = []
    updated = False
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        # Check if Notes column exists
        if "Keterangan / Deliverable" in headers and "Catatan Progress" not in headers:
            headers.append("Catatan Progress")
            headers.append("Terakhir Update")
            
        for r in reader:
            if len(r) < len(headers):
                r.extend([""] * (len(headers) - len(r)))
            if r[0] == task_id:
                r[3] = new_status
                if notes:
                    r[-2] = notes
                r[-1] = datetime.now().strftime("%Y-%m-%d %H:%M")
                updated = True
            rows.append(r)

    if not updated:
        print(f"Warning: Task ID {task_id} not found in CSV.")
        return False

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    # 2. Update XLSX with Styling
    if os.path.exists(XLSX_PATH):
        wb = openpyxl.load_workbook(XLSX_PATH)
        ws = wb.active

        # Find column indices
        col_map = {}
        for col_idx in range(1, ws.max_column + 1):
            val = ws.cell(row=4, column=col_idx).value
            if val:
                col_map[str(val).strip()] = col_idx

        # Ensure Update columns exist in header if not present
        if "Catatan Progress" not in col_map:
            col_map["Catatan Progress"] = ws.max_column + 1
            cell = ws.cell(row=4, column=col_map["Catatan Progress"], value="Catatan Progress")
            cell.fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
            cell.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        if "Terakhir Update" not in col_map:
            col_map["Terakhir Update"] = ws.max_column + 1
            cell = ws.cell(row=4, column=col_map["Terakhir Update"], value="Terakhir Update")
            cell.fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
            cell.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Find row and update
        for r_idx in range(5, ws.max_row + 1):
            cell_id = ws.cell(row=r_idx, column=1).value
            if cell_id == task_id:
                # Update Status Cell
                status_cell = ws.cell(row=r_idx, column=4, value=new_status)
                status_cell.alignment = Alignment(horizontal="center", vertical="center")
                
                cfg = STATUS_COLORS.get(new_status, STATUS_COLORS["Pending"])
                status_cell.fill = PatternFill(start_color=cfg["bg"], end_color=cfg["bg"], fill_type="solid")
                status_cell.font = Font(name="Calibri", size=10, bold=cfg["bold"], color=cfg["fg"])
                
                # Update Notes
                if notes and "Catatan Progress" in col_map:
                    ws.cell(row=r_idx, column=col_map["Catatan Progress"], value=notes)
                if "Terakhir Update" in col_map:
                    ws.cell(row=r_idx, column=col_map["Terakhir Update"], value=datetime.now().strftime("%Y-%m-%d %H:%M"))
                break

        # Adjust column widths
        for col in ws.columns:
            max_len = max(len(str(c.value or '')) for c in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        wb.save(XLSX_PATH)
        print(f"✅ Successfully updated Task {task_id} to [{new_status}] in XLSX and CSV.")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 update_checklist.py <TASK_ID> <STATUS> [NOTES]")
        print("Example: python3 update_checklist.py DATA-01 'In Progress' 'Building GitHub Actions scraper cron'")
        sys.exit(1)
        
    t_id = sys.argv[1]
    st = sys.argv[2]
    nt = sys.argv[3] if len(sys.argv) > 3 else ""
    update_task_status(t_id, st, nt)
