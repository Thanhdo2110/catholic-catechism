import { useState } from "react";
import {
  BookOpen,
  Heart,
  ChevronRight,
  Terminal,
  Play,
  Route,
  Search,
  Cpu,
  Activity,
  Zap,
  GraduationCap,
  Users,
  FileText,
  CheckCircle2,
  ArrowLeft,
  Command,
} from "lucide-react";
import type { LanguageCode } from "../types/quiz";

/* ------------------------------------------------------------------ */
/*  Translation dictionaries                                          */
/* ------------------------------------------------------------------ */

type TranslationKey =
  | "badgeActive"
  | "headline"
  | "headlineHighlight"
  | "ctaTry"
  | "ctaPath"
  | "systemTitle"
  | "sysPathways"
  | "sysQuizzes"
  | "sysLessons"
  | "sysCCC"
  | "terminalTitle"
  | "terminalRunning"
  | "terminalReady"
  | "terminalScheduler"
  | "trackCCC"
  | "trackCCCDesc"
  | "trackMarriage"
  | "trackMarriageDesc"
  | "trackLessons"
  | "trackQuestions"
  | "searchPlaceholder"
  | "searchHint"
  | "backToHome"
  | "footerCopyright"
  | "footerMission";

const translations: Record<LanguageCode, Record<TranslationKey, string>> = {
  vi: {
    badgeActive: "Học tập Ngắt quãng & Chủ động",
    headline: "Học Giáo Lý bằng hành động,",
    headlineHighlight: "không chỉ bằng đọc sách.",
    ctaTry: "Trải nghiệm Học thử",
    ctaPath: "Chọn Lộ trình học",
    systemTitle: "Tổng quan Hệ thống",
    sysPathways: "Lộ trình học",
    sysQuizzes: "Câu hỏi",
    sysLessons: "Bài học",
    sysCCC: "Đoạn CCC",
    terminalTitle: "Trạng thái Hệ thống",
    terminalRunning: "Đang chạy",
    terminalReady: "Sẵn sàng",
    terminalScheduler: "Bộ lập lịch Leitner nền",
    trackCCC: "Giáo Lý Công Giáo (CCC)",
    trackCCCDesc: "2850 đoạn Catechism qua flashcard khoa học",
    trackMarriage: "Hôn Nhân & Gia Đình",
    trackMarriageDesc: "Giá trị Kitô giáo qua tình huống thực tế",
    trackLessons: "bài học",
    trackQuestions: "câu hỏi",
    searchPlaceholder: "Tìm kiếm bài học, đoạn CCC...",
    searchHint: "Nhấn ⌘K để tìm kiếm nhanh",
    backToHome: "← Quay lại Trang Chủ",
    footerCopyright: "© 2026 Giáo Hội Công Giáo",
    footerMission: "Học Giáo Lý — Sống Tin Mừng",
  },
  en: {
    badgeActive: "Spaced & Active Learning",
    headline: "Learn Catechism through action,",
    headlineHighlight: "not just by reading.",
    ctaTry: "Try a Free Lesson",
    ctaPath: "Choose Learning Path",
    systemTitle: "System Overview",
    sysPathways: "Learning paths",
    sysQuizzes: "Quiz questions",
    sysLessons: "Lessons",
    sysCCC: "CCC paragraphs",
    terminalTitle: "System Status",
    terminalRunning: "Running",
    terminalReady: "Ready",
    terminalScheduler: "Leitner background scheduler",
    trackCCC: "Catechism (CCC)",
    trackCCCDesc: "2850 Catechism paragraphs via spaced flashcards",
    trackMarriage: "Marriage & Family",
    trackMarriageDesc: "Christian values through real-life scenarios",
    trackLessons: "lessons",
    trackQuestions: "questions",
    searchPlaceholder: "Search lessons, CCC paragraphs...",
    searchHint: "Press ⌘K to quick search",
    backToHome: "← Back to Home",
    footerCopyright: "© 2026 Catholic Church",
    footerMission: "Learn Catechism — Live the Gospel",
  },
};

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface Track {
  id: string;
  icon: typeof BookOpen;
  color: string;
  bgColor: string;
  lessons: number;
  questions: number;
}

const tracks: Track[] = [
  {
    id: "ccc",
    icon: BookOpen,
    color: "text-amber-700",
    bgColor: "bg-amber-100",
    lessons: 45,
    questions: 2500,
  },
  {
    id: "marriage",
    icon: Heart,
    color: "text-rose-700",
    bgColor: "bg-rose-100",
    lessons: 30,
    questions: 1200,
  },
];

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */

interface DashboardProps {
  onSelectTrack: (trackId: string) => void;
  currentLang: LanguageCode;
}

export function Dashboard({ onSelectTrack, currentLang }: DashboardProps) {
  const t = translations[currentLang];
  const [searchFocused, setSearchFocused] = useState(false);

  return (
    <div className="min-h-screen bg-[#fafafa] font-sans antialiased text-slate-900">
      {/* ── Navigation Bar ─────────────────────────────────────── */}
      <nav className="sticky top-0 z-50 border-b border-slate-200/60 bg-white/70 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
          {/* Logo / Brand */}
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-900">
              <GraduationCap className="h-5 w-5 text-amber-400" />
            </div>
            <span className="text-lg font-bold tracking-tight text-slate-950">
              Catechism<span className="text-amber-600">.</span>Learn
            </span>
          </div>

          {/* Search Bar */}
          <div className="hidden md:flex items-center">
            <div
              className={`flex items-center gap-2 rounded-xl border px-4 py-2 text-sm transition ${
                searchFocused
                  ? "border-amber-400 bg-amber-50/50 shadow-sm"
                  : "border-slate-200 bg-slate-50 hover:border-slate-300"
              }`}
            >
              <Search className="h-4 w-4 text-slate-400" />
              <span className="text-slate-400">{t.searchPlaceholder}</span>
              <kbd className="ml-4 flex items-center gap-0.5 rounded-lg border border-slate-200 bg-white px-2 py-0.5 text-xs font-medium text-slate-500 shadow-sm">
                <Command className="h-3 w-3" />
                K
              </kbd>
            </div>
          </div>

          {/* Right nav items */}
          <div className="flex items-center gap-4">
            <button className="rounded-xl px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100">
              {currentLang === "vi" ? "Đăng nhập" : "Sign In"}
            </button>
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-amber-100 text-sm font-bold text-amber-700">
              JD
            </div>
          </div>
        </div>
      </nav>

      {/* ── Main Content ───────────────────────────────────────── */}
      <main className="mx-auto max-w-7xl px-6 py-10">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
          {/* ── Left Column (7/12) ─────────────────────────────── */}
          <div className="lg:col-span-7 space-y-8">
            {/* Active Badge */}
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-4 py-1.5">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
              </span>
              <span className="text-sm font-semibold text-emerald-800">
                {t.badgeActive}
              </span>
            </div>

            {/* Headline */}
            <div>
              <h1 className="text-4xl font-bold leading-tight tracking-tight text-slate-950 sm:text-5xl">
                {t.headline}{" "}
                <span className="relative inline-block">
                  <span className="relative z-10">{t.headlineHighlight}</span>
                  <span className="absolute bottom-1 left-0 right-0 h-3 bg-amber-100/60" />
                </span>
              </h1>
              <p className="mt-4 max-w-xl text-lg leading-relaxed text-slate-500">
                {currentLang === "vi"
                  ? "Hệ thống học tập thông minh kết hợp khoa học nhớ Leitner và kiến thức Công Giáo chính thống, giúp bạn ghi nhớ vĩnh viễn."
                  : "An intelligent learning system combining Leitner spaced-repetition science with authentic Catholic doctrine for permanent retention."}
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-wrap gap-4">
              <button
                onClick={() => onSelectTrack("ccc")}
                className="group inline-flex items-center gap-2 rounded-xl bg-slate-900 px-6 py-3.5 text-base font-semibold text-white shadow-lg shadow-slate-900/20 transition hover:bg-slate-800 hover:shadow-xl"
              >
                <Play className="h-5 w-5 text-amber-400" />
                {t.ctaTry}
                <ChevronRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
              </button>
              <button
                onClick={() => onSelectTrack("ccc")}
                className="inline-flex items-center gap-2 rounded-xl border-2 border-slate-200 bg-white px-6 py-3.5 text-base font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
              >
                <Route className="h-5 w-5 text-slate-400" />
                {t.ctaPath}
              </button>
            </div>

            {/* System Summary Box (Fake Terminal) */}
            <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">
              {/* Window dots */}
              <div className="flex items-center gap-2 border-b border-slate-100 px-5 py-3">
                <span className="h-3 w-3 rounded-full bg-red-400" />
                <span className="h-3 w-3 rounded-full bg-amber-400" />
                <span className="h-3 w-3 rounded-full bg-emerald-400" />
                <span className="ml-3 text-xs font-medium text-slate-400">
                  {t.systemTitle}
                </span>
              </div>
              {/* JSON-like stats */}
              <div className="p-5">
                <pre className="font-mono text-sm leading-7 text-slate-700">
                  <span className="text-slate-400">{"{"}</span>
                  {"\n"}
                  <span className="text-slate-500">  "</span>
                  <span className="text-amber-700">pathways</span>
                  <span className="text-slate-500">": </span>
                  <span className="text-emerald-600 font-semibold">2</span>
                  <span className="text-slate-500">,</span>
                  {"\n"}
                  <span className="text-slate-500">  "</span>
                  <span className="text-amber-700">totalQuizzes</span>
                  <span className="text-slate-500">": </span>
                  <span className="text-emerald-600 font-semibold">2,500+</span>
                  <span className="text-slate-500">,</span>
                  {"\n"}
                  <span className="text-slate-500">  "</span>
                  <span className="text-amber-700">lessons</span>
                  <span className="text-slate-500">": </span>
                  <span className="text-emerald-600 font-semibold">45</span>
                  <span className="text-slate-500">,</span>
                  {"\n"}
                  <span className="text-slate-500">  "</span>
                  <span className="text-amber-700">cccParagraphs</span>
                  <span className="text-slate-500">": </span>
                  <span className="text-emerald-600 font-semibold">2,865</span>
                  {"\n"}
                  <span className="text-slate-400">{"}"}</span>
                </pre>
              </div>
            </div>
          </div>

          {/* ── Right Column (5/12) ────────────────────────────── */}
          <div className="lg:col-span-5 space-y-6">
            {/* Engine Status Card */}
            <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
              {/* Card Header */}
              <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
                <div className="flex items-center gap-2.5">
                  <Cpu className="h-5 w-5 text-slate-700" />
                  <span className="text-sm font-semibold text-slate-800">
                    {t.terminalTitle}
                  </span>
                </div>
                <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                  <span className="relative flex h-1.5 w-1.5">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                    <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  </span>
                  {t.terminalRunning}
                </span>
              </div>

              {/* Tracks */}
              <div className="p-4 space-y-3">
                {tracks.map((track) => {
                  const Icon = track.icon;
                  return (
                    <button
                      key={track.id}
                      onClick={() => onSelectTrack(track.id)}
                      className="group flex w-full items-center gap-4 rounded-xl border border-slate-100 bg-slate-50/50 p-4 text-left transition hover:border-slate-200 hover:bg-white hover:shadow-md"
                    >
                      {/* Icon container */}
                      <div
                        className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ${track.bgColor} transition-transform group-hover:scale-110`}
                      >
                        <Icon className={`h-6 w-6 ${track.color}`} />
                      </div>

                      {/* Track info */}
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-slate-900 truncate">
                          {track.id === "ccc" ? t.trackCCC : t.trackMarriage}
                        </p>
                        <p className="mt-0.5 text-sm text-slate-500 truncate">
                          {track.id === "ccc"
                            ? t.trackCCCDesc
                            : t.trackMarriageDesc}
                        </p>
                        <div className="mt-2 flex items-center gap-3 text-xs text-slate-400">
                          <span className="inline-flex items-center gap-1">
                            <FileText className="h-3 w-3" />
                            {track.lessons} {t.trackLessons}
                          </span>
                          <span className="inline-flex items-center gap-1">
                            <CheckCircle2 className="h-3 w-3" />
                            {track.questions.toLocaleString()} {t.trackQuestions}
                          </span>
                        </div>
                      </div>

                      {/* Arrow */}
                      <ChevronRight className="h-5 w-5 shrink-0 text-slate-300 transition group-hover:translate-x-1 group-hover:text-slate-500" />
                    </button>
                  );
                })}
              </div>

              {/* Bottom Code Terminal */}
              <div className="border-t border-slate-100 bg-slate-950 px-5 py-4">
                <div className="flex items-center gap-2 mb-3">
                  <Activity className="h-3.5 w-3.5 text-emerald-400" />
                  <span className="text-xs font-medium text-slate-400">
                    {t.terminalScheduler}
                  </span>
                  <span className="ml-auto flex items-center gap-1 text-xs text-emerald-400">
                    <Zap className="h-3 w-3" />
                    {t.terminalReady}
                  </span>
                </div>
                <pre className="font-mono text-xs leading-6 text-slate-300 overflow-x-auto">
                  <span className="text-slate-500">$ </span>
                  <span className="text-amber-300">kubectl</span> get review-schedule
                  {"\n\n"}
                  <span className="text-slate-500">NAME</span>
                  <span className="text-slate-600">                    </span>
                  <span className="text-slate-500">STATUS</span>
                  <span className="text-slate-600">       </span>
                  <span className="text-slate-500">DUE</span>
                  <span className="text-slate-600">      </span>
                  <span className="text-slate-500">CARDS</span>
                  {"\n"}
                  <span className="text-emerald-400">leitner-worker-ccc</span>
                  <span className="text-slate-600">    </span>
                  <span className="text-emerald-400">Active</span>
                  <span className="text-slate-600">    </span>
                  <span className="text-amber-300">2m ago</span>
                  <span className="text-slate-600">    </span>
                  <span className="text-white">247</span>
                  {"\n"}
                  <span className="text-sky-400">leitner-worker-marriage</span>
                  <span className="text-slate-600"> </span>
                  <span className="text-emerald-400">Active</span>
                  <span className="text-slate-600">    </span>
                  <span className="text-amber-300">5m ago</span>
                  <span className="text-slate-600">    </span>
                  <span className="text-white">183</span>
                  {"\n\n"}
                  <span className="text-slate-500">2 workers running. All schedules healthy.</span>
                  <span className="text-emerald-400"> ✓</span>
                </pre>
              </div>
            </div>

            {/* Quick Stats Row */}
            <div className="grid grid-cols-3 gap-3">
              <div className="rounded-xl border border-slate-200 bg-white p-4 text-center shadow-sm">
                <Users className="mx-auto h-5 w-5 text-amber-600" />
                <p className="mt-2 text-2xl font-bold text-slate-900">2</p>
                <p className="text-xs text-slate-500">{t.sysPathways}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-white p-4 text-center shadow-sm">
                <FileText className="mx-auto h-5 w-5 text-amber-600" />
                <p className="mt-2 text-2xl font-bold text-slate-900">45</p>
                <p className="text-xs text-slate-500">{t.sysLessons}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-white p-4 text-center shadow-sm">
                <CheckCircle2 className="mx-auto h-5 w-5 text-emerald-600" />
                <p className="mt-2 text-2xl font-bold text-slate-900">2,865</p>
                <p className="text-xs text-slate-500">{t.sysCCC}</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* ── Footer ─────────────────────────────────────────────── */}
      <footer className="border-t border-slate-200/60 bg-white/50">
        <div className="mx-auto max-w-7xl px-6 py-6">
          <div className="flex flex-col items-center justify-between gap-3 sm:flex-row">
            <p className="text-sm text-slate-400">{t.footerCopyright}</p>
            <p className="text-sm font-medium text-slate-500">
              {t.footerMission}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
