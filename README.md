# Data-wrangling demos — Nao Kokubo

I build small, boring, reliable tools that take data out of a format people hate
and put it into one they can use: **PDF → Excel, websites → spreadsheets, messy CSV → clean CSV.**

Each folder below is a working demo, not a slide. Clone it, run the command, get the output file.
All sample data is generated and fictional; the one website involved publishes itself for scraping practice.

| Demo | The ask it answers | Stack |
|---|---|---|
| [invoices-to-excel](invoices-to-excel/) | "Turn this month's supplier invoice PDFs into one spreadsheet" | Python, pdfplumber, openpyxl |
| [scrape-books-to-csv](scrape-books-to-csv/) | "Get every product from this site, including fields only on the detail page" | Python, Playwright |
| [dedupe-contacts](dedupe-contacts/) | "Clean this merged contact list before it goes into our CRM" | Python, rapidfuzz, pandas |
| [pdf-llm-to-sheets](pdf-llm-to-sheets/) | "These receipts and invoices are in a dozen different layouts — get them into one sheet I can trust" | Python, pdfplumber, Claude + JSON schema, openpyxl |

## How I work

- **I ask before I build.** One sample of each input layout, the exact output shape, and the deadline — in writing, before any code.
- **A free sample first.** For a new client I run the first ~20 rows and send the result within 24 hours, so you see the quality before money moves.
- **You get something you can re-run.** Script + a README with the exact command + a screenshot or recording of it running. Not a one-off file you have to come back to me for.
- **Nothing fails quietly.** Totals that don't reconcile, rows that look wrong, pages that changed shape — these are flagged in the output, not swallowed.
- **I use a model only when rules can't win.** Same layout every month: coordinates and regexes, free and identical every run. Layouts all over the place: an LLM, plus a verification layer that re-checks every number against the paper.
- **I say no to the wrong jobs.** Sites that forbid automated collection, or work that needs credentials I shouldn't have.

One revision round is included. Anything beyond that we scope and quote separately.

## Running these

Python 3.12+.

```bash
pip install -r requirements.txt
cd invoices-to-excel && python make_samples.py && python extract.py samples/*.pdf -o invoices.xlsx
```

## Contact

Upwork: <https://www.upwork.com/freelancers/~01e8408dd381727b05>

---

### 日本語

PDF・Web サイト・散らかった CSV を、使える表に直す小さな道具を作ります。
3 つのフォルダはどれも**動く実演**です（見本のデータはすべて架空、対象サイトは練習用に公開されているもの）。
日本語での依頼も承ります。クラウドワークス・ランサーズでも同じ名前で活動しています。
