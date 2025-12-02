import jwt
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

EMAIL_VERIFICATION_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Your Email</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f4f4f4;
            line-height: 1.6;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            text-align: center;
        }}
        .header h1 {{
            color: #ffffff;
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .content {{
            padding: 40px 30px;
            color: #333333;
        }}
        .content h2 {{
            color: #333333;
            font-size: 24px;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        .content p {{
            font-size: 16px;
            color: #666666;
            margin-bottom: 20px;
        }}
        .verification-code {{
            background-color: #f8f9fa;
            border: 2px dashed #667eea;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 30px 0;
        }}
        .code {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            letter-spacing: 8px;
            font-family: 'Courier New', monospace;
        }}
        .button-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .verify-button {{
            display: inline-block;
            padding: 16px 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #ffffff;
            text-decoration: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s;
        }}
        .verify-button:hover {{
            transform: translateY(-2px);
        }}
        .divider {{
            border-top: 1px solid #e0e0e0;
            margin: 30px 0;
        }}
        .info-box {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .info-box p {{
            margin: 0;
            font-size: 14px;
            color: #856404;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666666;
            font-size: 14px;
        }}
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        .social-links {{
            margin: 20px 0;
        }}
        .social-links a {{
            display: inline-block;
            margin: 0 10px;
            color: #666666;
            text-decoration: none;
        }}
        @media only screen and (max-width: 600px) {{
            .content {{
                padding: 30px 20px;
            }}
            .header h1 {{
                font-size: 24px;
            }}
            .code {{
                font-size: 28px;
                letter-spacing: 4px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>📧 Email Verification</h1>
        </div>

        <div class="content">
            <h2>Hello {user_name}!</h2>
            <p>Thank you for signing up! We're excited to have you on board. To complete your registration, please verify your email address.</p>

            <div class="button-container">
                <a href="{verification_url}" class="verify-button">Verify Email Address</a>
            </div>

            <div class="divider"></div>

            <p>Or enter this verification code:</p>
            <div class="verification-code">
                <div class="code">{verification_code}</div>
            </div>

            <div class="info-box">
                <p><strong>⏰ This code will expire in 24 hours.</strong> If you didn't create an account, you can safely ignore this email.</p>
            </div>

            <p>If you're having trouble with the button above, copy and paste this URL into your browser:</p>
            <p style="word-break: break-all; color: #667eea; font-size: 14px;">{verification_url}</p>
        </div>

        <div class="footer">
            <p><strong>Your Company Name</strong></p>
            <p>123 Business Street, City, State 12345</p>
            <div class="social-links">
                <a href="#">Twitter</a> |
                <a href="#">Facebook</a> |
                <a href="#">LinkedIn</a>
            </div>
            <p>Need help? <a href="mailto:support@yourcompany.com">Contact Support</a></p>
            <p style="font-size: 12px; color: #999999; margin-top: 20px;">
                © 2024 Your Company. All rights reserved.<br>
                <a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a>
            </p>
        </div>
    </div>
</body>
</html>
"""

class EmailConstructor:
    def __init__(self, app):
        self.app = app
        self.conf = ConnectionConfig(
            MAIL_USERNAME=self.app.config.MAIL_ADDRESS,
            MAIL_PASSWORD=self.app.config.MAIL_PASSWORD,
            MAIL_FROM=self.app.config.MAIL_ADDRESS,
            MAIL_PORT="465", MAIL_SERVER="smtp.gmail.com",
            MAIL_STARTTLS = False, MAIL_SSL_TLS = True,
            USE_CREDENTIALS = True, VALIDATE_CERTS = True
        )

    async def send_mail(self, email: list, instance: dict):
        token_data = {
            "UUID": instance["uuid"],
            "USR_NAME": instance["user_name"]
        }

        verification_token = jwt.encode(token_data, self.app.config.YOU_HAVE_BEEN_WARNED, algorithm="HS256")

        email_template = EMAIL_VERIFICATION_TEMPLATE.format(
            user_name=instance["user_name"],
            verification_code=verification_token,
            verification_url=f"https://filthy-cauldron-6q6pxgq4wg2rppr-8000.app.github.dev/api/v1/gateway/verify/{verification_token}"
        )

        message = MessageSchema(
            subject="Kureghor Account Verification Email",
            recipients=email,
            body=email_template,
            subtype="html"
        )

        fast_mail = FastMail(self.conf)
        await fast_mail.send_message(message=message)