from flask import Flask, render_template, request, send_file
import pandas as pd
import uuid, os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/settle", methods=["POST"])
def settle():
    data = request.json

    participants = data["participants"]
    rates = data["exchange_rates"]
    expenses = data["expenses"]

    paid = {p: 0 for p in participants}
    owed = {p: 0 for p in participants}
    expense_rows = []

    for e in expenses:
        krw = e["amount"] * rates[e["currency"]]
        share = krw / len(e["participants"])

        paid[e["payer"]] += krw
        for p in e["participants"]:
            owed[p] += share

        expense_rows.append({
            "날짜": e["date"],
            "항목": e["category"],
            "내용": e["memo"],
            "결제자": e["payer"],
            "통화": e["currency"],
            "외화금액": e["amount"],
            "원화금액": round(krw),
            "참여자": ", ".join(e["participants"])
        })

    summary = []
    for p in participants:
        summary.append({
            "이름": p,
            "낸 돈": round(paid[p]),
            "부담금": round(owed[p]),
            "차액": round(paid[p] - owed[p])
        })

    transfers = []
    givers = [(p, -v) for p, v in paid.items() if paid[p] - owed[p] < 0]
    takers = [(p, v) for p, v in paid.items() if paid[p] - owed[p] > 0]

    gi = ti = 0
    while gi < len(givers) and ti < len(takers):
        g_name, g_amt = givers[gi]
        t_name, t_amt = takers[ti]
        amt = min(g_amt, t_amt)

        transfers.append({
            "보내는 사람": g_name,
            "받는 사람": t_name,
            "금액": round(amt)
        })

        givers[gi] = (g_name, g_amt - amt)
        takers[ti] = (t_name, t_amt - amt)

        if givers[gi][1] == 0: gi += 1
        if takers[ti][1] == 0: ti += 1

    filename = f"travel_settlement_{uuid.uuid4().hex}.xlsx"

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        pd.DataFrame(expense_rows).to_excel(writer, index=False, sheet_name="지출내역")
        pd.DataFrame(summary).to_excel(writer, index=False, sheet_name="정산요약")
        pd.DataFrame(transfers).to_excel(writer, index=False, sheet_name="송금안내")

    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run()
