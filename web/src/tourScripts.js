export const TOURS = {
  beekeeper: [
    {
      path: "/app/dashboard",
      target: "[data-tour=dash-welcome]",
      title: "Your hive home",
      body: "This page is only your hives and the next jobs that matter today — not the public marketing site.",
      hi: {
        title: "आपका छत्ता होम",
        body: "यह पेज सिर्फ़ आपके छत्ते और आज के ज़रूरी काम दिखाता है — सार्वजनिक साइट नहीं।",
      },
    },
    {
      path: "/app/monitor",
      target: "[data-tour=hive-select]",
      title: "Watch the colony",
      body: "Weight, heat, and humidity update from the live hive feed. Use this before you log a harvest.",
      hi: {
        title: "कॉलोनी देखें",
        body: "वजन, गर्मी और नमी लाइव फ़ीड से अपडेट होते हैं। फसल दर्ज करने से पहले यही देखें।",
      },
    },
    {
      path: "/app/harvests",
      target: "[data-tour=harvest-form]",
      title: "Log a harvest",
      body: "Write the harvest weight here. HoneyChain checks it against the hive scale so the later batch can be trusted.",
      hi: {
        title: "फसल दर्ज करें",
        body: "यहाँ फसल का वजन लिखें। HoneyChain छत्ते के तराजू से मिलाता है ताकि बाद का बैच भरोसेमंद रहे।",
      },
    },
    {
      path: "/app/harvests",
      target: "[data-tour=harvest-status]",
      title: "From harvest to batch",
      body: "Status stays pending until an officer groups the harvest into a batch and the ledger accepts it.",
      hi: {
        title: "फसल से बैच तक",
        body: "स्थिति तब तक पेंडिंग रहती है जब तक अधिकारी फसल को बैच में जोड़कर लेजर पर स्वीकार नहीं करते।",
      },
    },
    {
      path: "/app/insights",
      target: "[data-tour=insights]",
      title: "Colony health and yield",
      body: "These models estimate health and the next weight forecast from your own hive readings.",
      hi: {
        title: "कॉलोनी स्वास्थ्य और उपज",
        body: "ये मॉडल आपके छत्ते के रीडिंग से स्वास्थ्य और अगला वजन अनुमान लगाते हैं।",
      },
    },
    {
      path: "/app/market",
      target: "[data-tour=market-board]",
      title: "See real demand",
      body: "Open listings and recent sale prices — so you are not guessing what buyers will pay.",
      hi: {
        title: "असली माँग देखें",
        body: "खुली लिस्टिंग और हाल की बिक्री भाव — ताकि खरीदार क्या देगा, अनुमान न लगाना पड़े।",
      },
    },
  ],
  officer: [
    {
      path: "/app/cluster",
      target: "[data-tour=cluster]",
      title: "Start with your own cluster",
      body: "You are the KVIC field officer for this region. The lists below are only your hives and beekeepers. Hives from other regions are hidden. Your job is to turn a beekeeper’s harvest into a sealed batch after the lab passes it.",
      hi: {
        title: "अपने क्लस्टर से शुरू करें",
        body: "आप इस क्षेत्र के KVIC फील्ड अधिकारी हैं। नीचे सिर्फ़ आपके छत्ते और पालक हैं। दूसरे क्षेत्र छिपे रहते हैं। आपका काम है पालक की फसल को लैब पास के बाद सील बैच बनाना।",
      },
    },
    {
      path: "/app/batches",
      target: "[data-tour=batch-form]",
      title: "Make a draft — do not seal it yet",
      body: "Tick the harvests that belong together. Type the kilograms this batch claims. Leave Lab test result as “pending — send to Lab desk”, then press Create draft batch. The lab inspector must pass it before you can seal it.",
      hi: {
        title: "ड्राफ्ट बनाएँ — अभी सील न करें",
        body: "जो फसलें एक साथ हैं उन्हें चुनें। इस बैच का दावा किया किलोग्राम लिखें। लैब परिणाम “pending” रखें और Create draft batch दबाएँ। सील से पहले लैब इंस्पेक्टर को पास करना होगा।",
      },
    },
    {
      path: "/app/batches",
      target: "[data-tour=commit]",
      title: "Seal only after the lab says pass",
      body: "Come back here after the lab records a pass. Pick that draft and press commit. HoneyChain allows the seal only if the claimed kilograms stay within 10% of the hive scale. A new package ID and QR are created for the jar.",
      hi: {
        title: "लैब के पास के बाद ही सील करें",
        body: "लैब के पास के बाद यहाँ लौटें। वह ड्राफ्ट चुनकर commit करें। सील तभी होगी जब दावा किया वजन छत्ते के तराजू के 10% के अंदर हो। जार के लिए नया पैकेज आईडी और QR बनता है।",
      },
    },
    {
      path: "/app/ledger",
      target: "[data-tour=ledger]",
      title: "Check the seal still matches",
      body: "Green means every sealed batch still matches what was stored. This page recalculates that each time you open it. If someone changes a sealed number, the banner turns red and names the broken block.",
      hi: {
        title: "जाँचें कि सील अब भी मेल खाती है",
        body: "हरा मतलब हर सील बैच अब भी संग्रहित आँकड़े से मेल खाता है। पेज खोलने पर यह दोबारा गिना जाता है। कोई सील संख्या बदले तो बैनर लाल हो जाता है।",
      },
    },
    {
      path: "/app/clonewatch",
      target: "[data-tour=clonewatch]",
      title: "Follow up on a copied jar",
      body: "A jar scanned too many times, or in two places too far apart to be the same jar, is listed here. Open a flagged row and follow up with the cluster. Batches that failed the 10% weight check also appear.",
      hi: {
        title: "नकली जार पर कार्रवाई करें",
        body: "जो जार बहुत बार स्कैन हुआ, या दो दूर जगहों पर दिखा, वह यहाँ है। फ्लैग पंक्ति खोलकर क्लस्टर से जाँच करें। 10% वजन जाँच में फेल बैच भी यहाँ आते हैं।",
      },
    },
    {
      path: "/app/alerts",
      target: "[data-tour=alerts]",
      title: "Warn the beekeeper",
      body: "Type a hive ID and a short note — for example, weight dropped, check the colony. Send alert queues that message for the beekeeper. This does not send SMS.",
      hi: {
        title: "पालक को चेतावनी दें",
        body: "छत्ता आईडी और छोटा नोट लिखें — जैसे वजन गिरा, कॉलोनी देखें। Send alert वह संदेश पालक के लिए रखता है। यह SMS नहीं भेजता।",
      },
    },
  ],
  lab: [
    {
      path: "/app/lab",
      target: "[data-tour=lab-queue]",
      title: "Only waiting drafts are yours",
      body: "You are the lab inspector. This list is draft batches the field officer sent for inspection. You do not create batches and you do not seal them. Click a batch ID to load it into the form.",
      hi: {
        title: "सिर्फ़ प्रतीक्षारत ड्राफ्ट आपके हैं",
        body: "आप लैब इंस्पेक्टर हैं। यह सूची फील्ड अधिकारी के भेजे ड्राफ्ट बैच हैं। आप बैच नहीं बनाते और सील नहीं करते। बैच आईडी पर क्लिक करके फॉर्म भरें।",
      },
    },
    {
      path: "/app/lab",
      target: "[data-tour=lab-form]",
      title: "Pass or fail this batch",
      body: "Enter moisture % and purity % from your test. Choose pass or fail, add a short note, then submit. Fail blocks the officer from sealing that batch. Pass unlocks the 10% weight check on Batch Review.",
      hi: {
        title: "इस बैच को पास या फेल करें",
        body: "अपनी जाँच से नमी % और शुद्धता % लिखें। पास या फेल चुनें, नोट जोड़ें, फिर जमा करें। फेल अधिकारी को सील करने से रोकता है। पास बैच रिव्यू पर 10% वजन जाँच खोलता है।",
      },
    },
    {
      path: "/app/lab",
      target: "[data-tour=lab-history]",
      title: "Your result stays on the record",
      body: "Every pass and fail you submit is listed here with your name as inspector. The officer uses that recorded pass before they can seal the batch and issue a QR.",
      hi: {
        title: "आपका परिणाम रिकॉर्ड पर रहता है",
        body: "आपका हर पास और फेल यहाँ आपके नाम के साथ रहता है। अधिकारी उसी पास के बाद बैच सील करके QR जारी कर सकता है।",
      },
    },
  ],
  admin: [
    {
      path: "/app/dashboard",
      target: "[data-tour=admin-register]",
      title: "Register a hive for a beekeeper",
      body: "You are the KVIC admin. This form adds a hive, writes starter scale readings, and can assign it to a beekeeper so they can log a harvest without waiting for a field sensor.",
      hi: {
        title: "पालक के लिए छत्ता दर्ज करें",
        body: "आप KVIC एडमिन हैं। यह फॉर्म छत्ता जोड़ता है, शुरुआती तराजू रीडिंग लिखता है, और पालक को असाइन कर सकता है ताकि वे फसल दर्ज कर सकें।",
      },
    },
    {
      path: "/app/users",
      target: "[data-tour=admin-users]",
      title: "Create the staff desks",
      body: "Officers, lab inspectors, and other admins are created here. Beekeepers register themselves and cannot choose a staff role. Set the region so an officer only sees that cluster.",
      hi: {
        title: "स्टाफ डेस्क बनाएँ",
        body: "अधिकारी, लैब इंस्पेक्टर और अन्य एडमिन यहाँ बनते हैं। पालक खुद रजिस्टर करते हैं और स्टाफ भूमिका नहीं चुन सकते। क्षेत्र सेट करें ताकि अधिकारी सिर्फ़ वह क्लस्टर देखें।",
      },
    },
    {
      path: "/app/batches",
      target: "[data-tour=batch-form]",
      title: "Draft a batch, leave it pending",
      body: "Same desk as the field officer. Tick harvests, type the claimed kilograms, leave lab result as pending, and create the draft. Do not commit until the lab has recorded a pass.",
      hi: {
        title: "बैच ड्राफ्ट करें, पेंडिंग रखें",
        body: "यह फील्ड अधिकारी वाला डेस्क है। फसलें चुनें, दावा किया किलोग्राम लिखें, लैब परिणाम पेंडिंग रखें, और ड्राफ्ट बनाएँ। लैब के पास से पहले commit न करें।",
      },
    },
    {
      path: "/app/lab",
      target: "[data-tour=lab-form]",
      title: "Record the lab result",
      body: "Open a waiting batch, enter moisture and purity, then pass or fail. Fail stops the jar. Pass is what lets the next step seal it.",
      hi: {
        title: "लैब परिणाम दर्ज करें",
        body: "प्रतीक्षारत बैच खोलें, नमी और शुद्धता लिखें, फिर पास या फेल करें। फेल जार रोकता है। पास अगले चरण को सील करने देता है।",
      },
    },
    {
      path: "/app/batches",
      target: "[data-tour=commit]",
      title: "Seal the passed batch",
      body: "Pick the draft that now has a lab pass and commit it. The seal is refused if the claimed kilograms are more than 10% away from the hive scale. A package ID and QR are issued when it succeeds.",
      hi: {
        title: "पास हुए बैच को सील करें",
        body: "जिस ड्राफ्ट पर लैब पास है उसे चुनकर commit करें। दावा किया वजन तराजू से 10% से अधिक दूर हो तो सील रुक जाती है। सफल होने पर पैकेज आईडी और QR मिलता है।",
      },
    },
    {
      path: "/app/ledger",
      target: "[data-tour=tamper]",
      title: "Prove a changed number is caught",
      body: "Green means the sealed chain still matches. Tamper with first block changes a stored weight so the page turns red. Reset tamper puts the original number back. Only an admin sees these two buttons.",
      hi: {
        title: "दिखाएँ कि बदली संख्या पकड़ी जाती है",
        body: "हरा मतलब सील चेन मेल खाती है। Tamper with first block वजन बदलकर पेज लाल करता है। Reset tamper असली संख्या लौटाता है। ये बटन सिर्फ़ एडमिन को दिखते हैं।",
      },
    },
    {
      path: "/app/clonewatch",
      target: "[data-tour=clonewatch]",
      title: "See copied or impossible scans",
      body: "Flagged jars are repeat scans, travel that is too fast, or batches that failed the weight check. Use this list when a citizen report or a shop scan looks wrong.",
      hi: {
        title: "नकली या असंभव स्कैन देखें",
        body: "फ्लैग जार बार-बार स्कैन, बहुत तेज़ यात्रा, या वजन जाँच में फेल बैच हैं। नागरिक रिपोर्ट या दुकान स्कैन गलत लगे तो यह सूची खोलें।",
      },
    },
    {
      path: "/app/model",
      target: "[data-tour=model]",
      title: "Read the model card as printed",
      body: "These are held-out scores, not a marketing claim. Colony-health accuracy on the test split is about 40%. Quote the number on this page if someone asks how good the model is.",
      hi: {
        title: "मॉडल कार्ड जैसा छपा है वैसा पढ़ें",
        body: "ये टेस्ट स्कोर हैं, विज्ञापन नहीं। कॉलोनी-स्वास्थ्य सटीकता टेस्ट पर लगभग 40% है। मॉडल कितना अच्छा है, यह पूछे तो इसी पेज का आँकड़ा बताएँ।",
      },
    },
    {
      path: "/app/analytics",
      target: "[data-tour=analytics]",
      title: "Sales by region, not live GPS",
      body: "Hive count, sale kilograms, and sale value come from ledger-linked sales. Map pins are the center of a region, not a beekeeper’s live location.",
      hi: {
        title: "क्षेत्र के अनुसार बिक्री, लाइव GPS नहीं",
        body: "छत्ते, बिक्री किलोग्राम और राशि लेजर से जुड़ी बिक्री से आते हैं। मैप पिन क्षेत्र का केंद्र है, पालक का लाइव स्थान नहीं।",
      },
    },
  ],
};

export const TOUR_LABEL = {
  beekeeper: "BEEKEEPER",
  officer: "KVIC FIELD OFFICER",
  lab: "LAB INSPECTOR",
  admin: "KVIC ADMIN",
};

export const TOUR_OFFER = {
  beekeeper: {
    title: "Take a short walkthrough?",
    body: "Six steps on your screens: hive home, live readings, logging a harvest, what pending means, colony insights, and buyer prices.",
  },
  officer: {
    title: "Field officer walkthrough",
    body: "Six steps on your desk: your cluster, a draft batch, sealing after the lab passes, the ledger check, copied jars, and a beekeeper alert.",
  },
  lab: {
    title: "Lab inspector walkthrough",
    body: "Three steps on this desk: the waiting queue, how to pass or fail a batch, and where your result is saved.",
  },
  admin: {
    title: "KVIC admin walkthrough",
    body: "Nine steps across your desks: register a hive, create staff, draft a batch, record a lab result, seal it, test the ledger, copied jars, the model card, and the sales map.",
  },
};

export function tourCopy(step, language = "en") {
  const lang = (language || "en").slice(0, 2);
  if (lang !== "en" && step[lang]) {
    return { title: step[lang].title, body: step[lang].body };
  }
  return { title: step.title, body: step.body };
}

export function tourStorageKey(username) {
  return `honeychain_tour_done_${username || "anon"}`;
}
