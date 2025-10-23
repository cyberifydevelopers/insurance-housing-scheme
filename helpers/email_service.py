import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import jwt
from datetime import datetime, timedelta

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT'))
        self.smtp_username = os.getenv('SMTP_FROM_ADDRESS')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_name = os.getenv('SMTP_FROM_USER')
        self.jwt_secret = os.getenv('JWT_SECRET')

    def generate_login_token(self, user_id: int) -> str:
        expiration = datetime.utcnow() + timedelta(hours=24)
        return jwt.encode(
            {'user_id': user_id, 'exp': expiration},
            self.jwt_secret,
            algorithm='HS256'
        )

    def send_welcome_email(self, to_email: str, name: str, password: str, user_id: int):
        login_token = self.generate_login_token(user_id)
        login_link = f"http://localhost:5173/auto-login?token={login_token}"  # Update with your frontend URL

        message = MIMEMultipart()
        message['From'] = f"{self.from_name} <{self.smtp_username}>"
        message['To'] = to_email
        message['Subject'] = "Welcome to Insurance Housing Company!"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
                body {{
                    font-family: 'Inter', sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f7fa;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    padding: 0 20px;
                }}
                .card {{
                    background: white;
                    border-radius: 16px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    padding: 40px;
                    margin-bottom: 20px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    width: 150px;
                    margin-bottom: 20px;
                }}
                h1 {{
                    color: #1a1a1a;
                    font-size: 24px;
                    font-weight: 600;
                    margin: 0 0 20px;
                }}
                .welcome-text {{
                    color: #4b5563;
                    font-size: 16px;
                    margin-bottom: 30px;
                }}
                .credentials-box {{
                    background: #f8fafc;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .credential-item {{
                    margin: 10px 0;
                }}
                .credential-label {{
                    color: #6b7280;
                    font-size: 14px;
                    font-weight: 500;
                }}
                .credential-value {{
                    color: #111827;
                    font-weight: 600;
                    font-size: 16px;
                    margin-top: 4px;
                }}
                .button {{
                    display: inline-block;
                    background: #2563eb;
                    color: white;
                    text-decoration: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: 500;
                    margin: 20px 0;
                    text-align: center;
                }}
                .button:hover {{
                    background: #1d4ed8;
                }}
                .security-note {{
                    font-size: 14px;
                    color: #6b7280;
                    border-left: 4px solid #fbbf24;
                    padding-left: 16px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #6b7280;
                    font-size: 14px;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <div class="header">
                        <h1>Welcome to Insurance Housing Company!</h1>
                    </div>
                    
                    <div class="welcome-text">
                        Hello {name}, your account has been successfully created. Below are your login credentials.
                    </div>

                    <div class="credentials-box">
                        <div class="credential-item">
                            <div class="credential-label">Email Address</div>
                            <div class="credential-value">{to_email}</div>
                        </div>
                        <div class="credential-item">
                            <div class="credential-label">Password</div>
                            <div class="credential-value">{password}</div>
                        </div>
                    </div>

                    <a href="{login_link}" class="button">Login to Your Account</a>

                    <div class="security-note">
                        For your security, we recommend changing your password after your first login. The login link above is valid for 24 hours.
                    </div>

                    <div class="footer">
                        <p>Best regards,<br><strong>Insurance Housing Company Team</strong></p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        message.attach(MIMEText(html, 'html'))

        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(message)