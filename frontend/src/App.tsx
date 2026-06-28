import { useState } from "react";
import { ArrowLeft } from "lucide-react";
import { Dashboard } from "./components/Dashboard";
import { QuizInterface } from "./components/QuizInterface";
import type { LanguageCode } from "./types/quiz";

export default function App() {
  const [selectedTrack, setSelectedTrack] = useState<string | null>(null);
  const [lang, setLang] = useState<LanguageCode>("vi");

  const handleSelectTrack = (trackId: string) => {
    setSelectedTrack(trackId);
  };

  const handleBackToHome = () => {
    setSelectedTrack(null);
  };

  if (selectedTrack) {
    return (
      <div className="relative">
        {/* Breadcrumb back button */}
        <div className="sticky top-0 z-50 border-b border-slate-200/60 bg-white/80 backdrop-blur-md">
          <div className="mx-auto max-w-4xl px-6 py-3">
            <button
              type="button"
              onClick={handleBackToHome}
              className="inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
            >
              <ArrowLeft className="h-4 w-4" />
              Quay lại Trang Chủ
            </button>
          </div>
        </div>

        {/* QuizInterface manages its own internal state */}
        <QuizInterface />
      </div>
    );
  }

  return (
    <Dashboard onSelectTrack={handleSelectTrack} currentLang={lang} />
  );
}
