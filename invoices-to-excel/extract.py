"""請求書 PDF(複数) → 1 つの Excel。
一覧シート(1 行 = 1 請求書)と明細シート(1 行 = 1 品目)を作る。
使い方:  python extract.py samples/*.pdf -o invoices.xlsx
"""
import argparse, re, sys
from pathlib import Path
import pdfplumber
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

def num(s: str) -> int:
    return int(re.sub(r"[^\d]", "", s or "0") or 0)

def read_invoice(path: Path) -> dict:
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text() or ""
        table = page.extract_table() or []
    g = lambda pat: (re.search(pat, text) or [None, ""])[1]
    inv = {
        "file": path.name,
        "no": g(r"請求書番号[:：]\s*(\S+)"),
        "date": g(r"発行日[:：]\s*(\S+)"),
        "vendor": g(r"\n([^\n]+?(?:株式会社|有限会社|合同会社)[^\n]*?)\s*$" if False else r"((?:[^\s]*?)(?:株式会社|有限会社|合同会社)[^\s]*)"),
        "reg_no": g(r"登録番号[:：]\s*(T\d{13})"),
        "subtotal": num(g(r"小計\s*¥?([\d,]+)")),
        "tax": num(g(r"消費税\(10%\)\s*¥?([\d,]+)")),
        "total": num(g(r"合計\s*¥?([\d,]+)")),
        "lines": [],
    }
    # 先頭行は見出し。空セルは詰める
    for row in table[1:]:
        cells = [c.strip() if c else "" for c in row]
        if len(cells) < 4 or not cells[0]:
            continue
        inv["lines"].append({"desc": cells[0], "qty": num(cells[1]), "unit": num(cells[2]), "amount": num(cells[3])})
    # 検算: 明細の合計と小計が合わなければ印を付ける
    inv["check"] = "OK" if sum(l["amount"] for l in inv["lines"]) == inv["subtotal"] else "要確認"
    return inv

def write_excel(invoices: list[dict], out: Path) -> None:
    wb = Workbook()
    head_font, head_fill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="305496")
    def header(ws, cols):
        ws.append(cols)
        for c in ws[1]:
            c.font, c.fill, c.alignment = head_font, head_fill, Alignment(horizontal="center")
        ws.freeze_panes = "A2"
    ws = wb.active; ws.title = "一覧"
    header(ws, ["請求書番号", "発行日", "発行元", "登録番号", "小計", "消費税", "合計", "明細行数", "検算", "元ファイル"])
    for inv in invoices:
        ws.append([inv["no"], inv["date"], inv["vendor"], inv["reg_no"], inv["subtotal"], inv["tax"], inv["total"], len(inv["lines"]), inv["check"], inv["file"]])
    ws2 = wb.create_sheet("明細")
    header(ws2, ["請求書番号", "発行日", "発行元", "品目", "数量", "単価", "金額"])
    for inv in invoices:
        for l in inv["lines"]:
            ws2.append([inv["no"], inv["date"], inv["vendor"], l["desc"], l["qty"], l["unit"], l["amount"]])
    for sheet, money_cols in ((ws, "EFG"), (ws2, "FG")):
        for col in money_cols:
            for cell in sheet[col][1:]:
                cell.number_format = "#,##0"
        for i, column in enumerate(sheet.columns, 1):
            width = max(len(str(c.value)) if c.value is not None else 0 for c in column)
            sheet.column_dimensions[get_column_letter(i)].width = min(max(10, width * 1.6), 40)
    wb.save(out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="+"); ap.add_argument("-o", "--out", default="invoices.xlsx")
    a = ap.parse_args()
    invs = [read_invoice(Path(p)) for p in a.pdfs]
    write_excel(invs, Path(a.out))
    for inv in invs:
        print(f"{inv['no']:14} {inv['date']} {inv['vendor']:16} 合計 ¥{inv['total']:>9,}  明細 {len(inv['lines'])} 行  検算 {inv['check']}")
    print("->", a.out)
