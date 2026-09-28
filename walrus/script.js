let grammar;

// Collage《I Am the Walrus》
let data = {
  start: [
    "⚠️ URGENT COLLECTION NOTICE ⚠️\n==========================================\nISSUER: #agency#\nACCOUNT ID: WALRUS-1967-#code#\nSTATUS: OVERDUE (#days_late# DAYS LATE)\n------------------------------------------\nDEBTOR: #debtor#\n\nUNPAID CHARGES & ABSURD VIOLATIONS:\n#charge_item#\n#charge_item#\n#charge_item#\n------------------------------------------\nBASE DEBT: $#subtotal#\nSTUPID BLOODY TUESDAY SURCHARGE: $#penalty#\nTOTAL OVERDUE AMOUNT: $#total#\n------------------------------------------\nPAYMENT DUE: WHILE WAITING FOR THE SUN\n\nLEGAL WARNING:\n#warning#\n=========================================="
  ],

  agency: [
    "Bureau of Egg Men Enforcement",
    "Department of English Rain & Custard Taxes",
    "Corporation T-Shirt Collection Unit",
    "Semolina Pilchard & Eiffel Tower Commission"
  ],

  code: ["404", "007", "999", "1967"],
  days_late: ["3", "42", "108", "1000"],

  debtor: [
    "The Egg Man",
    "The Walrus (Goo goo g'joob)",
    "Naughty Boy with a Long Face",
    "Mister City Policeman",
    "Elementary Penguin Singing Hare Krishna"
  ],

  charge_item: [
    "• #qty#x Unpaid fee for #walrus_act# ($#price#)",
    "• Violation charge: #walrus_crime# ($#price#)"
  ],

  qty: ["1", "2", "5", "100"],

  walrus_act: [
    "sitting on a corn flake waiting for the van to come",
    "letting your knickers down during a police inspection",
    "standing in the English rain hoping to get a tan",
    "kicking Edgar Allan Poe in public space",
    "climbing up the Eiffel tower without a permit"
  ],

  walrus_crime: [
    "dripping yellow matter custard from a dead dog's eye",
    "running like pigs from a gun on a stupid bloody Tuesday",
    "flying like Lucy in the sky in a restricted air zone",
    "choking smokers while acting like an expert texpert"
  ],

  price: ["45.00", "128.50", "999.00", "5,000.00"],
  subtotal: ["1,173.50", "6,128.50", "9,999.00"],
  penalty: ["2,347.00", "12,257.00", "19,998.00"],
  total: ["3,520.50", "18,385.50", "29,997.00"],

  warning: [
    "Villain, take my purse! If ever thou wilt thrive, bury my body and pay this fine immediately.",
    "Failure to pay will result in being forced to eat Yellow Matter Custard for eternity.",
    "Non-compliance will result in an ancient ritual: Umpa, umpa, stick it up your jumper!",
    "If you do not respond, the van will come and take your corn flakes."
  ]
};

function generate() {
  let expansion = grammar.flatten("#start#");
  let pre = document.createElement("pre");
  pre.className = "text overdue-notice";
  pre.textContent = expansion;
  let container = document.getElementById("receipt-container");
  container.insertBefore(pre, container.firstChild);
}


function clearAll() {
  let container = document.getElementById("receipt-container");
  container.innerHTML = "";
}


document.addEventListener("DOMContentLoaded", () => {
  grammar = tracery.createGrammar(data);
  document.getElementById("generate").addEventListener("click", generate);
  document.getElementById("clearButton").addEventListener("click", clearAll);
//   generate();
});