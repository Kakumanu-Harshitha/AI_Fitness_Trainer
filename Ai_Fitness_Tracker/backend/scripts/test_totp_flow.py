import requests
import pyotp
import time

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "test_totp_user@example.com"
INITIAL_PASSWORD = "password123"
NEW_PASSWORD = "newpassword123"

def test_flow():
    current_password = INITIAL_PASSWORD
    
    # 1. Register or Login
    print("1. Authenticating...")
    login_data = {
        "username": EMAIL,
        "password": current_password
    }
    
    # Try login first
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("Login failed, trying register...")
        # Try register
        register_data = {
            "email": EMAIL,
            "password": current_password,
            "username": "test_totp_user",
            "full_name": "Test TOTP User"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 200:
            print("Registration successful.")
            # Login again
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        else:
            print(f"Registration failed: {response.text}")
            # If registration failed because user exists, maybe password is different or something.
            # Let's assume user exists and maybe we changed password in previous run?
            # Try login with NEW_PASSWORD
            login_data["password"] = NEW_PASSWORD
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                print("Logged in with NEW password.")
                current_password = NEW_PASSWORD
            else:
                 print(f"Login failed: {response.text}")
                 return

    if response.status_code != 200:
        print("Authentication failed.")
        return

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Authenticated.")

    # 2. Setup TOTP
    print("\n2. Setting up TOTP...")
    response = requests.post(f"{BASE_URL}/auth/totp/setup", headers=headers)
    if response.status_code != 200:
        print(f"Setup failed: {response.text}")
        return
    
    data = response.json()
    secret = data["secret"]
    print(f"Got secret: {secret}")

    # 3. Verify TOTP
    print("\n3. Verifying TOTP...")
    totp = pyotp.TOTP(secret)
    otp = totp.now()
    print(f"Generated OTP: {otp}")
    
    verify_data = {"otp": otp}
    response = requests.post(f"{BASE_URL}/auth/totp/verify", json=verify_data, headers=headers)
    
    if response.status_code == 200:
        print("TOTP Verification Successful!")
    else:
        print(f"TOTP Verification Failed: {response.text}")
        return

    # 4. Change Password
    print("\n4. Changing Password...")
    
    # Let's wait 5s to ensure clean state
    print("Waiting 5s to ensure clean state...")
    time.sleep(5) 
    
    otp = totp.now()
    change_data = {
        "new_password": NEW_PASSWORD,
        "totp_code": otp
    }
    
    response = requests.post(f"{BASE_URL}/auth/change-password", json=change_data, headers=headers)
    
    if response.status_code == 200:
        print("Password Change Successful!")
    else:
        print(f"Password Change Failed: {response.text}")
        # If it failed because password was already changed (e.g. from previous run), it's tricky.
        # But we logged in with current_password, so it should be fine.
        return

    # 5. Verify Login with New Password
    print("\n5. Verifying Login with New Password...")
    login_data = {
        "username": EMAIL,
        "password": NEW_PASSWORD
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        print("Login with New Password Successful!")
    else:
        print(f"Login with New Password Failed: {response.text}")

if __name__ == "__main__":
    test_flow()
