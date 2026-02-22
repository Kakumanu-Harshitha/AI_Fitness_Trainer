import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowRight, 
  ArrowLeft, 
  Check, 
  User, 
  Dumbbell, 
  Shield, 
  Armchair, 
  Footprints, 
  Bike, 
  Zap, 
  TrendingDown, 
  Activity, 
  TrendingUp, 
  Moon, 
  Droplets,
  Brain
} from 'lucide-react';
import GlassCard from '../components/GlassCard';
import GradientButton from '../components/GradientButton';
import { useApi } from '../hooks/useApi';
import { useApp } from '../contexts/AppContext';

const steps = [
  {
    id: 'intro',
    type: 'intro',
    title: "Let's Personalize Your Experience",
    description: "To create the perfect plan for you, our AI needs to know a bit more about your lifestyle and goals.",
    buttonText: "Start Assessment"
  },
  {
    id: 'body_type',
    type: 'selection',
    question: "What's your body type?",
    description: "This helps us tailor your workout intensity and volume.",
    options: [
      { value: 'Ectomorph', label: 'Ectomorph', desc: 'Lean frame, difficulty building muscle', icon: User },
      { value: 'Mesomorph', label: 'Mesomorph', desc: 'Athletic build, builds muscle easily', icon: Dumbbell },
      { value: 'Endomorph', label: 'Endomorph', desc: 'Broad build, gains weight easily', icon: Shield }
    ]
  },
  {
    id: 'activity_level',
    type: 'selection',
    question: "How active are you?",
    description: "Be honest! This determines your baseline calorie needs.",
    options: [
      { value: 'Sedentary', label: 'Sedentary', desc: 'Desk job, little to no exercise', icon: Armchair },
      { value: 'Light', label: 'Lightly Active', desc: 'Light exercise 1-3 days/week', icon: Footprints },
      { value: 'Moderate', label: 'Moderately Active', desc: 'Moderate exercise 3-5 days/week', icon: Bike },
      { value: 'Active', label: 'Very Active', desc: 'Hard exercise 6-7 days/week', icon: Zap }
    ]
  },
  {
    id: 'diet_goal',
    type: 'selection',
    question: "What's your main goal?",
    description: "We'll adjust your nutrition and workout plans accordingly.",
    options: [
      { value: 'Lose Weight', label: 'Lose Weight', desc: 'Burn fat & get lean', icon: TrendingDown },
      { value: 'Maintain', label: 'Maintain', desc: 'Stay fit & healthy', icon: Activity },
      { value: 'Build Muscle', label: 'Build Muscle', desc: 'Gain mass & strength', icon: TrendingUp }
    ]
  },
  {
    id: 'goals',
    type: 'inputs',
    question: "Daily Targets",
    description: "Set your daily hydration and sleep goals for optimal recovery.",
    inputs: [
      { id: 'daily_sleep_goal', label: 'Sleep Goal (Hours)', icon: Moon, min: 4, max: 12, step: 0.5, default: 8.0 },
      { id: 'daily_water_goal', label: 'Water Goal (ml)', icon: Droplets, min: 1000, max: 5000, step: 100, default: 2500 }
    ]
  },
  {
    id: 'health_context',
    type: 'text_inputs',
    question: "Health & Preferences",
    description: "Tell us about any injuries or dietary preferences.",
    inputs: [
      { id: 'injuries', label: 'Injuries (if any)', placeholder: 'e.g. Lower back pain, knee issues...', icon: Shield },
      { id: 'dietary_preferences', label: 'Dietary Preferences', placeholder: 'e.g. Vegan, Keto, Gluten-free...', icon: Droplets }
    ]
  },
  {
    id: 'processing',
    type: 'processing',
    title: "AI Analysis in Progress",
    description: "Analyzing your profile to generate personalized recommendations...",
  }
];

const LifestyleQuiz = () => {
  const navigate = useNavigate();
  const { post } = useApi();
  const { refreshUserData } = useApp();
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    body_type: '',
    activity_level: '',
    diet_goal: '',
    daily_sleep_goal: 8.0,
    daily_water_goal: 2500,
    injuries: '',
    dietary_preferences: ''
  });
  const [loading, setLoading] = useState(false);

  const handleNext = async () => {
    if (currentStep < steps.length - 1) {
      // If moving to processing step, submit data
      if (steps[currentStep + 1].type === 'processing') {
        setCurrentStep(prev => prev + 1);
        await submitData();
      } else {
        setCurrentStep(prev => prev + 1);
      }
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleSelect = (value) => {
    const field = steps[currentStep].id;
    setFormData(prev => ({ ...prev, [field]: value }));
    // Auto advance for selection steps after a short delay for better UX
    setTimeout(() => {
        handleNext();
    }, 300);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: parseFloat(value) }));
  };

  const handleTextInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const submitData = async () => {
    setLoading(true);
    try {
      // Simulate AI processing time
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      await post('/profile', formData);
      await refreshUserData();
      
      navigate('/dashboard');
    } catch (error) {
      console.error('Failed to update profile:', error);
      // Go back to previous step if error
      setCurrentStep(prev => prev - 1);
    } finally {
      setLoading(false);
    }
  };

  const currentStepData = steps[currentStep];
  const progress = ((currentStep) / (steps.length - 1)) * 100;

  // Render Intro Step
  if (currentStepData.type === 'intro') {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-black text-gray-900 dark:text-white p-6 flex flex-col items-center justify-center relative overflow-hidden transition-colors duration-300">
        {/* Background Gradients */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
          <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary/20 rounded-full blur-[100px]" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-500/20 rounded-full blur-[100px]" />
        </div>

        <GlassCard className="w-full max-w-md z-10 text-center py-12 px-6">
          <div className="w-20 h-20 bg-gray-100 dark:bg-zinc-800 rounded-full flex items-center justify-center mx-auto mb-6 border border-gray-200 dark:border-zinc-700">
            <Brain size={40} className="text-primary animate-pulse" />
          </div>
          <h1 className="text-3xl font-black mb-4 text-gray-900 dark:text-white">
            {currentStepData.title}
          </h1>
          <p className="text-gray-500 dark:text-zinc-400 mb-8 text-lg leading-relaxed">
            {currentStepData.description}
          </p>
          <GradientButton onClick={handleNext} className="w-full py-4 text-lg">
            {currentStepData.buttonText} <ArrowRight size={20} className="ml-2" />
          </GradientButton>
        </GlassCard>
      </div>
    );
  }

  // Render Processing Step
  if (currentStepData.type === 'processing') {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-black text-gray-900 dark:text-white p-6 flex flex-col items-center justify-center relative transition-colors duration-300">
        <div className="text-center">
          <div className="relative w-24 h-24 mx-auto mb-8">
            <div className="absolute inset-0 border-4 border-gray-200 dark:border-zinc-800 rounded-full"></div>
            <div className="absolute inset-0 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            <Brain size={32} className="absolute inset-0 m-auto text-primary animate-pulse" />
          </div>
          <h2 className="text-2xl font-bold mb-2">{currentStepData.title}</h2>
          <p className="text-gray-500 dark:text-zinc-400">{currentStepData.description}</p>
        </div>
      </div>
    );
  }

  // Render Question Steps
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-black text-gray-900 dark:text-white p-6 flex flex-col relative transition-colors duration-300">
      {/* Header */}
      <div className="w-full max-w-md mx-auto mb-8 flex items-center justify-between">
        <button 
            onClick={handleBack}
            className="p-2 bg-white dark:bg-zinc-900 rounded-full text-gray-400 dark:text-zinc-400 hover:text-gray-900 dark:hover:text-white transition-colors border border-gray-200 dark:border-transparent"
        >
            <ArrowLeft size={20} />
        </button>
        <div className="flex-1 mx-4 bg-gray-200 dark:bg-zinc-900 h-2 rounded-full overflow-hidden">
            <div 
                className="h-full bg-primary transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
            />
        </div>
        <div className="text-xs text-gray-500 dark:text-zinc-500 font-mono">
            {currentStep}/{steps.length - 2}
        </div>
      </div>

      <div className="flex-1 flex flex-col justify-center max-w-md mx-auto w-full pb-10">
        <div className="mb-8">
            <h2 className="text-3xl font-bold mb-3">{currentStepData.question}</h2>
            <p className="text-gray-500 dark:text-zinc-400">{currentStepData.description}</p>
        </div>

        {currentStepData.type === 'selection' && (
            <div className="space-y-4">
                {currentStepData.options.map((option) => {
                    const Icon = option.icon;
                    const isSelected = formData[currentStepData.id] === option.value;
                    
                    return (
                        <button
                            key={option.value}
                            onClick={() => handleSelect(option.value)}
                            className={`w-full text-left p-5 rounded-2xl border transition-all duration-200 group relative overflow-hidden
                                ${isSelected 
                                    ? 'bg-primary/10 border-primary shadow-[0_0_20px_rgba(180,255,57,0.1)]' 
                                    : 'bg-white dark:bg-zinc-900/50 border-gray-200 dark:border-zinc-800 hover:border-gray-300 dark:hover:border-zinc-700 hover:bg-gray-50 dark:hover:bg-zinc-900'
                                }
                            `}
                        >
                            <div className="flex items-start gap-4 relative z-10">
                                <div className={`p-3 rounded-xl transition-colors ${isSelected ? 'bg-primary text-black' : 'bg-gray-100 dark:bg-zinc-800 text-gray-400 dark:text-zinc-400 group-hover:text-gray-900 dark:group-hover:text-white'}`}>
                                    <Icon size={24} />
                                </div>
                                <div className="flex-1">
                                    <h3 className={`text-lg font-bold mb-1 transition-colors ${isSelected ? 'text-gray-900 dark:text-white' : 'text-gray-700 dark:text-zinc-200'}`}>
                                        {option.label}
                                    </h3>
                                    <p className="text-sm text-gray-500 dark:text-zinc-500 leading-snug">
                                        {option.desc}
                                    </p>
                                </div>
                                {isSelected && (
                                    <div className="absolute top-4 right-4 text-primary">
                                        <Check size={20} />
                                    </div>
                                )}
                            </div>
                        </button>
                    );
                })}
            </div>
        )}

        {currentStepData.type === 'inputs' && (
            <div className="space-y-6">
                {currentStepData.inputs.map((input) => {
                    const Icon = input.icon;
                    return (
                        <GlassCard key={input.id} className="p-6">
                            <div className="flex items-center gap-3 mb-4">
                                <Icon className="text-primary" size={24} />
                                <span className="font-bold text-lg">{input.label}</span>
                            </div>
                            <div className="flex items-center gap-4">
                                <input 
                                    type="range"
                                    min={input.min}
                                    max={input.max}
                                    step={input.step}
                                    value={formData[input.id]}
                                    onChange={(e) => handleInputChange(input.id, e.target.value)}
                                    className="flex-1 h-2 bg-gray-200 dark:bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-primary"
                                />
                                <div className="min-w-[80px] text-right font-mono text-xl font-bold text-primary">
                                    {formData[input.id]}
                                </div>
                            </div>
                        </GlassCard>
                    );
                })}
                <GradientButton onClick={handleNext} className="w-full py-4 mt-8 text-lg font-bold">
                    Next <ArrowRight size={20} className="ml-2" />
                </GradientButton>
            </div>
        )}

        {currentStepData.type === 'text_inputs' && (
            <div className="space-y-6">
                {currentStepData.inputs.map((input) => {
                    const Icon = input.icon;
                    return (
                        <GlassCard key={input.id} className="p-6">
                            <div className="flex items-center gap-3 mb-4">
                                <Icon className="text-primary" size={24} />
                                <span className="font-bold text-lg">{input.label}</span>
                            </div>
                            <input 
                                type="text"
                                placeholder={input.placeholder}
                                value={formData[input.id]}
                                onChange={(e) => handleTextInputChange(input.id, e.target.value)}
                                className="w-full bg-white dark:bg-zinc-900/50 border border-gray-200 dark:border-zinc-700 rounded-xl p-4 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-zinc-500 focus:outline-none focus:border-primary transition-all"
                            />
                        </GlassCard>
                    );
                })}
                <GradientButton onClick={handleNext} className="w-full py-4 mt-8 text-lg font-bold">
                    Complete Profile <ArrowRight size={20} className="ml-2" />
                </GradientButton>
            </div>
        )}
      </div>
    </div>
  );
};

export default LifestyleQuiz;
