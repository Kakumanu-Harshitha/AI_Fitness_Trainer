import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Save, User, Mail, Calendar, Ruler, Weight, FileText, Camera } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import GradientButton from '../components/GradientButton';
import { useApi } from '../hooks/useApi';
import { useApp } from '../contexts/AppContext';
import { API_BASE_URL } from '../utils/api';

const EditProfile = () => {
  const navigate = useNavigate();
  const { get, post } = useApi();
  const { setUser } = useApp();
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);
  const [userData, setUserData] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    age: '',
    height_cm: '',
    weight_kg: '',
    body_type: '',
    diet_goal: '',
    activity_level: '',
    daily_sleep_goal: '',
    daily_water_goal: '',
    bio: ''
  });

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const data = await get('/profile');
      if (data) {
        setUserData(data);
        setFormData({
          username: data.username || '',
          email: data.email || '',
          age: data.age || '',
          height_cm: data.height_cm || '',
          weight_kg: data.weight_kg || '',
          body_type: data.body_type || '',
          diet_goal: data.diet_goal || '',
          activity_level: data.activity_level || '',
          daily_sleep_goal: data.daily_sleep_goal || '',
          daily_water_goal: data.daily_water_goal || '',
          bio: data.bio || ''
        });
      }
    } catch (error) {
      console.error('Failed to fetch user data:', error);
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      const updatedUser = await post('/profile/avatar', formData);
      setUserData(prev => ({ ...prev, profile_image: updatedUser.profile_image }));
      setUser(prev => ({ ...prev, profile_image: updatedUser.profile_image }));
    } catch (error) {
      console.error('Failed to upload image:', error);
      alert('Failed to upload image');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Filter out empty strings for numeric fields
      const dataToSend = { ...formData };
      if (dataToSend.age === '') delete dataToSend.age;
      if (dataToSend.height_cm === '') delete dataToSend.height_cm;
      if (dataToSend.weight_kg === '') delete dataToSend.weight_kg;
      if (dataToSend.daily_sleep_goal === '') delete dataToSend.daily_sleep_goal;
      if (dataToSend.daily_water_goal === '') delete dataToSend.daily_water_goal;

      const response = await post('/profile', dataToSend);
      
      if (response && response.user) {
        setUser(response.user); // Update global user state
        // If token was updated (username change), it should be handled by the API hook or we might need to reload
        if (response.access_token) {
          localStorage.setItem('token', response.access_token);
        }
        navigate('/profile');
      }
    } catch (error) {
      console.error('Failed to update profile:', error);
      alert('Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
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
        <h1 className="text-2xl font-black">Edit Profile</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Avatar Upload Section */}
        <div className="flex flex-col items-center mb-6">
          <div className="relative group">
            <div className="w-24 h-24 rounded-full bg-gray-200 dark:bg-zinc-800 border-2 border-primary flex items-center justify-center overflow-hidden">
               {userData?.profile_image ? (
                  <img 
                  src={`${API_BASE_URL}${userData.profile_image}?t=${new Date().getTime()}`} 
                  alt="Profile" 
                  className="w-full h-full object-cover" 
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.parentElement.classList.add('fallback-icon');
                  }}
                />
              ) : (
                  <User size={48} className="text-primary" />
                )}
            </div>
            <button 
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center text-black shadow-lg hover:scale-110 transition-transform"
            >
              <Camera size={16} />
            </button>
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleImageUpload} 
              accept="image/*" 
              className="hidden" 
            />
          </div>
          <p className="mt-2 text-gray-500 dark:text-zinc-400 text-xs">Tap to change photo</p>
        </div>

        <GlassCard className="p-6 space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-bold text-gray-500 dark:text-zinc-500 flex items-center gap-2">
              <User size={16} />
              Username
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="w-full bg-white dark:bg-zinc-900/50 border border-gray-200 dark:border-zinc-800 rounded-xl p-4 text-gray-900 dark:text-white focus:outline-none focus:border-primary transition-colors"
              placeholder="Enter username"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
             <div className="space-y-2">
              <label className="text-sm font-bold text-gray-500 dark:text-zinc-500 flex items-center gap-2">
                Body Type
              </label>
              <select
                name="body_type"
                value={formData.body_type}
                onChange={handleChange}
                className="w-full bg-white dark:bg-zinc-900/50 border border-gray-200 dark:border-zinc-800 rounded-xl p-4 text-gray-900 dark:text-white focus:outline-none focus:border-primary transition-colors appearance-none"
              >
                <option value="">Select Body Type</option>
                <option value="Ectomorph">Ectomorph (Lean)</option>
                <option value="Mesomorph">Mesomorph (Athletic)</option>
                <option value="Endomorph">Endomorph (Broad)</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-bold text-gray-500 dark:text-zinc-500 flex items-center gap-2">
                Diet Goal
              </label>
              <select
                name="diet_goal"
                value={formData.diet_goal}
                onChange={handleChange}
                className="w-full bg-white dark:bg-zinc-900/50 border border-gray-200 dark:border-zinc-800 rounded-xl p-4 text-gray-900 dark:text-white focus:outline-none focus:border-primary transition-colors appearance-none"
              >
                <option value="">Select Goal</option>
                <option value="Lose Weight">Lose Weight</option>
                <option value="Build Muscle">Build Muscle</option>
                <option value="Maintain">Maintain</option>
                <option value="Improve Endurance">Improve Endurance</option>
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-bold text-gray-500 dark:text-zinc-500 flex items-center gap-2">
              Activity Level
            </label>
            <select
              name="activity_level"
              value={formData.activity_level}
              onChange={handleChange}
              className="w-full bg-white dark:bg-zinc-900/50 border border-gray-200 dark:border-zinc-800 rounded-xl p-4 text-gray-900 dark:text-white focus:outline-none focus:border-primary transition-colors appearance-none"
            >
              <option value="">Select Activity Level</option>
              <option value="Sedentary">Sedentary (Little/no exercise)</option>
              <option value="Light">Light (Exercise 1-3 days/week)</option>
              <option value="Moderate">Moderate (Exercise 3-5 days/week)</option>
              <option value="Active">Active (Exercise 6-7 days/week)</option>
              <option value="Very Active">Very Active (Physical job/training)</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-bold text-gray-500 dark:text-zinc-500 flex items-center gap-2">
                Sleep Goal (hrs)
              </label>
              <input
                type="number"
                name="daily_sleep_goal"
                value={formData.daily_sleep_goal}
                onChange={handleChange}
                step="0.5"
                className="w-full bg-white dark:bg-zinc-900/50 border border-gray-200 dark:border-zinc-800 rounded-xl p-4 text-gray-900 dark:text-white focus:outline-none focus:border-primary transition-colors"
                placeholder="8.0"
              />
            </div>
             <div className="space-y-2">
              <label className="text-sm font-bold text-gray-500 dark:text-zinc-500 flex items-center gap-2">
                Water Goal (ml)
              </label>
              <input
                type="number"
                name="daily_water_goal"
                value={formData.daily_water_goal}
                onChange={handleChange}
                step="50"
                className="w-full bg-white dark:bg-zinc-900/50 border border-gray-200 dark:border-zinc-800 rounded-xl p-4 text-gray-900 dark:text-white focus:outline-none focus:border-primary transition-colors"
                placeholder="2000"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-bold text-gray-500 dark:text-zinc-500 flex items-center gap-2">
              <Mail size={16} />
              Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full bg-white dark:bg-zinc-900/50 border border-gray-200 dark:border-zinc-800 rounded-xl p-4 text-gray-900 dark:text-white focus:outline-none focus:border-primary transition-colors"
              placeholder="Enter email"
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-bold text-gray-500 dark:text-zinc-500 flex items-center gap-2">
                <Calendar size={16} />
                Age
              </label>
              <input
                type="number"
                name="age"
                value={formData.age}
                onChange={handleChange}
                className="w-full bg-white dark:bg-zinc-900/50 border border-gray-200 dark:border-zinc-800 rounded-xl p-4 text-gray-900 dark:text-white focus:outline-none focus:border-primary transition-colors"
                placeholder="Age"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-bold text-gray-500 dark:text-zinc-500 flex items-center gap-2">
                <Ruler size={16} />
                Height (cm)
              </label>
              <input
                type="number"
                name="height_cm"
                value={formData.height_cm}
                onChange={handleChange}
                className="w-full bg-white dark:bg-zinc-900/50 border border-gray-200 dark:border-zinc-800 rounded-xl p-4 text-gray-900 dark:text-white focus:outline-none focus:border-primary transition-colors"
                placeholder="cm"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-bold text-gray-500 dark:text-zinc-500 flex items-center gap-2">
                <Weight size={16} />
                Weight (kg)
              </label>
              <input
                type="number"
                name="weight_kg"
                value={formData.weight_kg}
                onChange={handleChange}
                className="w-full bg-white dark:bg-zinc-900/50 border border-gray-200 dark:border-zinc-800 rounded-xl p-4 text-gray-900 dark:text-white focus:outline-none focus:border-primary transition-colors"
                placeholder="kg"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-bold text-gray-500 dark:text-zinc-500 flex items-center gap-2">
              <FileText size={16} />
              Bio
            </label>
            <textarea
              name="bio"
              value={formData.bio}
              onChange={handleChange}
              rows="3"
              className="w-full bg-white dark:bg-zinc-900/50 border border-gray-200 dark:border-zinc-800 rounded-xl p-4 text-gray-900 dark:text-white focus:outline-none focus:border-primary transition-colors resize-none"
              placeholder="Tell us about yourself..."
            />
          </div>
        </GlassCard>

        <GradientButton 
          type="submit" 
          disabled={loading}
          className="w-full flex items-center justify-center gap-2"
        >
          <Save size={20} />
          {loading ? 'Saving...' : 'Save Changes'}
        </GradientButton>
      </form>
    </div>
  );
};

export default EditProfile;
