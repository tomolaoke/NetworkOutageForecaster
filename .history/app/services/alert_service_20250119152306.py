import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import requests
from datetime import datetime

load_dotenv()

class AlertService:
    def __init__(self):
        # Email configuration
        self.email_sender = os.getenv('EMAIL_SENDER')
        self.email_password = os.getenv('EMAIL_APP_PASSWORD')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        # SMS configuration (using Twilio)
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')

    async def send_email_alert(self, recipient: str, school_name: str, risk_data: dict) -> bool:
        """Send email alert about potential network outage"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_sender
            msg['To'] = recipient
            msg['Subject'] = f"Network Outage Risk Alert - {school_name}"

            body = f"""
            Network Outage Risk Alert for {school_name}
            
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Risk Level: {risk_data['risk_score']*100:.1f}%
            Status: {risk_data['message']}
            
            Current Weather Conditions:
            - Temperature: {risk_data['current_weather']['temperature']}°C
            - Humidity: {risk_data['current_weather']['humidity']}%
            - Wind Speed: {risk_data['current_weather']['wind_speed']} m/s
            
            Please monitor your network status and take necessary precautions.
            """

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"Email alert error: {str(e)}")
            return False

    async def send_sms_alert(self, phone_number: str, school_name: str, risk_data: dict) -> bool:
        """Send SMS alert about potential network outage"""
        try:
            # Using Twilio API
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
            message = (
                f"Network Outage Alert - {school_name}\n"
                f"Risk Level: {risk_data['risk_score']*100:.1f}%\n"
                f"Status: {risk_data['message']}"
            )
            
            response = requests.post(
                url,
                auth=(self.twilio_account_sid, self.twilio_auth_token),
                data={
                    'From': self.twilio_phone_number,
                    'To': phone_number,
                    'Body': message
                }
            )
            
            return response.status_code == 201

        except Exception as e:
            print(f"SMS alert error: {str(e)}")
            return False

    async def send_alerts(self, school_name: str, contact_email: str, 
                         contact_phone: str, risk_data: dict) -> dict:
        """Send both email and SMS alerts if risk is high enough"""
        results = {
            "email_sent": False,
            "sms_sent": False,
            "risk_level": risk_data['risk_score']
        }
        
        # Only send alerts if risk is moderate or high (above 40%)
        if risk_data['risk_score'] >= 0.4:
            results['email_sent'] = await self.send_email_alert(
                contact_email, school_name, risk_data
            )
            
            # Send SMS for high risk only (above 70%)
            if risk_data['risk_score'] >= 0.7:
                results['sms_sent'] = await self.send_sms_alert(
                    contact_phone, school_name, risk_data
                )
        
        return results