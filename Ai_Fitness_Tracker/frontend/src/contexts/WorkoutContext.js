import React, { createContext, useContext, useState, useRef, useCallback } from 'react';
import { PostureScoreSystem, ExerciseStateMachine, CoachEngine } from '../utils/engines';

const WorkoutContext = createContext(undefined);

export const useWorkout = () => {
  const context = useContext(WorkoutContext);
  if (!context) {
    throw new Error('useWorkout must be used within WorkoutProvider');
  }
  return context;
};

const INITIAL_STATS = {
  reps: 0,
  time: 0,
  calories: 0,
  avgScore: 100,
  scores: [],
};

export const WorkoutProvider = ({ children }) => {
  const [isActive, setIsActive] = useState(false);
  const [currentExercise, setCurrentExercise] = useState(null);
  const [routine, setRoutine] = useState(null);
  const [sessionStats, setSessionStats] = useState(INITIAL_STATS);
  const [phase, setPhase] = useState('calibration');

  // AI Engine Refs
  const scoreSystem = useRef(new PostureScoreSystem());
  const stateMachine = useRef(null);
  const coach = useRef(new CoachEngine());

  const startWorkout = useCallback((workoutRoutine, exercise = 'squats') => {
    try {
      setIsActive(true);
      setRoutine(workoutRoutine);
      setCurrentExercise(exercise);
      setPhase('calibration');

      // Initialize engines
      scoreSystem.current.reset();
      stateMachine.current = new ExerciseStateMachine(exercise);
      coach.current.reset();

      setSessionStats(INITIAL_STATS);
    } catch (error) {
      console.error('[WorkoutContext] Start error:', error);
    }
  }, []);

  const updateWorkoutStats = useCallback((landmarks) => {
    if (!isActive || !stateMachine.current) return null;

    try {
      // Update posture score
      const scoreData = scoreSystem.current.update(landmarks);

      // Update rep count
      const repData = stateMachine.current.update(landmarks);

      // Get coach advice
      const advice = coach.current.update(scoreData);

    // Update session stats
    setSessionStats(prev => {
      const newScore = scoreData.total;
      // Only include score if it's non-zero (landmarks detected)
      const newScores = newScore > 0 ? [...prev.scores, newScore] : prev.scores;
      const currentAvg = newScores.length > 0 
        ? Math.round(newScores.reduce((a, b) => a + b, 0) / newScores.length)
        : prev.avgScore;

      return {
        ...prev,
        reps: repData.repCount,
        avgScore: currentAvg,
        scores: newScores,
      };
    });

      return {
        score: scoreData,
        reps: repData,
        advice,
      };
    } catch (error) {
      console.error('[WorkoutContext] Update error:', error);
      return null;
    }
  }, [isActive]);

  const incrementTime = useCallback(() => {
    setSessionStats(prev => ({
      ...prev,
      time: prev.time + 1,
      calories: prev.calories + (phase === 'workout' ? 0.2 : 0),
    }));
  }, [phase]);

  const changeExercise = useCallback((exercise) => {
    try {
      setCurrentExercise(exercise);
      stateMachine.current = new ExerciseStateMachine(exercise);
    } catch (error) {
      console.error('[WorkoutContext] Change exercise error:', error);
    }
  }, []);

  const pauseWorkout = useCallback(() => {
    setPhase('rest');
  }, []);

  const resumeWorkout = useCallback(() => {
    setPhase('workout');
  }, []);

  const completeWorkout = useCallback(() => {
    setIsActive(false);
    setPhase('complete');

    // avgScore is already being updated incrementally in updateWorkoutStats
    return sessionStats;
  }, [sessionStats]);

  const resetWorkout = useCallback(() => {
    setIsActive(false);
    setCurrentExercise(null);
    setRoutine(null);
    setPhase('calibration');
    setSessionStats(INITIAL_STATS);
  }, []);

  const value = {
    isActive,
    currentExercise,
    routine,
    sessionStats,
    phase,
    setPhase,
    startWorkout,
    updateWorkoutStats,
    incrementTime,
    changeExercise,
    pauseWorkout,
    resumeWorkout,
    completeWorkout,
    resetWorkout,
    scoreSystem: scoreSystem.current,
    stateMachine: stateMachine.current,
    coach: coach.current,
  };

  return <WorkoutContext.Provider value={value}>{children}</WorkoutContext.Provider>;
};
