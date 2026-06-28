import { useEffect, useState } from "react";

import type { LanguageCode } from "../types/quiz";

const STORAGE_KEY = "catechism-language";

const resources = {
  en: {
    quiz: "Catechism Quiz",
    question: "Question",
    explanation: "Explanation",
    reference: "Reference",
    correct: "Correct",
    incorrect: "Incorrect",
    nextQuestion: "Next Question",
    saving: "Saving progress...",
    saveFailed: "Progress sync failed. Retrying in background.",
    progress: "Progress",
    answered: "Answered",
    correctCount: "Correct",
    language: "Language",
    loading: "Loading quiz...",
  },
  vi: {
    quiz: "Trac Nghiem Giao Ly",
    question: "Cau hoi",
    explanation: "Giai thich",
    reference: "Tham chieu",
    correct: "Dung",
    incorrect: "Sai",
    nextQuestion: "Cau hoi tiep theo",
    saving: "Dang luu tien do...",
    saveFailed: "Dong bo tien do that bai. He thong se tu thu lai.",
    progress: "Tien do",
    answered: "Da tra loi",
    correctCount: "Dung",
    language: "Ngon ngu",
    loading: "Dang tai cau hoi...",
  },
} satisfies Record<LanguageCode, Record<string, string>>;

const detectInitialLanguage = (): LanguageCode => {
  if (typeof window === "undefined") {
    return "en";
  }

  const savedLanguage = window.localStorage.getItem(STORAGE_KEY);
  if (savedLanguage === "en" || savedLanguage === "vi") {
    return savedLanguage;
  }

  const browserLanguage = window.navigator.language.toLowerCase();
  return browserLanguage.startsWith("vi") ? "vi" : "en";
};

export const useMockI18n = () => {
  const [language, setLanguage] = useState<LanguageCode>(detectInitialLanguage);

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, language);
  }, [language]);

  const t = (key: keyof (typeof resources)["en"]): string => resources[language][key];

  return {
    i18n: {
      language,
      changeLanguage: setLanguage,
    },
    t,
  };
};

