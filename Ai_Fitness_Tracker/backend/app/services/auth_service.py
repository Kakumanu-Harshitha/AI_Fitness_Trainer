from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from ..db.repositories.user_repo import UserRepository
from ..core.security import verify_password, create_access_token, hash_password, encrypt_totp_secret, decrypt_totp_secret
from ..schemas.schemas import UserRegister, TokenResponse
from ..core.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import timedelta, datetime
from jose import jwt, JWTError
import pyotp
import qrcode
import io
import base64

import asyncio

# Simple in-memory rate limiter for TOTP verification
# Format: {user_id: [timestamp1, timestamp2, ...]}
TOTP_ATTEMPTS = {}
MAX_ATTEMPTS = 5
TIME_WINDOW = 60  # seconds

class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    def _check_rate_limit(self, user_id: int):
        now = datetime.now()
        attempts = TOTP_ATTEMPTS.get(user_id, [])
        # Filter out old attempts
        attempts = [t for t in attempts if (now - t).total_seconds() < TIME_WINDOW]
        
        if len(attempts) >= MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
                detail="Too many TOTP attempts. Please try again later."
            )
            
        attempts.append(now)
        TOTP_ATTEMPTS[user_id] = attempts

    async def register_user(self, user_data: UserRegister) -> TokenResponse:
        if await self.user_repo.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        if user_data.email and await self.user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user = await self.user_repo.create(user_data)
        access_token = create_access_token(data={"sub": user.username})
        response = {"access_token": access_token, "token_type": "bearer", "user": user}
        print(f"DEBUG: register_user returning: {response.keys()}")
        return response

    async def authenticate_user(self, username: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_username(username)
        if not user:
            # Try to find by email if username lookup failed
            user = await self.user_repo.get_by_email(username)

        if not user:
            print(f"Auth failed: User '{username}' not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not verify_password(password, user.password):
            print(f"Auth failed: Password mismatch for user '{username}'. Provided len: {len(password)}, Hash len: {len(user.password)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer", "user": user}

    async def forgot_password(self, email: str):
        user = await self.user_repo.get_by_email(email)
        if not user:
            # We don't want to reveal if the email exists or not
            return {"message": "If this email is registered, you will receive a password reset link."}
        
        expires = timedelta(hours=settings.RESET_PASSWORD_TOKEN_EXPIRE_HOURS)
        reset_token = create_access_token(data={"sub": user.email, "type": "reset"}, expires_delta=expires)
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_reset_email, user.email, reset_token)
        except Exception as e:
            print(f"Error sending email: {e}")
            raise HTTPException(status_code=500, detail="Error sending email")
            
        return {"message": "If this email is registered, you will receive a password reset link."}

    async def reset_password(self, token: str, new_password: str):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email = payload.get("sub")
            token_type = payload.get("type")
            if email is None or token_type != "reset":
                raise HTTPException(status_code=400, detail="Invalid token")
        except JWTError:
            raise HTTPException(status_code=400, detail="Invalid token")
            
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        hashed_pw = hash_password(new_password)
        await self.user_repo.update_password(user, hashed_pw)
        return {"message": "Password updated successfully"}

    def _send_reset_email(self, email_to: str, token: str):
        if not settings.GMAIL_SENDER_EMAIL or not settings.GMAIL_APP_PASSWORD:
            print("SMTP credentials not set")
            return

        reset_link = f"{settings.WEB_BASE_URL}/reset-password?token={token}"
        msg = MIMEMultipart()
        msg['From'] = settings.GMAIL_SENDER_EMAIL
        msg['To'] = email_to
        msg['Subject'] = "Password Reset Request"
        
        body = f"Click here to reset your password: {reset_link}\nThis link expires in {settings.RESET_PASSWORD_TOKEN_EXPIRE_HOURS} hours."
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(settings.GMAIL_SENDER_EMAIL, settings.GMAIL_APP_PASSWORD)
                server.send_message(msg)
                print(f"Email sent to {email_to}")
        except Exception as e:
            print(f"Failed to send email: {e}")
            raise e

    async def setup_totp(self, user):
        # We allow re-setup if not enabled yet, or if they want to reset it (logic can be adjusted)
        # If already enabled, maybe require current OTP? 
        # For simplicity, if enabled, we allow reset but it invalidates old one.
        
        # Generate random secret
        secret = pyotp.random_base32()
        
        # Encrypt and save secret
        encrypted_secret = encrypt_totp_secret(secret)
        await self.user_repo.update_totp_secret(user, encrypted_secret)
        
        # Create provisioning URI using plaintext secret
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name="Ai Fitness Tracker"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        qr_code_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return {"secret": secret, "qr_code": f"data:image/png;base64,{qr_code_base64}"}

    async def verify_totp(self, user, otp: str):
        self._check_rate_limit(user.id)
        
        if not user.totp_secret:
             raise HTTPException(status_code=400, detail="TOTP not setup. Please setup first.")
             
        # Decrypt secret
        try:
            secret = decrypt_totp_secret(user.totp_secret)
        except Exception:
            # Fallback if secret was not encrypted (migration support) or key changed
            # In production, this should log an error.
            # Assuming old secrets are plaintext if decryption fails? 
            # Or just fail. Let's assume we might need to handle legacy if any.
            # But since this is a new feature, we can just fail or assume plaintext.
            # Let's assume fail for security.
            print(f"Error decrypting secret for user {user.id}")
            raise HTTPException(status_code=500, detail="Internal server error")

        totp = pyotp.TOTP(secret)
        # Verify with a window of 1 (30 seconds tolerance)
        if not totp.verify(otp, valid_window=1):
             raise HTTPException(status_code=400, detail="Invalid OTP")
             
        # If not enabled, enable it
        if not user.is_totp_enabled:
             await self.user_repo.enable_totp(user, True)
             
        return {"message": "OTP verified successfully"}

    async def change_password_with_totp(self, user, new_password: str, totp_code: str = None):
        if user.is_totp_enabled:
             self._check_rate_limit(user.id)
             
             if not totp_code:
                  raise HTTPException(status_code=400, detail="TOTP code required")
             
             # Verify TOTP
             if not user.totp_secret:
                  # Should not happen if is_totp_enabled is true, but safe check
                  raise HTTPException(status_code=400, detail="TOTP secret missing")
                  
             try:
                 secret = decrypt_totp_secret(user.totp_secret)
             except Exception:
                 raise HTTPException(status_code=500, detail="Internal server error")

             totp = pyotp.TOTP(secret)
             if not totp.verify(totp_code, valid_window=1):
                  raise HTTPException(status_code=400, detail="Invalid TOTP code")
        
        hashed_pw = hash_password(new_password)
        await self.user_repo.update_password(user, hashed_pw)
        return {"message": "Password changed successfully"}
