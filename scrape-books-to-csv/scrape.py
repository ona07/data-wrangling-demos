"""公開サイト(スクレイピング練習用の books.toscrape.com)から商品一覧を集めて CSV と Excel にする。
ページ送り・詳細ページへのクリック・待ち時間つき。
使い方:  python scrape.py --pages 3 -o books.csv
"""
import argparse, csv, re, time
from pathlib import Path
from playwright.sync_api import sync_playwright
from openpyxl import Workbook

BASE = "https://books.toscrape.com/"
RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

def scrape(pages: int, delay: float, with_detail: bool) -> list[dict]:
    rows: list[dict] = []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        url = BASE + "catalogue/page-1.html"
        for n in range(1, pages + 1):
            pg.goto(url, wait_until="domcontentloaded")
            for art in pg.query_selector_all("article.product_pod"):
                a = art.query_selector("h3 a")
                rows.append({
                    "page": n,
                    "title": a.get_attribute("title"),
                    "price_gbp": float(re.sub(r"[^\d.]", "", art.query_selector(".price_color").inner_text())),
                    "rating": RATING.get(art.query_selector("p.star-rating").get_attribute("class").split()[-1], ""),
                    "in_stock": "In stock" in art.query_selector(".availability").inner_text(),
                    "url": BASE + "catalogue/" + a.get_attribute("href").replace("../", ""),
                })
            nxt = pg.query_selector("li.next a")
            if not nxt: break
            url = BASE + "catalogue/" + nxt.get_attribute("href")
            time.sleep(delay)  # 相手のサーバーに負荷をかけない
        if with_detail:  # 詳細ページを 1 件ずつ開いて UPC と在庫数を足す(「クリックして詳細」型)
            for r in rows:
                pg.goto(r["url"], wait_until="domcontentloaded")
                cells = {th.inner_text(): td.inner_text() for th, td in zip(pg.query_selector_all("table.table th"), pg.query_selector_all("table.table td"))}
                r["upc"] = cells.get("UPC", "")
                r["stock_qty"] = int((re.search(r"\((\d+) available\)", cells.get("Availability", "")) or [0, 0])[1])
                time.sleep(delay)
        b.close()
    return rows

def save(rows: list[dict], out: Path) -> None:
    cols = list(rows[0].keys())
    with out.open("w", newline="", encoding="utf-8-sig") as f:  # Excel で文字化けしない BOM 付き
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    wb = Workbook(); ws = wb.active; ws.title = "books"; ws.append(cols)
    for r in rows: ws.append([r[c] for c in cols])
    ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
    wb.save(out.with_suffix(".xlsx"))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=2); ap.add_argument("--delay", type=float, default=0.5)
    ap.add_argument("--detail", action="store_true", help="詳細ページも開く(遅いが UPC と在庫数が取れる)")
    ap.add_argument("-o", "--out", default="books.csv")
    a = ap.parse_args()
    rows = scrape(a.pages, a.delay, a.detail)
    save(rows, Path(a.out))
    print(f"{len(rows)} rows -> {a.out} / {Path(a.out).with_suffix('.xlsx')}")
