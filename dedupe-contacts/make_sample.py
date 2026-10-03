"""見本の連絡先 CSV(300 行)を作る。わざと重複・表記ゆれ・怪しいメールを混ぜる。"""
import csv, random
random.seed(7)
first = ["Emma","Liam","Olivia","Noah","Ava","Mason","Sophia","Ethan","Mia","Lucas","Aiko","Haruto","Yui","Sota","Hana","Ren"]
last = ["Smith","Johnson","Brown","Garcia","Miller","Davis","Wilson","Anderson","Tanaka","Sato","Suzuki","Takahashi","Kobayashi","Yamamoto"]
cos = ["Acme Corp","Globex Inc","Initech","Umbrella Co","Hooli","Vandelay Industries","Stark Industries","Wayne Enterprises","Soylent Corp","Wonka Industries"]
locs = ["New York, NY","Austin, TX","Tokyo, JP","Osaka, JP","London, UK","Berlin, DE","Toronto, CA","Sydney, AU"]
rows = []
for i in range(230):
    f, l, c = random.choice(first), random.choice(last), random.choice(cos)
    dom = c.lower().split()[0] + ".com"
    rows.append({"name": f"{f} {l}", "company": c, "email": f"{f.lower()}.{l.lower()}@{dom}",
                 "phone": f"+1 {random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}", "location": random.choice(locs)})
def variant(r):
    v = dict(r)
    k = random.randint(0, 4)
    if k == 0: v["name"] = v["name"].upper()
    if k == 1: v["email"] = v["email"].upper()
    if k == 2: v["company"] = v["company"].replace(" Corp", " Corporation").replace(" Inc", ", Inc.")
    if k == 3: v["phone"] = v["phone"].replace("-", "").replace(" ", "").replace("+1", "(")[:4] + ") " + v["phone"][-8:]
    if k == 4: v["name"] = v["name"].split()[0][0] + ". " + v["name"].split()[1]
    return v
for r in random.sample(rows, 40): rows.append(variant(r))         # 近似重複 40
for r in random.sample(rows[:230], 15): rows.append(dict(r))       # 完全重複 15
for i in range(10):                                                # 怪しいメール / 欠損
    rows.append({"name": f"Test User{i}", "company": "" if i % 2 else "Acme Corp", "email": random.choice(["asdf@asdf.com","nobody@mailinator.com","john@@example.com","x@tempmail.net","info@example"]), "phone": "", "location": "" if i % 3 else "Austin, TX"})
random.shuffle(rows)
with open("contacts_raw.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["name","company","email","phone","location"]); w.writeheader(); w.writerows(rows)
print(len(rows), "rows -> contacts_raw.csv")
