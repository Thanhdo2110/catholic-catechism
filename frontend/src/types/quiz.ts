export type LanguageCode = "en" | "vi";

export interface QuizQuestion {
  id: number;
  lessonId: number;
  difficulty: number;
  language: LanguageCode;
  prompt: string;
  options: string[];
  correctOption: string;
  reference?: string | null;
  explanation?: string | null;
}

export interface QuizProgressState {
  answeredCount: number;
  correctCount: number;
  saving: boolean;
  error: string | null;
}

