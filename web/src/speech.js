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

export function speak(text, language = "en") {
  if (!canSpeak() || !text) {
    return;
  }
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = SPEECH_LANG[language] || "en-IN";
  utterance.rate = 0.95;
  window.speechSynthesis.speak(utterance);
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
