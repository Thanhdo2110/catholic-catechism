import type { LanguageCode } from "../types/quiz";
import { useQuizController } from "../hooks/useQuizController";
import { useMockI18n } from "../lib/mockI18n";

const optionStyles = (
  isSelected: boolean,
  isCorrect: boolean,
  isWrongSelection: boolean,
): string => {
  if (isCorrect) {
    return "border-emerald-500 bg-emerald-50 text-emerald-900";
  }

  if (isWrongSelection) {
    return "border-rose-500 bg-rose-50 text-rose-900";
  }

  if (isSelected) {
    return "border-slate-900 bg-slate-900 text-white";
  }

  return "border-slate-200 bg-white text-slate-800 hover:border-amber-500 hover:bg-amber-50";
};

export function QuizInterface() {
  const { i18n, t } = useMockI18n();
  const {
    currentQuestion,
    currentIndex,
    selectedOption,
    revealedCorrectness,
    progress,
    isPending,
    selectOption,
    goToNextQuestion,
  } = useQuizController(i18n.language);

  const switchLanguage = (language: LanguageCode) => {
    i18n.changeLanguage(language);
  };

  if (isPending || !currentQuestion) {
    return (
      <section className="mx-auto flex min-h-screen max-w-4xl items-center justify-center bg-[radial-gradient(circle_at_top,_#fff7ed,_#fde68a_45%,_#f8fafc_100%)] px-6 py-16 text-slate-900">
        <div className="rounded-3xl border border-white/70 bg-white/80 px-8 py-10 shadow-[0_30px_80px_rgba(148,163,184,0.18)] backdrop-blur">
          <p className="font-semibold tracking-[0.2em] text-amber-700">{t("loading")}</p>
        </div>
      </section>
    );
  }

  return (
    <section className="min-h-screen bg-[radial-gradient(circle_at_top,_#fff7ed,_#fde68a_35%,_#f8fafc_100%)] px-4 py-10 text-slate-900 sm:px-6">
      <div className="mx-auto max-w-4xl">
        <div className="mb-6 flex flex-col gap-4 rounded-[2rem] border border-white/70 bg-white/80 p-6 shadow-[0_30px_80px_rgba(148,163,184,0.18)] backdrop-blur sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-amber-700">{t("quiz")}</p>
            <h1 className="mt-2 font-serif text-3xl text-slate-950">{t("question")} {currentIndex + 1}</h1>
          </div>

          <div className="flex items-center gap-3 self-start rounded-full bg-slate-900 p-1 text-sm font-semibold text-white">
            <span className="px-3 text-slate-300">{t("language")}</span>
            <button
              type="button"
              onClick={() => switchLanguage("en")}
              className={`rounded-full px-4 py-2 transition ${i18n.language === "en" ? "bg-amber-400 text-slate-950" : "text-slate-200"}`}
            >
              EN
            </button>
            <button
              type="button"
              onClick={() => switchLanguage("vi")}
              className={`rounded-full px-4 py-2 transition ${i18n.language === "vi" ? "bg-amber-400 text-slate-950" : "text-slate-200"}`}
            >
              VI
            </button>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_18rem]">
          <article className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-[0_24px_60px_rgba(15,23,42,0.08)] sm:p-8">
            <p className="text-lg font-medium leading-8 text-slate-900">{currentQuestion.prompt}</p>

            <div className="mt-8 grid gap-3">
              {currentQuestion.options.map((option) => {
                const isSelected = selectedOption === option;
                const isCorrect = selectedOption !== null && option === currentQuestion.correctOption;
                const isWrongSelection = isSelected && option !== currentQuestion.correctOption;

                return (
                  <button
                    key={option}
                    type="button"
                    disabled={selectedOption !== null}
                    onClick={() => void selectOption(option)}
                    className={`rounded-2xl border px-5 py-4 text-left text-base font-medium transition ${optionStyles(
                      isSelected,
                      isCorrect,
                      isWrongSelection,
                    )}`}
                  >
                    {option}
                  </button>
                );
              })}
            </div>

            {selectedOption && (
              <div className="mt-8 rounded-2xl bg-slate-50 p-5">
                <p className={`text-sm font-semibold uppercase tracking-[0.25em] ${revealedCorrectness ? "text-emerald-700" : "text-rose-700"}`}>
                  {revealedCorrectness ? t("correct") : t("incorrect")}
                </p>
                {currentQuestion.explanation && (
                  <p className="mt-3 text-sm leading-7 text-slate-700">
                    <span className="font-semibold text-slate-950">{t("explanation")}: </span>
                    {currentQuestion.explanation}
                  </p>
                )}
                {currentQuestion.reference && (
                  <p className="mt-2 text-sm text-slate-600">
                    <span className="font-semibold text-slate-950">{t("reference")}: </span>
                    {currentQuestion.reference}
                  </p>
                )}

                <button
                  type="button"
                  onClick={goToNextQuestion}
                  className="mt-5 inline-flex rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-amber-500 hover:text-slate-950"
                >
                  {t("nextQuestion")}
                </button>
              </div>
            )}
          </article>

          <aside className="rounded-[2rem] border border-slate-200 bg-slate-950 p-6 text-white shadow-[0_24px_60px_rgba(15,23,42,0.18)]">
            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-amber-400">{t("progress")}</p>
            <dl className="mt-6 space-y-4">
              <div>
                <dt className="text-sm text-slate-300">{t("answered")}</dt>
                <dd className="text-3xl font-semibold">{progress.answeredCount}</dd>
              </div>
              <div>
                <dt className="text-sm text-slate-300">{t("correctCount")}</dt>
                <dd className="text-3xl font-semibold">{progress.correctCount}</dd>
              </div>
            </dl>

            <div className="mt-8 rounded-2xl bg-white/10 p-4 text-sm text-slate-200">
              {progress.saving ? t("saving") : progress.error ? t("saveFailed") : null}
            </div>
          </aside>
        </div>
      </div>
    </section>
  );
}

