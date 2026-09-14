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
      title: "Your cluster",
      body: "Every hive and beekeeper in your assigned region. Other regions stay out of this list.",
      hi: {
        title: "आपका क्लस्टर",
        body: "आपके क्षेत्र के सभी छत्ते और पालक। दूसरे क्षेत्र इस सूची में नहीं आते।",
      },
    },
    {
      path: "/app/batches",
      target: "[data-tour=batch-form]",
      title: "Review a harvest into a batch",
      body: "Link pending harvests, set the declared weight, and create a draft batch for inspection.",
      hi: {
        title: "फसल से बैच बनाएँ",
        body: "पेंडिंग फसलें जोड़ें, घोषित वजन लिखें, और जाँच के लिए ड्राफ्ट बैच बनाएँ।",
      },
    },
    {
      path: "/app/batches",
      target: "[data-tour=commit]",
      title: "Oracle check",
      body: "Commit runs the weight oracle against sensor-logged harvests before anything is sealed on the chain.",
      hi: {
        title: "ऑरेकल जाँच",
        body: "कमीट सेंसर-लॉग फसलों पर वजन ऑरेकल चलाता है, फिर चेन पर सील होता है।",
      },
    },
    {
      path: "/app/ledger",
      target: "[data-tour=ledger]",
      title: "Ledger integrity",
      body: "This page recomputes the hash-chain live. A green result is not a stored tick.",
      hi: {
        title: "लेजर अखंडता",
        body: "यह पेज हैश-चेन लाइव जोड़ता है। हरा निशान जमा टिक नहीं है।",
      },
    },
    {
      path: "/app/clonewatch",
      target: "[data-tour=clonewatch]",
      title: "Flagged batches",
      body: "CloneWatch lists oracle rejections and implausible scans so a cluster officer can follow up.",
      hi: {
        title: "फ्लैग किए बैच",
        body: "क्लोनवॉच ऑरेकल अस्वीकृति और संदिग्ध स्कैन दिखाता है ताकि अधिकारी आगे की कार्रवाई कर सकें।",
      },
    },
  ],
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
