import { useEffect, useState, useTransition } from "react";

import type { LanguageCode, QuizProgressState, QuizQuestion } from "../types/quiz";

const quizFixtures: Record<LanguageCode, QuizQuestion[]> = {
  en: [
    {
      id: 1,
      lessonId: 10,
      difficulty: 1,
      language: "en",
      prompt: "Who is the first person of the Holy Trinity?",
      options: ["The Father", "The Son", "The Holy Spirit", "Saint Peter"],
      correctOption: "The Father",
      reference: "CCC 238-242",
      explanation: "The Father is the first person of the Holy Trinity, source of the Son and the Spirit.",
    },
    {
      id: 2,
      lessonId: 10,
      difficulty: 1,
      language: "en",
      prompt: "What does the Church call God's plan to share divine life with us?",
      options: ["Sacramental law", "Divine pedagogy", "The economy of salvation", "Natural theology"],
      correctOption: "The economy of salvation",
      reference: "CCC 236",
      explanation: "The economy of salvation describes God's saving work and self-gift in history.",
    },
  ],
  vi: [
    {
      id: 1,
      lessonId: 10,
      difficulty: 1,
      language: "vi",
      prompt: "Ai la Ngoi thu nhat trong Ba Ngoi Cuc Thanh?",
      options: ["Chua Cha", "Chua Con", "Chua Thanh Than", "Thanh Phero"],
      correctOption: "Chua Cha",
      reference: "GLHTCG 238-242",
      explanation: "Chua Cha la Ngoi thu nhat trong Ba Ngoi Cuc Thanh, nguon mach cua Chua Con va Chua Thanh Than.",
    },
    {
      id: 2,
      lessonId: 10,
      difficulty: 1,
      language: "vi",
      prompt: "Hoi Thanh goi ke hoach cua Thien Chua chia se su song than linh cho chung ta la gi?",
      options: ["Luat bi tich", "Su pham than linh", "Nhiem cuc cuu do", "Than hoc tu nhien"],
      correctOption: "Nhiem cuc cuu do",
      reference: "GLHTCG 236",
      explanation: "Nhiem cuc cuu do dien ta cong trinh cuu do va su tu ban cua Thien Chua trong lich su.",
    },
  ],
};

const persistProgress = async (payload: {
  questionId: number;
  language: LanguageCode;
  selectedOption: string;
  isCorrect: boolean;
}) => {
  await new Promise((resolve) => window.setTimeout(resolve, 350));
  return payload;
};

export const useQuizController = (language: LanguageCode) => {
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [revealedCorrectness, setRevealedCorrectness] = useState<boolean | null>(null);
  const [progress, setProgress] = useState<QuizProgressState>({
    answeredCount: 0,
    correctCount: 0,
    saving: false,
    error: null,
  });
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    startTransition(() => {
      setQuestions(quizFixtures[language]);
      setCurrentIndex(0);
      setSelectedOption(null);
      setRevealedCorrectness(null);
      setProgress((current) => ({
        ...current,
        error: null,
      }));
    });
  }, [language]);

  const currentQuestion = questions[currentIndex] ?? null;

  const selectOption = async (option: string) => {
    if (!currentQuestion || selectedOption) {
      return;
    }

    const isCorrect = option === currentQuestion.correctOption;
    setSelectedOption(option);
    setRevealedCorrectness(isCorrect);
    setProgress((current) => ({
      answeredCount: current.answeredCount + 1,
      correctCount: current.correctCount + (isCorrect ? 1 : 0),
      saving: true,
      error: null,
    }));

    try {
      await persistProgress({
        questionId: currentQuestion.id,
        language,
        selectedOption: option,
        isCorrect,
      });
      setProgress((current) => ({
        ...current,
        saving: false,
      }));
    } catch {
      setProgress((current) => ({
        ...current,
        saving: false,
        error: "save_failed",
      }));
    }
  };

  const goToNextQuestion = () => {
    if (!questions.length) {
      return;
    }

    setCurrentIndex((current) => (current + 1) % questions.length);
    setSelectedOption(null);
    setRevealedCorrectness(null);
  };

  return {
    currentQuestion,
    currentIndex,
    selectedOption,
    revealedCorrectness,
    progress,
    isPending,
    selectOption,
    goToNextQuestion,
  };
};

