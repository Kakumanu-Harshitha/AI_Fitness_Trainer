import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Shield, 
  CheckCircle, 
  Lock, 
  Key, 
  Smartphone,
  Copy,
  AlertTriangle
} from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { setupTOTP, verifyTOTP, changePassword } from '../utils/api';
import GlassCard from '../components/GlassCard';

const ChangePassword = () => {
  const navigate = useNavigate();
  const { user, token, refreshUserData } = useApp();
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [step, setStep] = useState('check'); // check, setup, change
  
  // Setup State
  const [qrCode, setQrCode] = useState('');
  const [secret, setSecret] = useState('');
  const [setupOtp, setSetupOtp] = useState('');
  
  // Change Password State
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [changeOtp, setChangeOtp] = useState('');

  useEffect(() => {
    if (user) {
      if (user.is_totp_enabled) {
        setStep('change');
      } else {
        setStep('setup');
        handleSetup();
      }
    }
  }, [user]);

  const handleSetup = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await setupTOTP(token);
      setQrCode(data.qr_code);
      setSecret(data.secret);
    } catch (err) {
      setError(err.message || 'Failed to initialize 2FA setup');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifySetup = async (e) => {
    e.preventDefault();
    if (!setupOtp || setupOtp.length !== 6) {
      setError('Please enter a valid 6-digit code');
      return;
    }

    setLoading(true);
    setError('');
    try {
      await verifyTOTP(token, setupOtp);
      await refreshUserData();
      setStep('change');
      setSuccess('2FA Enabled Successfully! You can now change your password.');
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 5000);
    } catch (err) {
      setError(err.message || 'Invalid code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!newPassword || !confirmPassword || !changeOtp) {
      setError('All fields are required');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }
    
    if (changeOtp.length !== 6) {
        setError('Please enter a valid 6-digit OTP code');
        return;
    }

    setLoading(true);
    try {
      await changePassword(token, newPassword, changeOtp);
      setSuccess('Password changed successfully!');
      setTimeout(() => {
        navigate('/settings');
      }, 2000);
    } catch (err) {
      setError(err.message || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(secret);
    alert('Secret copied to clipboard!');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-black text-gray-900 dark:text-white p-6 pb-24 max-w-2xl mx-auto overflow-y-auto transition-colors duration-300">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button 
          onClick={() => navigate(-1)}
          className="w-10 h-10 rounded-full bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 flex items-center justify-center text-gray-500 dark:text-zinc-400 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          <ArrowLeft size={20} />
        </button>
        <h1 className="text-2xl font-black">Change Password</h1>
      </div>

      <div className="space-y-6">
        {/* Error/Success Messages */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/50 text-red-600 dark:text-red-500 p-4 rounded-xl flex items-center gap-3">
            <AlertTriangle size={20} />
            <p>{error}</p>
          </div>
        )}
        
        {success && (
          <div className="bg-green-500/10 border border-green-500/50 text-green-600 dark:text-green-500 p-4 rounded-xl flex items-center gap-3">
            <CheckCircle size={20} />
            <p>{success}</p>
          </div>
        )}

        {/* Setup Step */}
        {step === 'setup' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <GlassCard className="p-6 space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto">
                  <Shield size={32} className="text-primary" />
                </div>
                <h2 className="text-xl font-bold">Setup Two-Factor Authentication</h2>
                <p className="text-gray-500 dark:text-zinc-400 text-sm">
                  To secure your account, please set up 2FA before changing your password.
                </p>
              </div>

              {loading && !qrCode ? (
                <div className="flex justify-center py-8">
                  <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                </div>
              ) : (
                <>
                  <div className="flex flex-col items-center space-y-4 bg-white p-4 rounded-xl border border-gray-200 dark:border-transparent">
                    {qrCode && <img src={qrCode} alt="2FA QR Code" className="w-48 h-48" />}
                  </div>

                  <div className="bg-gray-100 dark:bg-zinc-900/50 p-4 rounded-xl space-y-2">
                    <p className="text-xs text-gray-500 dark:text-zinc-500 uppercase tracking-wider font-bold">Secret Key</p>
                    <div className="flex items-center justify-between gap-2">
                      <code className="text-primary font-mono text-sm break-all">{secret}</code>
                      <button 
                        onClick={copyToClipboard}
                        className="p-2 hover:bg-gray-200 dark:hover:bg-white/10 rounded-lg transition-colors"
                      >
                        <Copy size={16} className="text-gray-500 dark:text-zinc-400" />
                      </button>
                    </div>
                  </div>

                  <form onSubmit={handleVerifySetup} className="space-y-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700 dark:text-zinc-300">Enter Verification Code</label>
                      <div className="relative">
                        <Smartphone className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 dark:text-zinc-500" size={18} />
                        <input
                          type="text"
                          maxLength="6"
                          placeholder="000000"
                          value={setupOtp}
                          onChange={(e) => setSetupOtp(e.target.value.replace(/\D/g, ''))}
                          className="w-full bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-xl py-3 pl-10 pr-4 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-zinc-600 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all tracking-widest"
                        />
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full bg-primary text-black font-bold py-3 rounded-xl hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-50"
                    >
                      {loading ? 'Verifying...' : 'Verify & Enable'}
                    </button>
                  </form>
                </>
              )}
            </GlassCard>
          </div>
        )}

        {/* Change Password Step */}
        {step === 'change' && (
          <form onSubmit={handleChangePassword} className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <GlassCard className="p-6 space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-zinc-300">New Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 dark:text-zinc-500" size={18} />
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-xl py-3 pl-10 pr-4 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-zinc-600 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                    placeholder="Enter new password"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-zinc-300">Confirm New Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 dark:text-zinc-500" size={18} />
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-xl py-3 pl-10 pr-4 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-zinc-600 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                    placeholder="Confirm new password"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-zinc-300">Authenticator Code (2FA)</label>
                <div className="relative">
                  <Smartphone className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 dark:text-zinc-500" size={18} />
                  <input
                    type="text"
                    maxLength="6"
                    placeholder="000000"
                    value={changeOtp}
                    onChange={(e) => setChangeOtp(e.target.value.replace(/\D/g, ''))}
                    className="w-full bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-xl py-3 pl-10 pr-4 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-zinc-600 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all tracking-widest"
                  />
                </div>
                <p className="text-xs text-gray-500 dark:text-zinc-500">
                  Open your Authenticator app and enter the 6-digit code.
                </p>
              </div>
            </GlassCard>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-black font-bold py-3 rounded-xl hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-50"
            >
              {loading ? 'Updating Password...' : 'Change Password'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default ChangePassword;
