import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, Dumbbell, ArrowLeft } from 'lucide-react';
import { forgotPassword } from '../utils/api';

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) {
      setError("Please enter your email");
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await forgotPassword(email);
      setSuccess("If this email is registered, you will receive a password reset link shortly.");
    } catch (err) {
      setError(err.message || "Failed to send reset email");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center p-6 bg-gray-50 dark:bg-black transition-colors duration-300">
      <div className="w-full max-w-md glass-card p-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-primary/20 rounded-2xl flex items-center justify-center mb-4">
            <Dumbbell size={32} className="text-lime-600 dark:text-primary" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white">Reset Password</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2 text-center">Enter your email to receive a reset link</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-2 rounded-lg text-sm text-center">
              {error}
            </div>
          )}
          
          {success && (
            <div className="bg-green-500/10 border border-green-500 text-green-500 px-4 py-2 rounded-lg text-sm text-center">
              {success}
            </div>
          )}

          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Mail size={20} className="text-gray-400 dark:text-gray-500" />
            </div>
            <input
              type="email"
              className="w-full bg-gray-100 dark:bg-zinc-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white pl-10 pr-4 py-3 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all placeholder:text-gray-400 dark:placeholder:text-gray-500"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading || success}
            />
          </div>

          <button
            type="submit"
            disabled={loading || success}
            className="w-full bg-primary text-black font-bold py-3 rounded-xl hover:opacity-90 active:scale-[0.98] transition-all flex justify-center items-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="w-6 h-6 border-2 border-black border-t-transparent rounded-full animate-spin"></div>
            ) : (
              "Send Reset Link"
            )}
          </button>
          
          <div className="text-center">
            <Link to="/login" className="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white flex items-center justify-center gap-2 transition-colors">
              <ArrowLeft size={16} /> Back to Login
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ForgotPassword;
