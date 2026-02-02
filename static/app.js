function submitData() {
  const participants = document.getElementById("participants").value.split(",");
  const ratesInput = document.getElementById("rates").value.split(",");
  const expensesInput = document.getElementById("expenses").value.split("\n");

  let rates = {};
  ratesInput.forEach(r => {
    let [k,v] = r.split(":");
    rates[k] = Number(v);
  });

  let expenses = expensesInput.map(line => {
    let [date,cat,payer,currency,amount,ps,memo] = line.split(",");
    return {
      date,
      category: cat,
      payer,
      currency,
      amount: Number(amount),
      participants: ps.split("|"),
      memo
    };
  });

  fetch("/settle", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      participants,
      exchange_rates: rates,
      expenses
    })
  })
  .then(r => r.blob())
  .then(b => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(b);
    a.download = "여행정산.xlsx";
    a.click();
  });
}
