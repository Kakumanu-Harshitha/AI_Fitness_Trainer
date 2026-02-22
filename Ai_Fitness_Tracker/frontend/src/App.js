import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider, useApp } from './contexts/AppContext';
import { WorkoutProvider } from './contexts/WorkoutContext';
import Layout from './components/Layout';
import DuelManager from './components/DuelManager';
import NotificationToast from './components/NotificationToast';

// Lazy load screens for better initial load performance
const Login = lazy(() => import('./screens/Login'));
const Signup = lazy(() => import('./screens/Signup'));
const ForgotPassword = lazy(() => import('./screens/ForgotPassword'));
const ResetPassword = lazy(() => import('./screens/ResetPassword'));
const HomeDashboard = lazy(() => import('./screens/HomeDashboard'));
const Workouts = lazy(() => import('./screens/Workouts'));
const Stats = lazy(() => import('./screens/Stats'));
const Leaderboard = lazy(() => import('./screens/Leaderboard'));
const Profile = lazy(() => import('./screens/Profile'));
const LiveWorkout = lazy(() => import('./screens/LiveWorkout'));
const WorkoutSummary = lazy(() => import('./screens/WorkoutSummary'));
const Chat = lazy(() => import('./screens/Chat'));
const EditProfile = lazy(() => import('./screens/EditProfile'));
const Settings = lazy(() => import('./screens/Settings'));
const ChangePassword = lazy(() => import('./screens/ChangePassword'));
const LifestyleQuiz = lazy(() => import('./screens/LifestyleQuiz'));

const LoadingSpinner = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-black transition-colors duration-300">
    <div className="w-12 h-12 border-4 border-gray-200 dark:border-zinc-800 border-t-primary rounded-full animate-spin"></div>
  </div>
);

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useApp();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-black transition-colors duration-300">
        <div className="w-12 h-12 border-4 border-gray-200 dark:border-zinc-800 border-t-primary rounded-full animate-spin"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Suspense fallback={<LoadingSpinner />}><Login /></Suspense>} />
      <Route path="/signup" element={<Suspense fallback={<LoadingSpinner />}><Signup /></Suspense>} />
      <Route path="/forgot-password" element={<Suspense fallback={<LoadingSpinner />}><ForgotPassword /></Suspense>} />
      <Route path="/reset-password" element={<Suspense fallback={<LoadingSpinner />}><ResetPassword /></Suspense>} />
      
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/dashboard" element={<Suspense fallback={<LoadingSpinner />}><HomeDashboard /></Suspense>} />
        <Route path="/workouts" element={<Suspense fallback={<LoadingSpinner />}><Workouts /></Suspense>} />
        <Route path="/stats" element={<Suspense fallback={<LoadingSpinner />}><Stats /></Suspense>} />
        <Route path="/leaderboard" element={<Suspense fallback={<LoadingSpinner />}><Leaderboard /></Suspense>} />
        <Route path="/profile" element={<Suspense fallback={<LoadingSpinner />}><Profile /></Suspense>} />
        <Route path="/edit-profile" element={<Suspense fallback={<LoadingSpinner />}><EditProfile /></Suspense>} />
        <Route path="/settings" element={<Suspense fallback={<LoadingSpinner />}><Settings /></Suspense>} />
        <Route path="/change-password" element={<Suspense fallback={<LoadingSpinner />}><ChangePassword /></Suspense>} />
        <Route path="/chat/:username" element={<Suspense fallback={<LoadingSpinner />}><Chat /></Suspense>} />
      </Route>

      <Route 
        path="/lifestyle-quiz" 
        element={
          <ProtectedRoute>
            <Suspense fallback={<LoadingSpinner />}>
              <LifestyleQuiz />
            </Suspense>
          </ProtectedRoute>
        } 
      />

      <Route 
        path="/live-workout" 
        element={
          <ProtectedRoute>
            <Suspense fallback={<LoadingSpinner />}>
              <LiveWorkout />
            </Suspense>
          </ProtectedRoute>
        } 
      />

      <Route 
        path="/workout-summary" 
        element={
          <ProtectedRoute>
            <Suspense fallback={<LoadingSpinner />}>
              <WorkoutSummary />
            </Suspense>
          </ProtectedRoute>
        } 
      />
      
      <Route path="/" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
}

function App() {
  return (
    <AppProvider>
      <WorkoutProvider>
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <div className="min-h-screen bg-white dark:bg-black text-black dark:text-white transition-colors duration-300">
            <DuelManager />
            <NotificationToast />
            <AppRoutes />
          </div>
        </Router>
      </WorkoutProvider>
    </AppProvider>
  );
}

export default App;
