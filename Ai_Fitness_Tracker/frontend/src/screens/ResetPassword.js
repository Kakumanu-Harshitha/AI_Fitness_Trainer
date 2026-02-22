import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Lock, Eye, EyeOff, Dumbbell, CheckCircle } from 'lucide-react';
import { resetPassword } from '../utils/api';

const ResetPassword = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!password || !confirmPassword) {
      setError("Please fill in all fields");
      return;
    }
    
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    
    if (!token) {
      setError("Invalid or missing reset token");
      return;
    }

    setLoading(true);
    setError('');

    try {
      await resetPassword(token, password);
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err) {
      setError(err.message || "Failed to reset password");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex flex-col justify-center items-center p-6 bg-gray-50 dark:bg-black transition-colors duration-300">
        <div className="w-full max-w-md glass-card p-8 animate-in fade-in slide-in-from-bottom-4 duration-500 text-center">
          <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle size={32} className="text-green-500" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Password Reset Successful</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">Your password has been updated. Redirecting to login...</p>
          <button
            onClick={() => navigate('/login')}
            className="w-full bg-primary text-black font-bold py-3 rounded-xl hover:opacity-90 active:scale-[0.98] transition-all"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col justify-center items-center p-6 bg-gray-50 dark:bg-black transition-colors duration-300">
      <div className="w-full max-w-md glass-card p-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-primary/20 rounded-2xl flex items-center justify-center mb-4">
            <Dumbbell size={32} className="text-lime-600 dark:text-primary" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white">New Password</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2 text-center">Create a new secure password</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-2 rounded-lg text-sm text-center">
              {error}
            </div>
          )}

          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Lock size={20} className="text-gray-400 dark:text-gray-500" />
            </div>
            <input
              type={showPassword ? "text" : "password"}
              className="w-full bg-gray-100 dark:bg-zinc-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white pl-10 pr-10 py-3 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all placeholder:text-gray-400 dark:placeholder:text-gray-500"
              placeholder="New Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              {showPassword ? <EyeOff size={20} className="text-gray-400 dark:text-gray-500" /> : <Eye size={20} className="text-gray-400 dark:text-gray-500" />}
            </button>
          </div>

          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Lock size={20} className="text-gray-400 dark:text-gray-500" />
            </div>
            <input
              type={showPassword ? "text" : "password"}
              className="w-full bg-gray-100 dark:bg-zinc-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white pl-10 pr-10 py-3 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all placeholder:text-gray-400 dark:placeholder:text-gray-500"
              placeholder="Confirm New Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-black font-bold py-3 rounded-xl hover:opacity-90 active:scale-[0.98] transition-all flex justify-center items-center"
          >
            {loading ? (
              <div className="w-6 h-6 border-2 border-black border-t-transparent rounded-full animate-spin"></div>
            ) : (
              "Reset Password"
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;
