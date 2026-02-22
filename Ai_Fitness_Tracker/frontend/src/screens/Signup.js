import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { User, Lock, Eye, EyeOff, Mail, Dumbbell, ShieldCheck, Chrome, Github, Apple } from 'lucide-react';
import { useApp } from '../contexts/AppContext';

const Signup = () => {
  const { signup } = useApp();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [acceptedTerms, setAcceptedTerms] = useState(false);

  const calculatePasswordStrength = (pwd) => {
    let strength = 0;
    if (pwd.length >= 8) strength++;
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength++;
    if (/\d/.test(pwd)) strength++;
    if (/[^a-zA-Z0-9]/.test(pwd)) strength++;
    return strength;
  };

  const handlePasswordChange = (e) => {
    const text = e.target.value;
    setPassword(text);
    setPasswordStrength(calculatePasswordStrength(text));
  };

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    if (!username || !email || !password) {
      setError('Please fill in all fields');
      return;
    }

    if (!validateEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    if (passwordStrength < 2) {
      setError('Please use a stronger password');
      return;
    }

    if (!acceptedTerms) {
      setError('Please accept the Terms & Conditions');
      return;
    }

    setLoading(true);
    setError('');

    const result = await signup(username, password, email);

    if (result.success) {
      navigate('/lifestyle-quiz');
    } else {
      setError(result.error || 'Signup failed');
    }

    setLoading(false);
  };

  const getStrengthColor = () => {
    if (passwordStrength === 0) return 'text-gray-500';
    if (passwordStrength <= 2) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getStrengthBarColor = (step) => {
    if (step > passwordStrength) return 'bg-gray-200 dark:bg-zinc-800';
    if (passwordStrength <= 2) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getStrengthLabel = () => {
    if (passwordStrength === 0) return 'Very Weak';
    if (passwordStrength === 1) return 'Weak';
    if (passwordStrength === 2) return 'Fair';
    if (passwordStrength === 3) return 'Strong';
    return 'Very Strong';
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center p-6 bg-gray-50 dark:bg-black transition-colors duration-300">
      <div className="w-full max-w-md glass-card p-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-primary/20 rounded-2xl flex items-center justify-center mb-4">
            <Dumbbell size={32} className="text-lime-600 dark:text-primary" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white">Join FitAI</h1>
          <p className="text-gray-500 dark:text-gray-400">Start your fitness journey with AI</p>
        </div>

        <form onSubmit={handleSignup} className="space-y-4">
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
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoCapitalize="none"
            />
          </div>

          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Mail size={20} className="text-gray-400 dark:text-gray-500" />
            </div>
            <input
              type="email"
              className="w-full bg-gray-100 dark:bg-zinc-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white pl-10 pr-4 py-3 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all placeholder:text-gray-400 dark:placeholder:text-gray-500"
              placeholder="Email Address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoCapitalize="none"
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
              onChange={handlePasswordChange}
              autoComplete="new-password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              {showPassword ? <EyeOff size={20} className="text-gray-400 dark:text-gray-500" /> : <Eye size={20} className="text-gray-400 dark:text-gray-500" />}
            </button>
          </div>

          {password.length > 0 && (
            <div className="space-y-1">
              <div className="flex gap-1 h-1">
                {[1, 2, 3, 4].map((step) => (
                  <div
                    key={step}
                    className={`flex-1 rounded-full transition-colors ${getStrengthBarColor(step)}`}
                  />
                ))}
              </div>
              <p className={`text-xs font-semibold ${getStrengthColor()}`}>
                {getStrengthLabel()}
              </p>
            </div>
          )}

          <div className="flex items-center gap-3 py-2 cursor-pointer" onClick={() => setAcceptedTerms(!acceptedTerms)}>
            <div className={`w-5 h-5 rounded-md border-2 flex items-center justify-center transition-colors ${acceptedTerms ? 'bg-primary border-primary' : 'border-gray-200 dark:border-gray-700'}`}>
              {acceptedTerms && <ShieldCheck size={14} className="text-black" />}
            </div>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              I agree to the <Link to="/terms" className="text-lime-600 dark:text-primary hover:underline">Terms & Conditions</Link>
            </span>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-black font-bold py-3 rounded-xl hover:opacity-90 active:scale-[0.98] transition-all flex justify-center items-center"
          >
            {loading ? (
              <div className="w-6 h-6 border-2 border-black border-t-transparent rounded-full animate-spin"></div>
            ) : (
              "Create Account"
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
          Already have an account?{" "}
          <Link to="/login" className="text-lime-600 dark:text-primary font-bold hover:underline">
            Log In
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Signup;
