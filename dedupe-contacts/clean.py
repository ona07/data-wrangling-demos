"""連絡先 CSV の整形・重複除去・フラグ付け。
  - 表記の統一: 名前と会社は Title Case、メールは小文字、電話は数字と + だけに
  - 重複: 完全一致 → メール一致 → 名前+会社の近似一致(rapidfuzz, 92 以上)
  - 消さずに印を付ける: 怪しいメール、会社名か所在地が空
  - 出力: cleaned CSV + summary.md(何を何件消したか、理由つき)
使い方:  python clean.py contacts_raw.csv -o contacts_clean.csv
"""
import argparse, re
from collections import Counter
import pandas as pd
from rapidfuzz import fuzz

DISPOSABLE = {"mailinator.com", "tempmail.net", "guerrillamail.com", "10minutemail.com", "yopmail.com"}
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def norm_company(s: str) -> str:
    s = re.sub(r"[,.]", "", str(s)).strip()
    s = re.sub(r"\b(corporation)\b", "corp", s, flags=re.I)
    s = re.sub(r"\b(incorporated)\b", "inc", s, flags=re.I)
    return " ".join(w.capitalize() if not w.isupper() or len(w) > 4 else w for w in s.split())

def norm_phone(s: str) -> str:
    d = re.sub(r"[^\d+]", "", str(s))
    return d if d else ""

def main(src: str, out: str) -> None:
    df = pd.read_csv(src, dtype=str).fillna("")
    n0 = len(df)
    df["name"] = df["name"].str.strip().str.title()
    df["company"] = df["company"].map(norm_company)
    df["email"] = df["email"].str.strip().str.lower()
    df["phone"] = df["phone"].map(norm_phone)
    df["location"] = df["location"].str.strip()
    # 1) 完全重複
    before = len(df); df = df.drop_duplicates(); exact = before - len(df)
    # 2) メール一致(空は除く)
    before = len(df); df = df[~(df["email"].ne("") & df.duplicated("email", keep="first"))]; by_email = before - len(df)
    # 3) 名前+会社の近似一致(頭文字略記 "E. Smith" にも効くよう姓で絞って比較)
    df = df.reset_index(drop=True); drop = set(); reasons = []
    key = (df["name"].str.split().str[-1].str.lower() + "|" + df["company"].str.lower())
    for k, idx in df.groupby(key).groups.items():
        idx = list(idx)
        for i in range(len(idx)):
            for j in range(i + 1, len(idx)):
                a, b = df.loc[idx[i]], df.loc[idx[j]]
                score = fuzz.token_set_ratio(a["name"] + " " + a["company"], b["name"] + " " + b["company"])
                initial = a["name"].split()[0].rstrip(".")[0:1] == b["name"].split()[0].rstrip(".")[0:1]
                same_phone = a["phone"] and a["phone"][-7:] == b["phone"][-7:]
                if score >= 92 or (initial and same_phone):
                    drop.add(idx[j]); reasons.append((a["name"], b["name"], a["company"], score))
    fuzzy = len(drop); df = df.drop(index=list(drop)).reset_index(drop=True)
    # 4) フラグ(消さない)
    def email_flag(e: str) -> str:
        if not e: return "email missing"
        if not EMAIL_RE.match(e): return "email invalid"
        if e.split("@")[1] in DISPOSABLE: return "email disposable"
        if re.fullmatch(r"(asdf|test|abc|xyz|qwerty)\d*@.*", e): return "email looks fake"
        return ""
    df["flag_email"] = df["email"].map(email_flag)
    df["flag_missing"] = df.apply(lambda r: ", ".join(k for k in ("company", "location") if not r[k]), axis=1)
    df.to_csv(out, index=False)
    flags = Counter(df["flag_email"][df["flag_email"] != ""]); missing = int((df["flag_missing"] != "").sum())
    lines = [f"# Cleaning summary", "", f"- Input rows: {n0}", f"- Output rows: {len(df)}",
             f"- Removed exact duplicates: {exact}", f"- Removed same-email duplicates: {by_email}",
             f"- Removed near-duplicates (name+company fuzzy >= 92, or same initial + same phone): {fuzzy}",
             f"- Flagged (kept): email issues {sum(flags.values())} ({dict(flags)}), missing company/location {missing}", "",
             "## Near-duplicate examples (kept ← removed, score)", ""]
    lines += [f"- {a}  ←  {b}  @ {c}  ({s})" for a, b, c, s in reasons[:12]]
    open("summary.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:9]))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("-o", "--out", default="contacts_clean.csv")
    a = ap.parse_args(); main(a.src, a.out)
