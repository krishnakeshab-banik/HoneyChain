export const SPEECH_LANG = {
  en: "en-IN",
  hi: "hi-IN",
  bn: "bn-IN",
  ta: "ta-IN",
  kn: "kn-IN",
  te: "te-IN",
  mr: "mr-IN",
};

export function canSpeak() {
  return typeof window !== "undefined" && "speechSynthesis" in window;
}

export function canListen() {
  return typeof window !== "undefined" && Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);
}

function pickVoice(lang) {
  const voices = window.speechSynthesis.getVoices() || [];
  const wanted = lang.toLowerCase().replace("_", "-");
  const prefix = wanted.slice(0, 2);
  return (
    voices.find((voice) => (voice.lang || "").toLowerCase().replace("_", "-") === wanted) ||
    voices.find((voice) => (voice.lang || "").toLowerCase().startsWith(prefix)) ||
    null
  );
}

export function speak(text, language = "en") {
  if (!canSpeak() || !text) {
    return Promise.resolve(false);
  }
  window.speechSynthesis.cancel();
  const lang = SPEECH_LANG[language] || "en-IN";
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;
  utterance.rate = 0.95;
  const voice = pickVoice(lang);
  if (voice) {
    utterance.voice = voice;
    utterance.lang = voice.lang || lang;
  }
  return new Promise((resolve) => {
    let settled = false;
    const done = (ok) => {
      if (settled) {
        return;
      }
      settled = true;
      resolve(Boolean(ok));
    };
    utterance.onstart = () => done(true);
    utterance.onerror = () => done(false);
    window.speechSynthesis.speak(utterance);
    try {
      window.speechSynthesis.pause();
      window.speechSynthesis.resume();
    } catch {
      /* Chrome sometimes needs a resume kick after speak() */
    }
    window.setTimeout(() => done(window.speechSynthesis.speaking || window.speechSynthesis.pending), 500);
  });
}

export function stopSpeaking() {
  if (canSpeak()) {
    window.speechSynthesis.cancel();
  }
}

export function listenOnce(language = "en") {
  return new Promise((resolve, reject) => {
    const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Ctor) {
      reject(new Error("This browser cannot hear the microphone. Type your question instead."));
      return;
    }
    const recognition = new Ctor();
    recognition.lang = SPEECH_LANG[language] || "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = (event) => resolve(event.results[0][0].transcript);
    recognition.onerror = (event) => reject(new Error(event.error || "Could not hear that."));
    recognition.start();
  });
}
