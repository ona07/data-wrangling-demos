"""見本の領収書・請求書 PDF を 3 枚作る。**わざと 3 つとも別のレイアウト**にしてある。

経費精算に実際に出てくる型を並べた:
  1. コンビニのレシート(細長い・罫線なし・品目が左右に並ぶ)
  2. 社内の立替精算書(項目名が「摘要」「日付」。合計が表の下にある)
  3. 海外取引先の英語の請求書(USD、税の書き方が違う)

実在の会社ではない。`extract.py` はこの 3 枚を同じ 1 つの表にまとめる。
"""
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas

pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
JP = "HeiseiKakuGo-W5"
EN = "Helvetica"
OUT = Path(__file__).parent / "samples"
OUT.mkdir(exist_ok=True)


def receipt(path: Path) -> None:
    """1. コンビニのレシート。幅 80mm の紙。罫線はなく、空白で桁を揃えている。"""
    w, h = 226, 560                       # 80mm × 197mm くらい
    c = canvas.Canvas(str(path), pagesize=(w, h))
    y = h - 30
    c.setFont(JP, 11)
    c.drawCentredString(w / 2, y, "ファミリーストア 函館五稜郭店")
    y -= 14
    c.setFont(JP, 7)
    c.drawCentredString(w / 2, y, "北海道函館市本町1-2-3  TEL 0138-00-0000")
    y -= 11
    c.drawCentredString(w / 2, y, "登録番号 T1234567890123")
    y -= 20
    c.setFont(JP, 8)
    c.drawString(14, y, "2026年9月28日(月) 19:42")
    y -= 10
    c.drawString(14, y, "レシートNo. 0431-02")
    y -= 18
    c.setFont(JP, 9)
    c.drawString(14, y, "領  収  書")
    y -= 16
    c.setFont(JP, 8)
    for name, qty, price in (("コピー用紙A4 500枚", 3, 580),
                             ("乾電池 単3 8本パック", 1, 698),
                             ("ボールペン 黒 10本", 2, 450),
                             ("インスタントコーヒー", 1, 880)):
        c.drawString(14, y, f"{name}")
        c.drawRightString(w - 14, y, f"{qty} x {price:,}")
        y -= 11
    y -= 6
    c.line(14, y + 4, w - 14, y + 4)
    subtotal = 3 * 580 + 698 + 2 * 450 + 880
    tax = round(subtotal * 0.1)
    y -= 6
    for label, val in (("小計", subtotal), ("消費税 10%", tax), ("合計", subtotal + tax)):
        c.drawString(14, y, label)
        c.drawRightString(w - 14, y, f"¥{val:,}")
        y -= 12
    y -= 6
    paid = 5000
    c.drawString(14, y, "現金")
    c.drawRightString(w - 14, y, f"¥{paid:,}")
    y -= 11
    c.drawString(14, y, "お釣り")
    c.drawRightString(w - 14, y, f"¥{paid - subtotal - tax:,}")
    y -= 20
    c.setFont(JP, 7)
    c.drawCentredString(w / 2, y, "上記正に領収いたしました")
    c.save()


def expense_form(path: Path) -> None:
    """2. 社内の立替精算書。項目名が「日付」「摘要」「金額」。合計は表の外。"""
    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4
    c.setFont(JP, 16)
    c.drawString(60, h - 70, "立替経費精算書")
    c.setFont(JP, 9)
    c.drawRightString(w - 60, h - 70, "提出日 令和8年10月2日")
    c.drawString(60, h - 95, "所属: 技術部   氏名: 小久保 直人")
    c.drawString(60, h - 110, "精算対象期間: 2026年9月1日 〜 2026年9月30日")
    rows = [("2026/09/03", "函館→札幌 特急往復(研究打合せ)", 11_240),
            ("2026/09/03", "宿泊費 1泊(札幌)", 8_600),
            ("2026/09/11", "部品代 立替(マイクロポンプ継手)", 4_730),
            ("2026/09/24", "学会参加費", 6_000)]
    x0, y = 60, h - 150
    cols = [x0, x0 + 90, x0 + 360, x0 + 460]
    c.setFont(JP, 9)
    c.line(x0, y + 13, cols[-1], y + 13)
    for i, t in enumerate(("日付", "摘要", "金額")):
        c.drawString(cols[i] + 4, y, t)
    c.line(x0, y - 5, cols[-1], y - 5)
    for date, memo, amount in rows:
        y -= 20
        c.drawString(cols[0] + 4, y, date)
        c.drawString(cols[1] + 4, y, memo)
        c.drawRightString(cols[3] - 4, y, f"{amount:,}")
        c.line(x0, y - 5, cols[-1], y - 5)
    for cx in cols:
        c.line(cx, h - 150 + 13, cx, y - 5)
    total = sum(r[2] for r in rows)
    y -= 34
    c.setFont(JP, 11)
    c.drawString(cols[1] + 4, y, "合計金額")
    c.drawRightString(cols[3] - 4, y, f"{total:,} 円")
    c.setFont(JP, 8)
    y -= 30
    c.drawString(60, y, "※ 交通費は実費。領収書は別添のとおり。消費税は内税。")
    y -= 14
    c.drawString(60, y, "承認: 部長 ____________   経理 ____________")
    c.save()


def invoice_en(path: Path) -> None:
    """3. 海外取引先の英語の請求書。USD。税が "VAT 0%"、支払期限つき。"""
    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4
    c.setFont(EN, 22)
    c.drawString(60, h - 70, "INVOICE")
    c.setFont(EN, 9)
    c.drawRightString(w - 60, h - 60, "Northline Instruments Ltd.")
    c.drawRightString(w - 60, h - 73, "41 Charlotte Street, London W1T 1RR, UK")
    c.drawRightString(w - 60, h - 86, "VAT Reg. GB123456789")
    c.drawString(60, h - 100, "Invoice No.  NL-2026-4417")
    c.drawString(60, h - 113, "Issue date   1 October 2026")
    c.drawString(60, h - 126, "Due date     31 October 2026 (net 30)")
    c.drawString(60, h - 152, "Bill to:  Kokubo Research, Hakodate, Japan")
    rows = [("Piezo transducer PZT-8, 2.0 MHz", 4, 185.00),
            ("Acrylic microfluidic chip, custom", 10, 42.50),
            ("Shipping (DHL Express)", 1, 96.00)]
    x0, y = 60, h - 190
    cols = [x0, x0 + 280, x0 + 340, x0 + 420, x0 + 500]
    c.setFont(EN, 9)
    for i, t in enumerate(("Description", "Qty", "Unit (USD)", "Amount")):
        c.drawString(cols[i] + 4, y, t)
    c.line(x0, y - 5, cols[-1], y - 5)
    subtotal = 0.0
    for desc, qty, unit in rows:
        y -= 18
        amount = qty * unit
        subtotal += amount
        c.drawString(cols[0] + 4, y, desc)
        c.drawRightString(cols[2] - 4, y, str(qty))
        c.drawRightString(cols[3] - 4, y, f"{unit:,.2f}")
        c.drawRightString(cols[4] - 4, y, f"{amount:,.2f}")
    y -= 10
    c.line(cols[2], y, cols[-1], y)
    for label, val in (("Subtotal", subtotal), ("VAT 0% (export)", 0.0), ("Total due USD", subtotal)):
        y -= 16
        c.drawString(cols[2] + 4, y, label)
        c.drawRightString(cols[4] - 4, y, f"{val:,.2f}")
    c.setFont(EN, 8)
    c.drawString(60, 110, "Payment by bank transfer. Please quote the invoice number as the reference.")
    c.drawString(60, 96, "Goods exported outside the UK - VAT zero-rated.")
    c.save()


def invoice_broken(path: Path) -> None:
    """4. ふつうの日本語の請求書。ただし **発行側が小計を書き間違えている**。

    明細の合計は 86,900 円だが、小計には 1 行落ちた 68,900 円が書いてある。
    こういう紙は実際に届く。LLM は書いてあるとおりに読むので、気づくのは検算の役目。
    """
    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4
    c.setFont(JP, 18)
    c.drawString(60, h - 70, "御 請 求 書")
    c.setFont(JP, 9)
    c.drawString(60, h - 100, "請求番号: 2026-0931")
    c.drawString(60, h - 114, "発行日: 2026年9月30日")
    c.drawString(60, h - 138, "小久保研究室 御中")
    c.drawRightString(w - 60, h - 100, "大沼精密加工 株式会社")
    c.drawRightString(w - 60, h - 114, "登録番号: T9876543210987")
    rows = [("アクリル板 切削加工(図面A)", 6, 7_800),
            ("アルミ治具 製作", 1, 24_500),
            ("表面研磨 追加工", 3, 5_200)]
    x0, y = 60, h - 180
    cols = [x0, x0 + 250, x0 + 310, x0 + 390, x0 + 475]
    c.setFont(JP, 9)
    c.line(x0, y + 13, cols[-1], y + 13)
    for i, t in enumerate(("品目", "数量", "単価", "金額")):
        c.drawString(cols[i] + 4, y, t)
    c.line(x0, y - 5, cols[-1], y - 5)
    for desc, qty, unit in rows:
        y -= 20
        c.drawString(cols[0] + 4, y, desc)
        c.drawRightString(cols[2] - 4, y, f"{qty:,}")
        c.drawRightString(cols[3] - 4, y, f"{unit:,}")
        c.drawRightString(cols[4] - 4, y, f"{qty * unit:,}")
        c.line(x0, y - 5, cols[-1], y - 5)
    for cx in cols:
        c.line(cx, h - 180 + 13, cx, y - 5)
    wrong_subtotal = 68_900          # 本当は 86,900。治具 1 行を足し忘れている
    y -= 32
    for label, val in (("小計", wrong_subtotal),
                       ("消費税(10%)", wrong_subtotal // 10),
                       ("合計", wrong_subtotal + wrong_subtotal // 10)):
        c.drawString(cols[2] + 4, y, label)
        c.drawRightString(cols[4] - 4, y, f"¥{val:,}")
        y -= 16
    c.setFont(JP, 8)
    c.drawString(60, 90, "お振込先: 道南しんきん 本店 普通 1234567  お支払期限: 2026年10月31日")
    c.save()


if __name__ == "__main__":
    receipt(OUT / "01-convenience-receipt.pdf")
    expense_form(OUT / "02-expense-form.pdf")
    invoice_en(OUT / "03-invoice-en.pdf")
    invoice_broken(OUT / "04-invoice-wrong-subtotal.pdf")
    print("made 4 PDFs in", OUT)
