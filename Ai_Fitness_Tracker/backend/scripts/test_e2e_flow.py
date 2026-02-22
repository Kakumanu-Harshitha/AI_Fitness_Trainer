import requests
import uuid
import sys
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_e2e_flow():
    # 1. Signup
    username = f"test_user_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "Password123!"
    
    print(f"Testing with user: {username}")
    
    signup_data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    try:
        print("1. Testing Signup...")
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
        if response.status_code != 200:
            print(f"Signup failed: {response.text}")
            return False
        print("Signup successful.")
        
        # 2. Login (Check for missing lifestyle data)
        print("2. Testing Login (Initial)...")
        
        # Try JSON with username
        response = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
        
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return False
            
        data = response.json()
        token = data.get("access_token")
        user = data.get("user", {})
        
        print("Login successful.")
        
        # Check if lifestyle data is missing
        if user.get("body_type"):
            print("WARNING: User already has body_type set? Should be empty.")
        else:
            print("Verified: body_type is missing (as expected).")
            
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Submit Lifestyle Data (Profile Update)
        print("3. Testing Lifestyle Data Submission...")
        lifestyle_data = {
            "body_type": "Mesomorph",
            "diet_goal": "Build Muscle",
            "activity_level": "Active",
            "daily_sleep_goal": 8.0,
            "daily_water_goal": 3000,
            "dietary_preferences": "None",
            "injuries": "None"
        }
        
        response = requests.post(f"{BASE_URL}/profile", json=lifestyle_data, headers=headers)
        if response.status_code != 200:
            print(f"Profile update failed: {response.text}")
            return False
            
        updated_user = response.json()
        # The endpoint might return the updated user object directly or nested
        # Based on schemas.py, ProfileResponse returns { user: UserResponse, access_token: ... } 
        # But wait, schemas.py has ProfileResponse. 
        # Let's check users.py to see what update_profile returns.
        
        # If it returns UserResponse, then body_type is at top level.
        # If it returns ProfileResponse, it's under 'user'.
        
        # Let's assume it returns UserResponse for now based on typical patterns, 
        # or check the response structure dynamically.
        
        actual_body_type = updated_user.get("body_type")
        if not actual_body_type and "user" in updated_user:
            actual_body_type = updated_user["user"].get("body_type")
            
        if actual_body_type != "Mesomorph":
            print(f"Failed to update body_type. Got: {actual_body_type}")
            print(f"Full response: {updated_user}")
            return False
        print("Lifestyle data submitted successfully.")
        
        # 4. Login Again (Verify data presence)
        print("4. Testing Login (Second time)...")
        response = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
             
        if response.status_code != 200:
            print(f"Second login failed: {response.text}")
            return False
            
        data = response.json()
        user = data.get("user", {})
        
        body_type = user.get("body_type")
        
        if body_type == "Mesomorph":
            print("Verified: body_type is present after re-login.")
        else:
            print(f"ERROR: body_type missing after update. User data: {user}")
            return False
            
        # 5. Access Dashboard
        print("5. Testing Dashboard Access...")
        response = requests.get(f"{BASE_URL}/dashboard/home", headers=headers)
        if response.status_code != 200:
            print(f"Dashboard access failed: {response.text}")
            return False
            
        print("Dashboard accessed successfully.")
        print("E2E Flow Test PASSED!")
        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    success = test_e2e_flow()
    if not success:
        sys.exit(1)
