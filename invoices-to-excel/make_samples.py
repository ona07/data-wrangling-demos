"""見本の請求書 PDF を 3 枚作る(実演用。実在の会社ではない)。"""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
FONT = "HeiseiKakuGo-W5"
OUT = Path("samples"); OUT.mkdir(exist_ok=True)

INVOICES = [
    {"no": "INV-2026-0912", "date": "2026-09-12", "vendor": "株式会社ノース電材", "to": "合同会社サンプル商会",
     "items": [("LED 照明器具 40W", 12, 4800), ("配線ダクト 2m", 20, 1350), ("取付工事(一式)", 1, 38000)]},
    {"no": "INV-2026-0920", "date": "2026-09-20", "vendor": "有限会社みなみ印刷", "to": "合同会社サンプル商会",
     "items": [("A4 チラシ 両面 1,000部", 2, 9800), ("名刺 100枚", 5, 1200)]},
    {"no": "INV-2026-1001", "date": "2026-10-01", "vendor": "東西ロジスティクス株式会社", "to": "合同会社サンプル商会",
     "items": [("宅配便 (60サイズ)", 143, 780), ("宅配便 (100サイズ)", 27, 1320), ("保管料 9月分", 1, 15000), ("梱包資材", 1, 6200)]},
]

def draw(inv: dict, path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4
    c.setFont(FONT, 20); c.drawString(60, h - 70, "請 求 書")
    c.setFont(FONT, 10)
    c.drawString(60, h - 100, f"請求書番号: {inv['no']}")
    c.drawString(60, h - 115, f"発行日: {inv['date']}")
    c.drawString(60, h - 140, f"{inv['to']} 御中")
    c.drawRightString(w - 60, h - 100, inv["vendor"])
    c.drawRightString(w - 60, h - 115, "登録番号: T0000000000000")
    # 明細表(罫線あり)
    x0, y = 60, h - 190
    cols = [x0, x0 + 250, x0 + 310, x0 + 390, x0 + 475]
    heads = ["品目", "数量", "単価", "金額"]
    c.setFont(FONT, 10)
    c.line(x0, y + 14, cols[-1], y + 14)
    for i, t in enumerate(heads):
        c.drawString(cols[i] + 4, y, t)
    c.line(x0, y - 4, cols[-1], y - 4)
    subtotal = 0
    for desc, qty, unit in inv["items"]:
        y -= 20
        amt = qty * unit; subtotal += amt
        c.drawString(cols[0] + 4, y, desc)
        c.drawRightString(cols[2] - 4, y, f"{qty:,}")
        c.drawRightString(cols[3] - 4, y, f"{unit:,}")
        c.drawRightString(cols[4] - 4, y, f"{amt:,}")
        c.line(x0, y - 4, cols[-1], y - 4)
    for cx in cols:
        c.line(cx, h - 190 + 14, cx, y - 4)
    tax = subtotal // 10
    y -= 30
    for label, val in (("小計", subtotal), ("消費税(10%)", tax), ("合計", subtotal + tax)):
        c.drawString(cols[2] + 4, y, label); c.drawRightString(cols[4] - 4, y, f"¥{val:,}"); y -= 16
    c.drawString(60, 80, "お振込先: サンプル銀行 本店 普通 0000000")
    c.save()

for inv in INVOICES:
    draw(inv, OUT / f"{inv['no']}.pdf")
print("made", len(INVOICES), "PDFs in", OUT)
