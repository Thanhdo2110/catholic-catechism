import { useState, useCallback } from "react";
import {
  Chrome,
  Mail,
  User,
  Lock,
  Sparkles,
  ShieldCheck,
  ArrowLeft,
  GraduationCap,
} from "lucide-react";
import type { LanguageCode } from "../types/quiz";

/* ------------------------------------------------------------------ */
/*  Translation keys (auth-specific subset)                           */
/* ------------------------------------------------------------------ */

type AuthTranslationKey =
  | "authTitle"
  | "authSubtitle"
  | "authGoogle"
  | "authGoogleDesc"
  | "authSubmit"
  | "authSwitchToLogin"
  | "authSwitchToRegister"
  | "authLoginTitle"
  | "authRegisterTitle"
  | "authLoginSubtitle"
  | "authRegisterSubtitle"
  | "authOrDivider"
  | "authSuccess"
  | "authError"
  | "authRequired"
  | "authInvalidEmail"
  | "authShortPassword"
  | "authGuest"
  | "authGuestDesc"
  | "authNameLabel"
  | "authNamePlaceholder"
  | "authEmailLabel"
  | "authEmailPlaceholder"
  | "authPasswordLabel"
  | "authPasswordPlaceholder"
  | "backToHome";

const authTranslations: Record<LanguageCode, Record<AuthTranslationKey, string>> = {
  vi: {
    authTitle: "Đăng nhập / Đăng ký",
    authSubtitle: "Đăng nhập để bắt đầu hành trình học Giáo Lý",
    authGoogle: "Đăng nhập với Google",
    authGoogleDesc: "Nhanh chóng và an toàn",
    authSubmit: "Đăng nhập",
    authSwitchToLogin: "Đăng nhập",
    authSwitchToRegister: "Đăng ký",
    authLoginTitle: "Đăng nhập",
    authRegisterTitle: "Đăng ký tài khoản",
    authLoginSubtitle: "Chào mừng bạn trở lại!",
    authRegisterSubtitle: "Tạo tài khoản để bắt đầu học",
    authOrDivider: "hoặc",
    authSuccess: "Đăng nhập thành công!",
    authError: "Đăng nhập thất bại. Vui lòng thử lại.",
    authRequired: "Vui lòng điền đầy đủ thông tin.",
    authInvalidEmail: "Email không hợp lệ.",
    authShortPassword: "Mật khẩu phải có ít nhất 6 ký tự.",
    authGuest: "Tiếp tục với tư cách Khách",
    authGuestDesc: "Không cần đăng ký, dùng thử ngay",
    authNameLabel: "Họ và tên",
    authNamePlaceholder: "Nguyễn Văn A",
    authEmailLabel: "Email",
    authEmailPlaceholder: "ban@example.com",
    authPasswordLabel: "Mật khẩu",
    authPasswordPlaceholder: "Ít nhất 6 ký tự",
    backToHome: "← Quay lại Trang Chủ",
  },
  en: {
    authTitle: "Sign In / Register",
    authSubtitle: "Sign in to start your Catechism journey",
    authGoogle: "Sign in with Google",
    authGoogleDesc: "Fast and secure",
    authSubmit: "Sign In",
    authSwitchToLogin: "Sign In",
    authSwitchToRegister: "Register",
    authLoginTitle: "Sign In",
    authRegisterTitle: "Create Account",
    authLoginSubtitle: "Welcome back!",
    authRegisterSubtitle: "Create an account to start learning",
    authOrDivider: "or",
    authSuccess: "Signed in successfully!",
    authError: "Sign in failed. Please try again.",
    authRequired: "Please fill in all fields.",
    authInvalidEmail: "Invalid email address.",
    authShortPassword: "Password must be at least 6 characters.",
    authGuest: "Continue as Guest",
    authGuestDesc: "No registration needed, try now",
    authNameLabel: "Full name",
    authNamePlaceholder: "John Doe",
    authEmailLabel: "Email",
    authEmailPlaceholder: "you@example.com",
    authPasswordLabel: "Password",
    authPasswordPlaceholder: "At least 6 characters",
    backToHome: "← Back to Home",
  },
};

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

type AuthMode = "login" | "register";

interface AuthScreenProps {
  mode: AuthMode;
  onSwitchMode: (mode: AuthMode) => void;
  onAuthSuccess: (method: "google" | "quick" | "guest") => void;
  onBack: () => void;
  currentLang: LanguageCode;
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */

export function AuthScreen({
  mode,
  onSwitchMode,
  onAuthSuccess,
  onBack,
  currentLang,
}: AuthScreenProps) {
  const t = authTranslations[currentLang];
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const validate = useCallback((): string | null => {
    if (!email.trim() || !password.trim()) return t.authRequired;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return t.authInvalidEmail;
    if (password.length < 6) return t.authShortPassword;
    if (mode === "register" && !name.trim()) return t.authRequired;
    return null;
  }, [email, password, name, mode, t]);

  const handleQuickAuth = async () => {
    const err = validate();
    if (err) {
      setError(err);
      return;
    }
    setLoading(true);
    setError(null);
    // Simulate API call — replace with real endpoint later
    await new Promise((r) => setTimeout(r, 800));
    setLoading(false);
    onAuthSuccess("quick");
  };

  const handleGoogleAuth = async () => {
    setLoading(true);
    setError(null);
    // Simulate Google OAuth — replace with real Google Sign-In later
    await new Promise((r) => setTimeout(r, 1000));
    setLoading(false);
    onAuthSuccess("google");
  };

  const handleGuest = () => {
    onAuthSuccess("guest");
  };

  const isLogin = mode === "login";

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-[#fafafa] px-4 py-12">
      <div className="w-full max-w-md">
        {/* Back button */}
        <button
          type="button"
          onClick={onBack}
          className="mb-6 inline-flex items-center gap-2 text-sm font-semibold text-slate-500 transition hover:text-slate-900"
        >
          <ArrowLeft className="h-4 w-4" />
          {t.backToHome}
        </button>

        {/* Card */}
        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-[0_24px_60px_rgba(15,23,42,0.08)]">
          {/* Header */}
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-900">
              <GraduationCap className="h-8 w-8 text-amber-400" />
            </div>
            <h2 className="text-2xl font-bold text-slate-950">
              {isLogin ? t.authLoginTitle : t.authRegisterTitle}
            </h2>
            <p className="mt-2 text-sm text-slate-500">
              {isLogin ? t.authLoginSubtitle : t.authRegisterSubtitle}
            </p>
          </div>

          {/* Error banner */}
          {error && (
            <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {error}
            </div>
          )}

          {/* Google button */}
          <button
            type="button"
            onClick={handleGoogleAuth}
            disabled={loading}
            className="mt-6 flex w-full items-center justify-center gap-3 rounded-xl border-2 border-slate-200 bg-white px-4 py-3.5 text-base font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 disabled:opacity-50"
          >
            <Chrome className="h-5 w-5" />
            {t.authGoogle}
            <span className="ml-auto text-xs text-slate-400">
              {t.authGoogleDesc}
            </span>
          </button>

          {/* Divider */}
          <div className="my-6 flex items-center gap-4">
            <div className="h-px flex-1 bg-slate-200" />
            <span className="text-xs font-medium text-slate-400">
              {t.authOrDivider}
            </span>
            <div className="h-px flex-1 bg-slate-200" />
          </div>

          {/* Quick register / login form */}
          <div className="space-y-4">
            {!isLogin && (
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-700">
                  {t.authNameLabel}
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder={t.authNamePlaceholder}
                    className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-10 pr-4 text-sm text-slate-900 placeholder-slate-400 transition focus:border-amber-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-400/20"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">
                {t.authEmailLabel}
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={t.authEmailPlaceholder}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-10 pr-4 text-sm text-slate-900 placeholder-slate-400 transition focus:border-amber-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-400/20"
                />
              </div>
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">
                {t.authPasswordLabel}
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={t.authPasswordPlaceholder}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-10 pr-4 text-sm text-slate-900 placeholder-slate-400 transition focus:border-amber-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-400/20"
                />
              </div>
            </div>

            <button
              type="button"
              onClick={handleQuickAuth}
              disabled={loading}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 py-3.5 text-base font-semibold text-white shadow-lg shadow-slate-900/20 transition hover:bg-slate-800 disabled:opacity-50"
            >
              {loading ? (
                <span className="h-5 w-5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              ) : (
                <Sparkles className="h-5 w-5 text-amber-400" />
              )}
              {isLogin ? t.authSubmit : t.authSubmit}
            </button>
          </div>

          {/* Switch mode */}
          <p className="mt-6 text-center text-sm text-slate-500">
            {isLogin ? "Chưa có tài khoản? " : "Đã có tài khoản? "}
            <button
              type="button"
              onClick={() => {
                setError(null);
                onSwitchMode(isLogin ? "register" : "login");
              }}
              className="font-semibold text-amber-700 transition hover:text-amber-800"
            >
              {isLogin ? t.authSwitchToRegister : t.authSwitchToLogin}
            </button>
          </p>

          {/* Guest option */}
          <div className="mt-4">
            <button
              type="button"
              onClick={handleGuest}
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-200 py-3 text-sm font-medium text-slate-500 transition hover:border-slate-300 hover:text-slate-700 disabled:opacity-50"
            >
              <ShieldCheck className="h-4 w-4" />
              {t.authGuest}
              <span className="text-xs text-slate-400">
                ({t.authGuestDesc})
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
