"""`extract.py` が作った TSV を Google Sheets に流し込む。

    python to_sheets.py out/expenses.tsv --sheet "経費 2026-09" --worksheet 一覧

資格情報は Google のサービスアカウント鍵（JSON）。環境変数 `GOOGLE_APPLICATION_CREDENTIALS`
か `--creds` で渡す。**鍵はリポジトリに置かない。** 対象のスプレッドシートは、鍵の
`client_email` に対して編集者で共有しておく（これを忘れるのが一番多いつまずき）。

鍵を使わない渡し方もある。TSV をそのまま Sheets のセル A1 に貼れば同じ表になる。
継続のお客にはこちらの自動化を、1 回だけのお客には貼り付けを勧めている。
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path


def rows_of(tsv: Path) -> list[list[str]]:
    return [line.split("\t") for line in tsv.read_text(encoding="utf-8").splitlines() if line]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("tsv", type=Path)
    parser.add_argument("--sheet", required=True, help="スプレッドシートの名前か URL")
    parser.add_argument("--worksheet", default="一覧")
    parser.add_argument("--creds", type=Path,
                        default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    parser.add_argument("--append", action="store_true", help="消さずに下に足す")
    args = parser.parse_args()

    if not args.creds:
        print("サービスアカウント鍵が無い。GOOGLE_APPLICATION_CREDENTIALS か --creds で渡すこと。")
        print("鍵なしで渡すなら、out/expenses.tsv を Sheets の A1 に貼れば同じ表になる。")
        return 1

    # 鍵があるときだけ要る
    import gspread

    client = gspread.service_account(filename=str(args.creds))
    book = (client.open_by_url(args.sheet) if str(args.sheet).startswith("http")
            else client.open(args.sheet))
    rows = rows_of(args.tsv)
    try:
        sheet = book.worksheet(args.worksheet)
    except gspread.WorksheetNotFound:
        sheet = book.add_worksheet(args.worksheet, rows=max(len(rows) + 10, 100), cols=len(rows[0]))

    if args.append:
        sheet.append_rows(rows[1:], value_input_option="USER_ENTERED")
        print(f"{len(rows) - 1} 行を足した: {book.title} / {sheet.title}")
    else:
        sheet.clear()
        sheet.update(values=rows, range_name="A1", value_input_option="USER_ENTERED")
        sheet.freeze(rows=1)
        print(f"{len(rows) - 1} 行を書いた: {book.title} / {sheet.title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
