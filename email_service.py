# email_service_simple.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.sender_email = "divyadharshini04.hr@gmail.com"
        self.password = "fhhp tfuk jeto albi"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def send_performance_email(self, to_email, name, level, score):
        """Send performance evaluation email"""
        subject = "Your Performance Evaluation Result"
        
        # Create email body based on performance level
        if level == "High":
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #28a745;">🎉 Congratulations!</h2>
                    <p>Dear <strong>{name}</strong>,</p>
                    <p>We are pleased to inform you that your recent performance evaluation has been rated as <strong style="color: #28a745;">HIGH</strong>.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0;"><strong>Performance Score:</strong> {score}</p>
                    </div>
                    
                    <p>Your dedication, productivity, and teamwork have made a strong positive impact on the organization.</p>
                    <p>Keep up the excellent work and continue striving for greater achievements.</p>
                    <p><strong>You will receive 15% of your salary as incentive this month!</strong></p>
                    
                    <p>Best wishes for your continued success.</p>
                    
                    <p style="margin-top: 30px;">Regards,<br><strong>HR Department</strong></p>
                </div>
            </body>
            </html>
            """
        elif level == "Medium":
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #ffc107;">📊 Performance Update</h2>
                    <p>Dear <strong>{name}</strong>,</p>
                    <p>We appreciate your consistent efforts and contributions to the team.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0;"><strong>Performance Score:</strong> {score}</p>
                        <p style="margin: 5px 0 0;"><strong>Performance Level:</strong> MEDIUM</p>
                    </div>
                    
                    <p>You are performing well, and with a bit more focus on key areas, you have the potential to achieve even higher performance levels.</p>
                    <p>We encourage you to continue improving and growing.</p>
                    
                    <p style="margin-top: 30px;">Regards,<br><strong>HR Department</strong></p>
                </div>
            </body>
            </html>
            """
        else:  # Low performance
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #dc3545;">📈 Performance Feedback</h2>
                    <p>Dear <strong>{name}</strong>,</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0;"><strong>Performance Score:</strong> {score}</p>
                        <p style="margin: 5px 0 0;"><strong>Performance Level:</strong> LOW</p>
                    </div>
                    
                    <p>We believe in your potential and encourage you to focus on improving key performance areas.</p>
                    <p>Your team leader and HR department are available to support you with guidance and development opportunities.</p>
                    <p>With consistent effort, you can achieve better results in the coming evaluation.</p>
                    
                    <p style="margin-top: 30px;">Regards,<br><strong>HR Department</strong></p>
                </div>
            </body>
            </html>
            """
        
        return self.send_email(to_email, subject, body)
    
    def send_email(self, to_email, subject, html_body):
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True, "Email sent successfully"
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False, str(e)