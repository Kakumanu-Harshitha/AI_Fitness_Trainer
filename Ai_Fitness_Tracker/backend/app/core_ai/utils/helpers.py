import cv2
import subprocess
import re

def get_wifi_strength():
    """
    Returns Wi-Fi signal strength percentage (0-100) on Windows.
    Returns None if not available or not on Windows.
    """
    try:
        cmd = "netsh wlan show interfaces"
        output = subprocess.check_output(cmd, shell=True).decode('utf-8')
        match = re.search(r"Signal\s*:\s*(\d+)%", output)
        if match:
            return int(match.group(1))
    except:
        pass
    return None

def draw_text_with_bg(frame, text, x, y,
                      font_scale=1,
                      text_color=(255, 255, 255),
                      bg_color=(0, 0, 0),
                      thickness=2):
    """
    Draws text with a solid background rectangle for better visibility
    """

    font = cv2.FONT_HERSHEY_SIMPLEX
    (w, h), _ = cv2.getTextSize(text, font, font_scale, thickness)

    # Draw background rectangle
    cv2.rectangle(
        frame,
        (x - 5, y - h - 10),
        (x + w + 5, y + 5),
        bg_color,
        -1
    )

    # Draw text
    cv2.putText(
        frame,
        text,
        (x, y),
        font,
        font_scale,
        text_color,
        thickness
    )

def check_lighting(frame):
    """
    Returns True if lighting is sufficient, False otherwise.
    Uses simple grayscale average brightness.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    avg_brightness = gray.mean()
    return avg_brightness > 50  # Threshold can be adjusted

def check_visibility(landmarks):
    """
    Checks if key landmarks are visible and not too close to edges.
    """
    if not landmarks:
        return False, "User not detected"
    
    # Key landmarks for most exercises
    # Hips (23, 24), Knees (25, 26), Ankles (27, 28), Shoulders (11, 12)
    key_indices = [11, 12, 23, 24, 25, 26, 27, 28]
    
    visible_count = 0
    for idx in key_indices:
        lm = landmarks[idx]
        # Visibility score from MediaPipe
        if lm.visibility > 0.5:
            # Check if within frame (0 to 1 range)
            if 0.05 < lm.x < 0.95 and 0.05 < lm.y < 0.95:
                visible_count += 1
                
    if visible_count < len(key_indices) * 0.7:
        return False, "Step back - Full body not visible"
        
    return True, "Ready"

def detect_fatigue(landmarks):
    """
    Simple fatigue detection based on shoulder drop and head tilt.
    """
    if not landmarks:
        return False, 0.0
    
    # 11: left shoulder, 12: right shoulder
    ls = landmarks[11]
    rs = landmarks[12]
    
    # Shoulder drop (large difference in y)
    shoulder_drop = abs(ls.y - rs.y)
    
    # 0: nose, 11: left shoulder, 12: right shoulder
    nose = landmarks[0]
    shoulder_mid_y = (ls.y + rs.y) / 2
    head_tilt = abs(nose.y - shoulder_mid_y)
    
    # Heuristic fatigue score
    # If shoulders are very uneven or head is hanging low
    fatigue_score = 0.0
    if shoulder_drop > 0.1: fatigue_score += 0.5
    if head_tilt < 0.2: fatigue_score += 0.5 # Head too close to shoulder line
    
    return fatigue_score > 0.7, fatigue_score
