import React, { createContext, useContext, useState, useRef, useCallback } from 'react';
import { PostureScoreSystem, ExerciseStateMachine, CoachEngine } from '../utils/engines';
import { YogaEngine, MeditationEngine } from '../utils/mindfulness';

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
  avgScore: 0,
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
      coach.current.reset();

      if (workoutRoutine?.type === 'mindfulness') {
        if (exercise.type === 'yoga') {
          stateMachine.current = new YogaEngine();
          stateMachine.current.setPose(exercise.name);
        } else if (exercise.type === 'meditation') {
          stateMachine.current = new MeditationEngine();
        }
      } else {
        stateMachine.current = new ExerciseStateMachine(exercise);
      }

      setSessionStats(INITIAL_STATS);
    } catch (error) {
      console.error('[WorkoutContext] Start error:', error);
    }
  }, []);

  const updateWorkoutStats = useCallback((landmarks) => {
    if (!isActive || !stateMachine.current) return null;

    try {
      let result = {};
      let advice = "";
      let newScore = 0;
      let newReps = sessionStats.reps;

      if (routine?.type === 'mindfulness') {
        // Mindfulness Logic
        const data = stateMachine.current.update(landmarks);
        
        if (currentExercise.type === 'yoga') {
          // data: { feedback, isCorrect, holdTime, score }
          newScore = data.score;
          newReps = Math.floor(data.holdTime); // Use hold time as "reps" for display
          advice = data.feedback;
        } else {
          // data: { feedback, breathRate, duration, isMeditating }
          newScore = 100; // Default score for meditation if detected
          newReps = data.breathRate;
          advice = data.feedback;
        }
        
        result = { score: { total: newScore }, reps: { repCount: newReps }, advice };
      } else {
        // Standard Workout Logic
        const scoreData = scoreSystem.current.update(landmarks);
        const repData = stateMachine.current.update(landmarks);
        advice = coach.current.update(scoreData);
        
        newScore = scoreData.total;
        newReps = repData.repCount;
        
        result = { score: scoreData, reps: repData, advice };
      }

      setSessionStats(prev => {
        const newScores = newScore > 0 ? [...prev.scores, newScore] : prev.scores;
        let currentAvg = prev.avgScore;
        if (newScores.length > 0) {
          currentAvg = Math.round(newScores.reduce((a, b) => a + b, 0) / newScores.length);
        }

        return {
          ...prev,
          reps: newReps,
          avgScore: currentAvg,
          scores: newScores,
        };
      });

      return result;
    } catch (error) {
      console.error('[WorkoutContext] Update error:', error);
      return null;
    }
  }, [isActive, routine, currentExercise, sessionStats.reps]);

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
