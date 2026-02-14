import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider, useApp } from './contexts/AppContext';
import { WorkoutProvider } from './contexts/WorkoutContext';
import Layout from './components/Layout';
import Login from './screens/Login';
import Signup from './screens/Signup';
import HomeDashboard from './screens/HomeDashboard';
import Workouts from './screens/Workouts';
import Stats from './screens/Stats';
import Leaderboard from './screens/Leaderboard';
import Profile from './screens/Profile';
import LiveWorkout from './screens/LiveWorkout';
import WorkoutSummary from './screens/WorkoutSummary';
import Chat from './screens/Chat';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useApp();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
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
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/dashboard" element={<HomeDashboard />} />
        <Route path="/workouts" element={<Workouts />} />
        <Route path="/stats" element={<Stats />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/chat/:username" element={<Chat />} />
      </Route>

      <Route 
        path="/live-workout" 
        element={
          <ProtectedRoute>
            <LiveWorkout />
          </ProtectedRoute>
        } 
      />

      <Route 
        path="/workout-summary" 
        element={
          <ProtectedRoute>
            <WorkoutSummary />
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
          <div className="min-h-screen bg-black text-white">
            <AppRoutes />
          </div>
        </Router>
      </WorkoutProvider>
    </AppProvider>
  );
}

export default App;
