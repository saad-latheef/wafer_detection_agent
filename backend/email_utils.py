"""
Email notification utilities for wafer defect alerts.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from datetime import datetime


class EmailNotificationService:
    """
    Email notification service for sending defect alerts.
    Supports SMTP configuration for various providers.
    """
    
    def __init__(
        self,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        username: str = "",
        password: str = "",
        from_email: str = "",
        enabled: bool = False
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email or username
        self.enabled = enabled
    
    def send_alert(
        self,
        to_emails: List[str],
        subject: str,
        body_html: str,
        body_text: Optional[str] = None
    ) -> Dict:
        """
        Send an email alert.
        
        Returns:
            Dict with success status and any error message
        """
        if not self.enabled:
            return {"success": False, "error": "Email notifications disabled"}
        
        if not to_emails:
            return {"success": False, "error": "No recipients specified"}
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = ", ".join(to_emails)
            
            # Add plain text and HTML versions
            if body_text:
                msg.attach(MIMEText(body_text, "plain"))
            msg.attach(MIMEText(body_html, "html"))
            
            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.sendmail(self.from_email, to_emails, msg.as_string())
            
            return {"success": True, "recipients": to_emails}
            
        except Exception as e:
            return {"success": False, "error": str(e)}


def create_defect_alert_html(
    lot_id: str,
    defect_rate: float,
    threshold: float,
    tool_id: str,
    top_defects: List[Dict],
    timestamp: datetime
) -> str:
    """
    Create an HTML email body for defect rate alerts.
    """
    defects_html = ""
    for defect in top_defects[:5]:
        defects_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{defect.get('pattern', 'Unknown')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{defect.get('count', 0)}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{defect.get('percentage', 0):.1f}%</td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .alert-box {{ background: #ff5555; color: white; padding: 20px; border-radius: 8px; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background: #00d4ff; color: white; padding: 10px; text-align: left; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 style="color: #ff5555;">⚠️ Defect Rate Alert</h1>
            
            <div class="alert-box">
                <h2>Threshold Exceeded: {defect_rate:.1f}%</h2>
                <p>Alert threshold: {threshold:.1f}%</p>
            </div>
            
            <h3>Details</h3>
            <table>
                <tr>
                    <td><strong>Lot ID:</strong></td>
                    <td>{lot_id}</td>
                </tr>
                <tr>
                    <td><strong>Tool ID:</strong></td>
                    <td>{tool_id}</td>
                </tr>
                <tr>
                    <td><strong>Timestamp:</strong></td>
                    <td>{timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td>
                </tr>
            </table>
            
            <h3>Top Defect Patterns</h3>
            <table>
                <thead>
                    <tr>
                        <th>Pattern</th>
                        <th>Count</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    {defects_html}
                </tbody>
            </table>
            
            <p style="margin-top: 30px; color: #666;">
                This is an automated alert from AgentWafer. 
                <a href="http://localhost:3000/analytics">View Dashboard</a>
            </p>
        </div>
    </body>
    </html>
    """


def create_daily_digest_html(
    date: datetime,
    total_wafers: int,
    defective_wafers: int,
    yield_rate: float,
    tool_summary: List[Dict]
) -> str:
    """
    Create an HTML email body for daily digest reports.
    """
    tools_html = ""
    for tool in tool_summary[:5]:
        status_color = "#22c55e" if tool.get('defect_rate', 0) < 10 else "#ff5555"
        tools_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{tool.get('tool_id', 'Unknown')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{tool.get('wafers_processed', 0)}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; color: {status_color};">{tool.get('defect_rate', 0):.1f}%</td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .summary-box {{ background: linear-gradient(135deg, #00d4ff, #8b5cf6); color: white; padding: 30px; border-radius: 12px; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background: #00d4ff; color: white; padding: 10px; text-align: left; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 style="color: #00d4ff;">📊 Daily Fab Report</h1>
            <p style="color: #666;">{date.strftime('%A, %B %d, %Y')}</p>
            
            <div class="summary-box">
                <h2 style="margin: 0;">Yield Rate: {yield_rate:.1f}%</h2>
                <p>Processed: {total_wafers} wafers | Defective: {defective_wafers}</p>
            </div>
            
            <h3>Tool Performance Summary</h3>
            <table>
                <thead>
                    <tr>
                        <th>Tool ID</th>
                        <th>Wafers</th>
                        <th>Defect Rate</th>
                    </tr>
                </thead>
                <tbody>
                    {tools_html}
                </tbody>
            </table>
            
            <p style="margin-top: 30px; color: #666;">
                <a href="http://localhost:3000/analytics">View Full Analytics Dashboard</a>
            </p>
        </div>
    </body>
    </html>
    """


# Global notification service instance (configured at runtime)
notification_service = EmailNotificationService()


def configure_notifications(config: Dict) -> Dict:
    """
    Configure the global notification service.
    """
    global notification_service
    notification_service = EmailNotificationService(
        smtp_host=config.get("smtp_host", "smtp.gmail.com"),
        smtp_port=config.get("smtp_port", 587),
        username=config.get("username", ""),
        password=config.get("password", ""),
        from_email=config.get("from_email", ""),
        enabled=config.get("enabled", False)
    )
    return {"success": True, "enabled": notification_service.enabled}
