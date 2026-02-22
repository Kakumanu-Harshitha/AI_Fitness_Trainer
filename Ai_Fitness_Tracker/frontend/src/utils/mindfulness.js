
/**
 * AI Engines for Yoga and Meditation
 */

export class YogaEngine {
  constructor() {
    this.currentPose = null;
    this.feedback = "Get ready...";
    this.holdTime = 0;
    this.startTime = null;
    this.isHolding = false;
    this.scores = [];
    this.totalHoldTime = 0;
    this.lastUpdate = null;
  }

  setPose(poseName) {
    this.currentPose = poseName;
    this.reset();
  }

  reset() {
    this.feedback = "Get ready...";
    this.holdTime = 0;
    this.totalHoldTime = 0;
    this.startTime = null;
    this.lastUpdate = null;
    this.isHolding = false;
    this.scores = [];
  }

  calculateAngle(a, b, c) {
    if (!a || !b || !c) return 0;
    const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
    let angle = Math.abs((radians * 180.0) / Math.PI);
    if (angle > 180.0) angle = 360 - angle;
    return angle;
  }

  update(landmarks) {
    if (!landmarks || landmarks.length < 33) return { feedback: "No person detected" };

    let isCorrect = false;
    let feedback = "";
    let score = 0;

    if (this.currentPose === 'Warrior II') {
      const result = this.checkWarriorII(landmarks);
      isCorrect = result.isCorrect;
      feedback = result.feedback;
      score = result.score;
    } else if (this.currentPose === 'Tree Pose') {
      const result = this.checkTreePose(landmarks);
      isCorrect = result.isCorrect;
      feedback = result.feedback;
      score = result.score;
    }

    if (isCorrect) {
      if (!this.isHolding) {
        this.startTime = Date.now();
        this.isHolding = true;
      }
      const currentHold = (Date.now() - this.startTime) / 1000;
      // We want to track accumulated time if user breaks and restarts
      // But holdTime usually means "current continuous hold".
      // Let's return total accumulated time as "holdTime" for the workout stats?
      // No, for yoga usually you want to hold for X seconds.
      // If they break, they might restart.
      // Let's return accumulated total hold time as "holdTime" to simulate "reps" of seconds.
      if (this.lastUpdate) {
          const delta = (Date.now() - this.lastUpdate) / 1000;
          this.totalHoldTime += delta;
      }
      this.holdTime = currentHold;
      this.scores.push(score);
    } else {
      this.isHolding = false;
      this.startTime = null;
    }
    this.lastUpdate = Date.now();

    return {
      feedback,
      isCorrect,
      holdTime: Math.floor(this.totalHoldTime), // Return total accumulated time
      currentHoldTime: this.holdTime,
      score: this.scores.length > 0 ? Math.round(this.scores.reduce((a,b)=>a+b,0)/this.scores.length) : 0
    };
  }

  checkWarriorII(landmarks) {
    // Landmarks: 11/12 (Shoulders), 23/24 (Hips), 25/26 (Knees), 27/28 (Ankles), 15/16 (Wrists)
    const leftShoulder = landmarks[11];
    const rightShoulder = landmarks[12];
    const leftWrist = landmarks[15];
    const rightWrist = landmarks[16];
    const leftHip = landmarks[23];
    const leftKnee = landmarks[25];
    const leftAnkle = landmarks[27];
    const rightHip = landmarks[24];
    const rightKnee = landmarks[26];
    const rightAnkle = landmarks[28];

    // 1. Arms Horizontal
    const armDiff = Math.abs(leftWrist.y - leftShoulder.y) + Math.abs(rightWrist.y - rightShoulder.y);
    if (armDiff > 0.15) return { isCorrect: false, feedback: "Raise arms to shoulder height", score: 50 };

    // 2. Wide Stance
    const stanceWidth = Math.abs(leftAnkle.x - rightAnkle.x);
    if (stanceWidth < 0.3) return { isCorrect: false, feedback: "Widen your stance", score: 60 };

    // 3. Front Knee Bent (Assuming Left is Front)
    const leftKneeAngle = this.calculateAngle(leftHip, leftKnee, leftAnkle);
    const rightKneeAngle = this.calculateAngle(rightHip, rightKnee, rightAnkle);

    // Check which knee is bent (Front knee should be ~90, Back leg straight ~180)
    if (leftKneeAngle < 130 && rightKneeAngle > 160) {
      // Left is front
      if (leftKneeAngle > 110) return { isCorrect: false, feedback: "Bend front knee more", score: 70 };
    } else if (rightKneeAngle < 130 && leftKneeAngle > 160) {
      // Right is front
      if (rightKneeAngle > 110) return { isCorrect: false, feedback: "Bend front knee more", score: 70 };
    } else {
       return { isCorrect: false, feedback: "Bend one knee, keep other straight", score: 60 };
    }

    return { isCorrect: true, feedback: "Perfect Warrior II!", score: 100 };
  }

  checkTreePose(landmarks) {
    const leftHip = landmarks[23];
    const leftKnee = landmarks[25];
    const leftAnkle = landmarks[27];
    const rightHip = landmarks[24];
    const rightKnee = landmarks[26];
    const rightAnkle = landmarks[28];

    // Calculate knee angles
    const leftAngle = this.calculateAngle(leftHip, leftKnee, leftAnkle);
    const rightAngle = this.calculateAngle(rightHip, rightKnee, rightAnkle);

    // One leg should be straight (~180), one bent (< 90 usually for tree pose foot placement)
    let isLeftStraight = leftAngle > 160;
    let isRightStraight = rightAngle > 160;
    let isLeftBent = leftAngle < 120; // High foot placement
    let isRightBent = rightAngle < 120;

    if ((isLeftStraight && isRightBent) || (isRightStraight && isLeftBent)) {
       // Check balance (shoulders level)
       const shoulderDiff = Math.abs(landmarks[11].y - landmarks[12].y);
       if (shoulderDiff > 0.05) return { isCorrect: false, feedback: "Level your shoulders", score: 80 };
       
       return { isCorrect: true, feedback: "Great balance!", score: 100 };
    }

    return { isCorrect: false, feedback: "Place foot on inner thigh/calf", score: 60 };
  }
}

export class MeditationEngine {
  constructor() {
    this.shoulderHistory = [];
    this.noseHistory = [];
    this.breathCount = 0;
    this.startTime = null;
    this.lastBreathTime = Date.now();
    this.isMeditating = false;
    this.feedback = "Sit comfortably.";
  }

  update(landmarks) {
    if (!landmarks || landmarks.length < 33) return { feedback: "No person detected" };

    if (!this.startTime) this.startTime = Date.now();

    const leftShoulder = landmarks[11];
    const rightShoulder = landmarks[12];
    const nose = landmarks[0];

    // 1. Posture Check (Upright)
    // Ear (7,8) should be aligned with Shoulder (11,12) vertically? 
    // Simple check: Shoulders should be roughly level
    if (Math.abs(leftShoulder.y - rightShoulder.y) > 0.05) {
      this.feedback = "Straighten your posture.";
      return this.getState();
    }

    // 2. Stillness (Nose movement variance)
    this.noseHistory.push(nose);
    if (this.noseHistory.length > 30) this.noseHistory.shift();
    
    let movement = 0;
    if (this.noseHistory.length > 1) {
        const last = this.noseHistory[this.noseHistory.length - 1];
        const prev = this.noseHistory[this.noseHistory.length - 2];
        movement = Math.sqrt(Math.pow(last.x - prev.x, 2) + Math.pow(last.y - prev.y, 2));
    }

    if (movement > 0.005) {
        this.feedback = "Try to remain still.";
    } else {
        this.feedback = "Good stillness. Focus on breath.";
    }

    // 3. Breath Detection (Shoulder Rise/Fall)
    const avgShoulderY = (leftShoulder.y + rightShoulder.y) / 2;
    this.shoulderHistory.push({ y: avgShoulderY, time: Date.now() });
    if (this.shoulderHistory.length > 150) this.shoulderHistory.shift(); // 5 seconds @ 30fps

    // Analyze oscillation
    // We look for peaks and valleys in Y
    this.detectBreath();

    return this.getState();
  }

  detectBreath() {
      // Very simple peak detection
      if (this.shoulderHistory.length < 30) return;
      
      // Smooth data
      // Find local maxima
      // If we find a peak that is significantly higher than recent valleys, count as breath
      // This is complex to do robustly in real-time JS without signal processing lib
      // So we simulate "breath detected" if we see a rise and fall cycle
      
      const now = Date.now();
      if (now - this.lastBreathTime > 3000) { // Assume min breath 3s
          // Check if we had movement
          const yValues = this.shoulderHistory.map(h => h.y);
          const max = Math.max(...yValues);
          const min = Math.min(...yValues);
          
          if (max - min > 0.002) { // minimal movement threshold
              this.breathCount++;
              this.lastBreathTime = now;
          }
      }
  }

  getState() {
      return {
          feedback: this.feedback,
          breathRate: this.breathCount,
          duration: Math.floor((Date.now() - this.startTime) / 1000),
          isMeditating: true
      };
  }
}
