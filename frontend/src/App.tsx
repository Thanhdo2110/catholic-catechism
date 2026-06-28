import { useState, useCallback } from "react";
import { ArrowLeft } from "lucide-react";
import { Dashboard } from "./components/Dashboard";
import { QuizInterface } from "./components/QuizInterface";
import { AuthScreen } from "./components/AuthScreen";
import type { LanguageCode } from "./types/quiz";

/* ------------------------------------------------------------------ */
/*  App-level state                                                    */
/*                                                                      */
/*  view: "dashboard" | "auth" | "quiz"                               */
/*  selectedTrack: "ccc" | "marriage" | null                           */
/*  authMethod: "google" | "quick" | "guest" | null                    */
/* ------------------------------------------------------------------ */

type View = "dashboard" | "auth" | "quiz";

export default function App() {
  const [view, setView] = useState<View>("dashboard");
  const [selectedTrack, setSelectedTrack] = useState<string | null>(null);
  const [authMethod, setAuthMethod] = useState<"google" | "quick" | "guest" | null>(null);
  const [lang, setLang] = useState<LanguageCode>("vi");

  /* ── Navigate to auth screen ─────────────────────────────────── */
  const handleSelectTrack = useCallback(
    (trackId: string) => {
      setSelectedTrack(trackId);
      setView("auth");
    },
    []
  );

  /* ── Auth success → go to quiz ───────────────────────────────── */
  const handleAuthSuccess = useCallback(
    (method: "google" | "quick" | "guest") => {
      setAuthMethod(method);
      setView("quiz");
    },
    []
  );

  /* ── Back to dashboard (resets everything) ───────────────────── */
  const handleBackToHome = useCallback(() => {
    setSelectedTrack(null);
    setAuthMethod(null);
    setView("dashboard");
  }, []);

  /* ── Render ──────────────────────────────────────────────────── */
  if (view === "quiz" && selectedTrack) {
    return (
      <div className="relative min-h-screen bg-[#f8fafc]">
        {/* Breadcrumb */}
        <div className="sticky top-0 z-50 border-b border-slate-200/60 bg-white/80 backdrop-blur-md">
          <div className="mx-auto max-w-4xl px-6 py-3">
            <button
              type="button"
              onClick={handleBackToHome}
              className="inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
            >
              <ArrowLeft className="h-4 w-4" />
              {lang === "vi" ? "Quay lại Trang Chủ" : "Back to Home"}
            </button>
          </div>
        </div>

        {/* Key fix: pass a resetKey that changes every time we enter quiz
            so QuizInterface's internal hook fully resets its state */}
        <QuizInterface key={`quiz-${selectedTrack}-${Date.now()}`} />
      </div>
    );
  }

  if (view === "auth") {
    return (
      <AuthScreen
        mode="login"
        onSwitchMode={() => {}}
        onAuthSuccess={handleAuthSuccess}
        onBack={handleBackToHome}
        currentLang={lang}
      />
    );
  }

  return (
    <Dashboard onSelectTrack={handleSelectTrack} currentLang={lang} />
  );
}
