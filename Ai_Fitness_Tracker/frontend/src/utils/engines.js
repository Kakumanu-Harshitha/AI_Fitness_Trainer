/**
 * AI Engines ported from mobile application
 * Includes: PostureScoreSystem, ExerciseStateMachine, CoachEngine, AnalyticsEngine
 */

/**
 * PostureScoreSystem - Analyzes pose landmarks and calculates posture scores
 */
export class PostureScoreSystem {
  constructor() {
    this.history = [];
    this.riskThresholds = {
      kneeValgus: 15,
      backRounding: 20,
      shoulderImbalance: 15,
    };
  }

  reset() {
    this.history = [];
  }

  calculateAngle(a, b, c) {
    if (!a || !b || !c) return 0;
    const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
    let angle = Math.abs((radians * 180.0) / Math.PI);
    if (angle > 180.0) angle = 360 - angle;
    return angle;
  }

  update(landmarks) {
    if (!landmarks || landmarks.length < 33) {
      return { total: 0, risks: [], jointScores: {} };
    }

    const scores = {};
    const risks = [];

    // Key landmark indices (MediaPipe Pose)
    const LEFT_SHOULDER = 11;
    const RIGHT_SHOULDER = 12;
    const LEFT_HIP = 23;
    const RIGHT_HIP = 24;
    const LEFT_KNEE = 25;
    const RIGHT_KNEE = 26;
    const LEFT_ANKLE = 27;
    const RIGHT_ANKLE = 28;

    // 1. Knee Alignment (Valgus Check)
    const leftKneeAngle = this.calculateAngle(
      landmarks[LEFT_HIP],
      landmarks[LEFT_KNEE],
      landmarks[LEFT_ANKLE]
    );
    const rightKneeAngle = this.calculateAngle(
      landmarks[RIGHT_HIP],
      landmarks[RIGHT_KNEE],
      landmarks[RIGHT_ANKLE]
    );

    scores.leftKnee = this.scoreJoint(leftKneeAngle, 170, 180);
    scores.rightKnee = this.scoreJoint(rightKneeAngle, 170, 180);

    if (scores.leftKnee < 70) risks.push({ type: 'Knee Valgus', joint: 'left_knee' });
    if (scores.rightKnee < 70) risks.push({ type: 'Knee Valgus', joint: 'right_knee' });

    // 2. Hip Alignment
    const hipDistance = Math.abs(landmarks[LEFT_HIP].y - landmarks[RIGHT_HIP].y);
    scores.hip = hipDistance < 0.05 ? 100 : Math.max(0, 100 - hipDistance * 500);

    // 3. Back Posture (Shoulder-Hip alignment)
    const shoulderMidY = (landmarks[LEFT_SHOULDER].y + landmarks[RIGHT_SHOULDER].y) / 2;
    const hipMidY = (landmarks[LEFT_HIP].y + landmarks[RIGHT_HIP].y) / 2;
    const backAngle = Math.abs(shoulderMidY - hipMidY);
    scores.back = backAngle > 0.3 ? Math.max(0, 100 - (backAngle - 0.3) * 200) : 100;

    if (scores.back < 70) risks.push({ type: 'Back Rounding', joint: 'spine' });

    // 4. Shoulder Symmetry
    const shoulderDiff = Math.abs(landmarks[LEFT_SHOULDER].y - landmarks[RIGHT_SHOULDER].y);
    scores.shoulder = shoulderDiff < 0.03 ? 100 : Math.max(0, 100 - shoulderDiff * 1000);

    // Calculate total score
    const jointScores = Object.values(scores);
    const total = jointScores.reduce((sum, score) => sum + score, 0) / jointScores.length;

    const result = {
      total: Math.round(total),
      risks,
      jointScores: scores,
    };

    this.history.push(result);
    return result;
  }

  scoreJoint(angle, idealMin, idealMax) {
    if (angle >= idealMin && angle <= idealMax) return 100;
    const deviation = Math.min(Math.abs(angle - idealMin), Math.abs(angle - idealMax));
    return Math.max(0, 100 - deviation * 2);
  }

  getHistory() {
    return this.history;
  }
}

/**
 * ExerciseStateMachine - Manages exercise states and rep counting
 */
export class ExerciseStateMachine {
  constructor(exerciseName = 'squat') {
    this.exerciseName = exerciseName.toLowerCase();
    this.repCount = 0;
    this.phase = 'START'; // 'START', 'DOWN', 'UP'
    this.holdStartTime = null;
    this.isFormValid = true;
    this.thresholds = this.getThresholds(this.exerciseName);
    this.history = {
      angles: [],
      maxHistory: 5
    };
    this.confidenceThreshold = 0.3; // Lowered from 0.5 for better detection in varying light
  }

  reset(exerciseName) {
    this.exerciseName = (exerciseName || this.exerciseName).toLowerCase();
    this.repCount = 0;
    this.phase = 'START';
    this.holdStartTime = null;
    this.isFormValid = true;
    this.thresholds = this.getThresholds(this.exerciseName);
    this.history.angles = [];
  }

  getThresholds(exercise) {
    const thresholds = {
      squat: { 
        downAngle: 110, // Relaxed from 100 for better detection
        upAngle: 150,   // Relaxed from 160 for better detection
        type: 'rep',
        joints: [23, 25, 27, 24, 26, 28] // Hips, Knees, Ankles
      },
      squats: { 
        downAngle: 110, 
        upAngle: 150, 
        type: 'rep',
        joints: [23, 25, 27, 24, 26, 28]
      },
      pushup: { 
        downAngle: 100, // Relaxed from 90
        upAngle: 140,   // Relaxed from 150
        type: 'rep',
        joints: [11, 13, 15, 12, 14, 16] // Shoulders, Elbows, Wrists
      },
      pushups: { 
        downAngle: 100, 
        upAngle: 140, 
        type: 'rep',
        joints: [11, 13, 15, 12, 14, 16]
      },
      lunge: { 
        downAngle: 110, 
        upAngle: 150, 
        type: 'rep',
        joints: [23, 25, 27, 24, 26, 28]
      },
      plank: { 
        type: 'time', 
        joints: [11, 23, 25, 27], // Shoulder, Hip, Knee, Ankle (Side profile)
        maxAngleDeviation: 20 // Max deviation from straight line
      },
      tree: {
        type: 'time',
        joints: [23, 25, 27, 24, 26, 28], // Both legs
        minKneeAngle: 100 // One knee must be bent
      }
    };
    return thresholds[exercise] || thresholds.squat;
  }

  update(landmarks) {
    if (!landmarks || landmarks.length < 33) {
      return { repCount: this.repCount, phase: this.phase, repDetected: false, isValid: false };
    }

    // Check confidence/visibility
    const requiredJoints = this.thresholds.joints || [];
    const lowConfidenceJoints = requiredJoints.filter(idx => (landmarks[idx]?.score || 0) < this.confidenceThreshold);
    
    if (lowConfidenceJoints.length > 0) {
      if (this.thresholds.type === 'time') this.holdStartTime = null; // Reset timer on poor visibility
      return { 
        repCount: this.repCount, 
        phase: this.phase, 
        repDetected: false, 
        isValid: false, 
        message: `Adjust camera - joints low confidence: ${lowConfidenceJoints.join(', ')}` 
      };
    }

    if (this.thresholds.type === 'rep') {
      return this.updateRepExercise(landmarks);
    } else {
      return this.updateTimeExercise(landmarks);
    }
  }

  updateRepExercise(landmarks) {
    let repDetected = false;
    let angle = 0;

    if (this.exerciseName === 'squat' || this.exerciseName === 'lunge' || this.exerciseName === 'squats') {
      const leftAngle = this.calculateAngle(landmarks[23], landmarks[25], landmarks[27]);
      const rightAngle = this.calculateAngle(landmarks[24], landmarks[26], landmarks[28]);
      angle = Math.min(leftAngle, rightAngle);
      // Log for debugging
      if (this.repCount === 0 && this.phase === 'START' && Math.random() > 0.99) {
          console.log(`[Exercise] ${this.exerciseName} detection: left=${Math.round(leftAngle)}, right=${Math.round(rightAngle)}`);
      }
    } else if (this.exerciseName === 'pushup' || this.exerciseName === 'pushups') {
      const leftAngle = this.calculateAngle(landmarks[11], landmarks[13], landmarks[15]);
      const rightAngle = this.calculateAngle(landmarks[12], landmarks[14], landmarks[16]);
      angle = Math.min(leftAngle, rightAngle);
    } else {
      // Fallback or other exercises (e.g. squats if name is slightly different)
      const leftAngle = this.calculateAngle(landmarks[23], landmarks[25], landmarks[27]);
      const rightAngle = this.calculateAngle(landmarks[24], landmarks[26], landmarks[28]);
      angle = Math.min(leftAngle, rightAngle);
    }

    // Smoothing
    this.history.angles.push(angle);
    if (this.history.angles.length > this.history.maxHistory) this.history.angles.shift();
    const smoothAngle = this.history.angles.reduce((a, b) => a + b, 0) / this.history.angles.length;

    if (Math.abs(smoothAngle - angle) > 5) {
        // console.log(`[Exercise] ${this.exerciseName} angle: ${Math.round(angle)}, smooth: ${Math.round(smoothAngle)}`);
    }

    // State Machine: START -> DOWN -> UP -> +1
    // START: Standing/Initial position
    // DOWN: Reached target depth
    // UP: Returned to start position

    if (this.phase === 'START' && smoothAngle > this.thresholds.upAngle) {
      // Valid start position
      this.isFormValid = true;
    }

    if (smoothAngle < this.thresholds.downAngle) {
      if (this.phase === 'START') {
        this.phase = 'DOWN';
        console.log(`[Exercise] ${this.exerciseName} phase: DOWN (angle: ${Math.round(smoothAngle)})`);
      }
    } else if (smoothAngle > this.thresholds.upAngle) {
      if (this.phase === 'DOWN') {
        this.repCount++;
        this.phase = 'START';
        repDetected = true;
        console.log(`[Exercise] ${this.exerciseName} phase: UP (+1 rep: ${this.repCount}, angle: ${Math.round(smoothAngle)})`);
      }
    }

    return { 
      repCount: this.repCount, 
      phase: this.phase, 
      repDetected, 
      isValid: this.isFormValid,
      angle: Math.round(smoothAngle)
    };
  }

  updateTimeExercise(landmarks) {
    let isValid = false;
    const now = Date.now();

    if (this.exerciseName === 'plank') {
      // Check if shoulder, hip, knee, and ankle are roughly in a straight line (180 deg)
      const hipAngle = this.calculateAngle(landmarks[11], landmarks[23], landmarks[25]);
      const kneeAngle = this.calculateAngle(landmarks[23], landmarks[25], landmarks[27]);
      
      // Plank is valid if body is straight (e.g., angles between 150 and 210)
      isValid = Math.abs(180 - hipAngle) < this.thresholds.maxAngleDeviation && 
                Math.abs(180 - kneeAngle) < this.thresholds.maxAngleDeviation;
    } else if (this.exerciseName === 'tree') {
      const leftKnee = this.calculateAngle(landmarks[23], landmarks[25], landmarks[27]);
      const rightKnee = this.calculateAngle(landmarks[24], landmarks[26], landmarks[28]);
      
      // One leg must be relatively straight, the other bent
      const oneLegStraight = leftKnee > 160 || rightKnee > 160;
      const oneLegBent = leftKnee < 130 || rightKnee < 130;
      isValid = oneLegStraight && oneLegBent;
    } else {
      // Fallback for unknown time-based exercises
      isValid = true; 
    }

    if (isValid) {
      if (!this.holdStartTime) {
        this.holdStartTime = now;
        console.log(`[Exercise] ${this.exerciseName} started holding`);
      }
    } else {
      if (this.holdStartTime) {
        this.holdStartTime = null;
        console.log(`[Exercise] ${this.exerciseName} form broken - timer reset`);
      }
    }

    const holdDuration = this.holdStartTime ? Math.floor((now - this.holdStartTime) / 1000) : 0;

    return { 
      repCount: holdDuration, // We reuse repCount for time in UI
      phase: isValid ? 'HOLDING' : 'BREAK',
      repDetected: false,
      isValid,
      duration: holdDuration
    };
  }

  calculateAngle(a, b, c) {
    if (!a || !b || !c) return 0;
    const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
    let angle = Math.abs((radians * 180.0) / Math.PI);
    if (angle > 180.0) angle = 360 - angle;
    return angle;
  }

  getRepCount() {
    return this.repCount;
  }
}

/**
 * CoachEngine - Provides AI coaching feedback
 */
export class CoachEngine {
  constructor(persona = 'supportive') {
    this.memory = [];
    this.lastAdviceTimestamp = Date.now();
    this.lastRiskTimestamp = 0;
    this.adviceInterval = 10000; // 10 seconds for general advice
    this.riskInterval = 5000;    // 5 seconds for critical feedback
    this.sessionHistory = {
      scores: [],
      risks: [],
    };
    this.persona = persona;
    this.personaTemplates = {
      supportive: {
        fatigue: "Fatigue detected. Focus on controlled movements, don't rush.",
        valgus: "Your knees are consistently caving. Push them OUT!",
        rounding: "Watch your lower back. Keep that chest proud!",
        excellent: [
          "Perfect form! You're crushing this set.",
          "Incredible consistency. Keep it up!",
          "Your technique is elite level. Stay focused.",
        ],
        progress: (avg) => `Session average: ${avg}%. Stay strong!`,
      },
      drill_sergeant: {
        fatigue: "YOUR FORM IS SLIPPING! DON'T YOU DARE QUIT NOW! FIX IT!",
        valgus: "KNEES OUT! STOP WEAKENING YOUR STANCE, SOLDIER!",
        rounding: "EYES UP! CHEST OUT! STOP SLUMPING LIKE A COWARD!",
        excellent: [
          "THAT'S WHAT I'M TALKING ABOUT! EMBRACE THE PAIN!",
          "UNSTOPPABLE! KEEP THAT INTENSITY!",
          "EXCELLENT WORK! NOW DO IT AGAIN, FASTER!",
        ],
        progress: (avg) => `${avg}% AVERAGE? YOU CAN DO BETTER THAN THAT! MOVE!`,
      },
      zen_coach: {
        fatigue: "Your body is speaking to you. Breathe deep and find your center again.",
        valgus: "Mindfully guide your knees outward. Find your balance.",
        rounding: "Lengthen your spine. Let your breath support your posture.",
        excellent: [
          "Beautiful alignment. You are in perfect harmony with your movement.",
          "Steady and mindful. Your focus is inspiring.",
          "Feel the strength in your stillness and flow. Well done.",
        ],
        progress: (avg) => `Your average stability is ${avg}%. You are blossoming.`,
      }
    };
  }

  setPersona(persona) {
    if (this.personaTemplates[persona]) {
      this.persona = persona;
    }
  }

  reset() {
    this.sessionHistory = { scores: [], risks: [] };
    this.lastAdviceTimestamp = Date.now();
    this.lastRiskTimestamp = 0;
  }

  update(scoreData) {
    if (scoreData) {
      this.sessionHistory.scores.push(scoreData.total);
      if (scoreData.risks && scoreData.risks.length > 0) {
        this.sessionHistory.risks.push(...scoreData.risks);
      }
    }

    const now = Date.now();
    
    // 1. Check for immediate risks first (higher priority)
    if (now - this.lastRiskTimestamp > this.riskInterval) {
      const riskAdvice = this.checkImmediateRisks();
      if (riskAdvice) {
        this.lastRiskTimestamp = now;
        // Also push back general advice to avoid overlap
        this.lastAdviceTimestamp = now; 
        return riskAdvice;
      }
    }

    // 2. Periodic encouragement/progress
    if (now - this.lastAdviceTimestamp > this.adviceInterval) {
      this.lastAdviceTimestamp = now;
      return this.generateGeneralAdvice();
    }
    return null;
  }

  checkImmediateRisks() {
    const recentRisks = this.sessionHistory.risks.slice(-5);
    if (recentRisks.length === 0) return null;

    const templates = this.personaTemplates[this.persona] || this.personaTemplates.supportive;

    // Check for knee valgus (most critical)
    const valgusCount = recentRisks.filter((r) => r.type === 'Knee Valgus').length;
    if (valgusCount >= 2) return templates.valgus;

    // Check for back rounding
    const roundingCount = recentRisks.filter((r) => r.type === 'Back Rounding').length;
    if (roundingCount >= 2) return templates.rounding;

    return null;
  }

  generateGeneralAdvice() {
    const scores = this.sessionHistory.scores;
    if (scores.length < 2) return null;

    const recentScores = scores.slice(-3);
    const recentAvg = recentScores.reduce((a, b) => a + b, 0) / recentScores.length;
    const templates = this.personaTemplates[this.persona] || this.personaTemplates.supportive;

    // 1. Fatigue Detection
    if (scores.length >= 10) {
      const initialAvg = scores.slice(0, 5).reduce((a, b) => a + b, 0) / 5;
      if (recentAvg < initialAvg - 15) {
        return templates.fatigue;
      }
    }

    // 2. Positive Reinforcement
    if (recentAvg > 92) {
      const encouragements = templates.excellent;
      return encouragements[Math.floor(Math.random() * encouragements.length)];
    }

    // 3. General Progress
    if (scores.length % 10 === 0) {
      const totalAvg = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
      return templates.progress(totalAvg);
    }

    return null;
  }

  getSessionStats() {
    const scores = this.sessionHistory.scores;
    if (scores.length === 0) return null;

    return {
      average: Math.round(scores.reduce((a, b) => a + b, 0) / scores.length),
      best: Math.max(...scores),
      worst: Math.min(...scores),
      totalRisks: this.sessionHistory.risks.length,
    };
  }
}

/**
 * AnalyticsEngine - Generates workout analytics
 */
export class AnalyticsEngine {
  constructor() {
    this.workoutHistory = [];
  }

  addWorkout(workoutData) {
    this.workoutHistory.push({
      ...workoutData,
      timestamp: Date.now(),
    });
  }

  getFatigueData(postureHistory) {
    if (!postureHistory || postureHistory.length === 0) return [];
    return postureHistory.map((h, i) => ({
      x: i + 1,
      y: h.total || h,
    }));
  }

  getJointStressData(postureHistory) {
    if (!postureHistory || postureHistory.length === 0) {
      return [0, 0, 0, 0, 0];
    }

    const jointStress = {
      knee: 0,
      hip: 0,
      back: 0,
      shoulder: 0,
      ankle: 0,
    };

    postureHistory.forEach((h) => {
      if (h.jointScores) {
        for (let joint in h.jointScores) {
          const stress = 100 - h.jointScores[joint];
          if (joint.toLowerCase().includes('knee')) jointStress.knee = Math.max(jointStress.knee, stress);
          if (joint.toLowerCase().includes('hip')) jointStress.hip = Math.max(jointStress.hip, stress);
          if (joint.toLowerCase().includes('back')) jointStress.back = Math.max(jointStress.back, stress);
          if (joint.toLowerCase().includes('shoulder')) jointStress.shoulder = Math.max(jointStress.shoulder, stress);
          if (joint.toLowerCase().includes('ankle')) jointStress.ankle = Math.max(jointStress.ankle, stress);
        }
      }
    });

    return [
      jointStress.knee,
      jointStress.hip,
      jointStress.back,
      jointStress.shoulder,
      jointStress.ankle,
    ];
  }

  getBestWorstRep(repScores) {
    if (!repScores || repScores.length === 0) return { best: 0, worst: 0 };
    return {
      best: Math.max(...repScores),
      worst: Math.min(...repScores),
    };
  }

  getFatigueRisk(postureHistory) {
    if (!postureHistory || postureHistory.length < 5) return 'LOW';

    const scores = postureHistory.map((h) => h.total || h);
    const last5 = scores.slice(-5);
    const avgLast5 = last5.reduce((a, b) => a + b, 0) / last5.length;
    const overallAvg = scores.reduce((a, b) => a + b, 0) / scores.length;

    if (avgLast5 < overallAvg - 15) return 'HIGH';
    if (avgLast5 < overallAvg - 5) return 'MODERATE';
    return 'LOW';
  }

  getAverageStability(postureHistory) {
    if (!postureHistory || postureHistory.length === 0) return 0;
    const scores = postureHistory.map((h) => h.total || h);
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  }
}
