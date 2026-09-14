import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import { LANGUAGES, resources } from "./resources";

export const LANG_KEY = "honeychain_lang";
export { LANGUAGES };

const stored = typeof window !== "undefined" ? window.localStorage.getItem(LANG_KEY) : null;
const start = LANGUAGES.some((item) => item.code === stored) ? stored : "en";

i18n.use(initReactI18next).init({
  resources,
  lng: start,
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

export default i18n;
