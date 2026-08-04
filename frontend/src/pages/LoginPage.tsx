import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { requestPasswordReset } from '../api/auth';

interface Props {
  onSuccess: () => void;
  onSwitchToSignup: () => void;
}

export function LoginPage({ onSuccess, onSwitchToSignup }: Props) {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [forgotPassword, setForgotPassword] = useState(false);
  const [resetEmailSent, setResetEmailSent] = useState(false);
  const [resetIsLoading, setResetIsLoading] = useState(false);
  const [resetError, setResetError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      await login({ email, password });
      onSuccess();
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setResetError(null);
    setResetIsLoading(true);
    try {
      await requestPasswordReset(email);
      setResetEmailSent(true);
    } catch (err: any) {
      setResetError(err.message || 'Failed to request password reset.');
    } finally {
      setResetIsLoading(false);
    }
  };

  return (
    <div className="auth-page min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-[#050816]">
      {/* Background gradients matching main app */}
      <div className="fixed inset-0 -z-10 bg-grid-radial opacity-90" />
      <div className="fixed inset-0 -z-20 bg-[radial-gradient(circle_at_top,_rgba(99,102,241,0.15),_transparent_40%),linear-gradient(180deg,_#050816_0%,_#02040a_100%)]" />

      <div className="auth-card w-full max-w-md p-8 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl relative z-10 transition-all duration-300">
        
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-indigo-500/20 text-indigo-400 mb-4 border border-indigo-500/30">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Enterprise RAG Assistant</h1>
          <p className="text-sm text-slate-400 mt-2">Sign in to continue</p>
        </div>

        {forgotPassword ? (
          <form onSubmit={handleResetSubmit} className="space-y-5">
            {resetEmailSent ? (
              <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20 text-green-400 text-sm mb-6 text-center">
                Password reset link sent to your email!
              </div>
            ) : (
              <>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5" htmlFor="reset-email">Email Address</label>
                  <input
                    id="reset-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full px-4 py-3 rounded-xl bg-black/20 border border-white/10 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all"
                    placeholder="you@company.com"
                  />
                </div>
                
                {resetError && (
                  <div className="animate-shake p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                    {resetError}
                  </div>
                )}
                
                <button
                  type="submit"
                  disabled={resetIsLoading || !email}
                  className="w-full py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center relative shadow-[0_0_15px_rgba(99,102,241,0.4)]"
                >
                  {resetIsLoading ? <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" /> : 'Send Reset Link'}
                </button>
              </>
            )}
            <div className="text-center">
              <button type="button" onClick={() => setForgotPassword(false)} className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors">
                Back to login
              </button>
            </div>
          </form>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5" htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 rounded-xl bg-black/20 border border-white/10 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all"
                placeholder="you@company.com"
              />
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-sm font-medium text-slate-300" htmlFor="password">Password</label>
                <button type="button" onClick={() => setForgotPassword(true)} className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors">
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full px-4 py-3 pr-12 rounded-xl bg-black/20 border border-white/10 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((value) => !value)}
                  className="absolute inset-y-0 right-0 flex w-12 items-center justify-center text-slate-400 transition hover:text-white"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  title={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c1.59 0 3.096-.35 4.447-.98M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.243 4.243L9.88 9.88" />
                    </svg>
                  ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.036 12.322a1.012 1.012 0 010-.644C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.437 0 .644C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.964-7.178z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {error && (
              <div className="animate-shake p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-start">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading || !email || !password}
              className="w-full py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center relative shadow-[0_0_15px_rgba(99,102,241,0.4)] hover:shadow-[0_0_25px_rgba(99,102,241,0.6)]"
            >
              {isLoading ? <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" /> : 'Sign In'}
            </button>
            
            <div className="text-center mt-6">
              <span className="text-slate-400 text-sm">Don't have an account? </span>
              <button type="button" onClick={onSwitchToSignup} className="text-sm font-medium text-indigo-400 hover:text-indigo-300 transition-colors">
                Sign up
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
