import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { User, Lock, Eye, EyeOff, Dumbbell, Chrome, Github, Apple } from 'lucide-react';
import { useApp } from '../contexts/AppContext';

const Login = () => {
  const { login } = useApp();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Please enter both email and password");
      return;
    }

    setLoading(true);
    setError('');

    const result = await login(email, password);

    if (result.success) {
      console.log('Login successful, navigating to dashboard...');
      navigate('/dashboard', { replace: true });
    } else {
      setError(result.error || 'Invalid credentials');
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center p-6 bg-gray-50 dark:bg-black transition-colors duration-300">
      <div className="w-full max-w-md glass-card p-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-primary/20 rounded-2xl flex items-center justify-center mb-4">
            <Dumbbell size={32} className="text-lime-600 dark:text-primary" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white">FitAI</h1>
          <p className="text-gray-500 dark:text-gray-400">Your Personal AI Coach</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          {error && (
            <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-2 rounded-lg text-sm text-center">
              {error}
            </div>
          )}

          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <User size={20} className="text-gray-400 dark:text-gray-500" />
            </div>
            <input
              type="text"
              className="w-full bg-gray-100 dark:bg-zinc-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white pl-10 pr-4 py-3 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all placeholder:text-gray-400 dark:placeholder:text-gray-500"
              placeholder="Email or Username"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Lock size={20} className="text-gray-400 dark:text-gray-500" />
            </div>
            <input
              type={showPassword ? "text" : "password"}
              className="w-full bg-gray-100 dark:bg-zinc-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white pl-10 pr-10 py-3 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all placeholder:text-gray-400 dark:placeholder:text-gray-500"
              placeholder="Password"
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

          <div className="text-right">
            <Link to="/forgot-password" size={20} className="text-lime-600 dark:text-primary text-sm font-medium hover:underline">
              Forgot Password?
            </Link>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-black font-bold py-3 rounded-xl hover:opacity-90 active:scale-[0.98] transition-all flex justify-center items-center"
          >
            {loading ? (
              <div className="w-6 h-6 border-2 border-black border-t-transparent rounded-full animate-spin"></div>
            ) : (
              "Login"
            )}
          </button>
        </form>

        <div className="my-8 flex items-center">
          <div className="flex-1 border-t border-gray-200 dark:border-gray-700"></div>
          <span className="mx-4 text-xs text-gray-500 uppercase font-bold tracking-wider">OR CONTINUE WITH</span>
          <div className="flex-1 border-t border-gray-200 dark:border-gray-700"></div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <button className="flex justify-center items-center py-3 bg-gray-100 dark:bg-zinc-900 border border-gray-200 dark:border-gray-700 rounded-xl hover:bg-gray-200 dark:hover:bg-zinc-800 transition-all text-gray-900 dark:text-white">
            <Chrome size={20} />
          </button>
          <button className="flex justify-center items-center py-3 bg-gray-100 dark:bg-zinc-900 border border-gray-200 dark:border-gray-700 rounded-xl hover:bg-gray-200 dark:hover:bg-zinc-800 transition-all text-gray-900 dark:text-white">
            <Github size={20} />
          </button>
          <button className="flex justify-center items-center py-3 bg-gray-100 dark:bg-zinc-900 border border-gray-200 dark:border-gray-700 rounded-xl hover:bg-gray-200 dark:hover:bg-zinc-800 transition-all text-gray-900 dark:text-white">
            <Apple size={20} />
          </button>
        </div>

        <div className="mt-8 text-center text-sm text-gray-500 dark:text-gray-400">
          Don't have an account?{" "}
          <Link to="/signup" className="text-lime-600 dark:text-primary font-bold hover:underline">
            Sign Up
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
