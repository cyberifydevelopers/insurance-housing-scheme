import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import List


class JobNotificationEmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_username = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_name = "Insurance Housing Company"

        if not all([self.smtp_server, self.smtp_username, self.smtp_password]):
            raise ValueError(
                f"Missing SMTP config — SERVER={self.smtp_server}, "
                f"USERNAME={self.smtp_username}, PASSWORD={'set' if self.smtp_password else 'MISSING'}"
            )

    def send_new_jobs_email(self, to_emails: list[str], jobs: List[dict]):
        if not jobs or not to_emails:
            return

        job_list_html = ""
        for job in jobs:
            raw_title = job.get("title")
            title = (
                raw_title
                if raw_title and raw_title.strip() and raw_title != "Title:"
                else job.get("job_summary", "New Job Available")[:60]
            )
            url = job.get("url") or job.get("link") or "#"

            job_list_html += f"""
                <li style="margin-bottom: 12px;">
                    <strong>{title}</strong><br/>
                    {'<a href="' + url + '" target="_blank">View Job</a>' if url != "#" else '<span>No public job link available</span>'}
                </li>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f7fa; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 12px;">
                <h2 style="color: #111827;">New Jobs Just Posted</h2>
                <p>The following new job opportunities have been found:</p>
                <ul style="padding-left: 20px;">
                    {job_list_html}
                </ul>
                <p style="margin-top: 30px;">
                    Best regards,<br/>
                    <strong>Insurance Housing Company Team</strong>
                </p>
            </div>
        </body>
        </html>
        """

        # Open ONE SMTP connection and send to all recipients
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.smtp_username, self.smtp_password)

            for email in to_emails:
                email = email.strip()
                if not email:
                    continue

                message = MIMEMultipart()
                message["From"] = f"{self.from_name} <{self.smtp_username}>"
                message["To"] = email
                message["Subject"] = "New Job Opportunities Available 🚀"
                message.attach(MIMEText(html, "html"))

                server.send_message(message)
                print(f"DEBUG - Email sent to: {email}")




# class JobNotificationEmailService:
#     def __init__(self):
#         self.smtp_server = os.getenv("SMTP_SERVER")
#         self.smtp_port = int(os.getenv("SMTP_PORT", 587))
#         self.smtp_username = os.getenv("SMTP_USER")        # changed from SMTP_FROM_ADDRESS
#         self.smtp_password = os.getenv("SMTP_PASSWORD")
#         self.from_name = "Insurance Housing Company"

#         print(self.smtp_server)
#         print(self.smtp_port)
#         print(self.smtp_username)
#         print(self.from_name)

#         # Fail early with a clear message
#         if not all([self.smtp_server, self.smtp_username, self.smtp_password]):
#             raise ValueError(
#                 f"Missing SMTP config — SERVER={self.smtp_server}, "
#                 f"USERNAME={self.smtp_username}, PASSWORD={'set' if self.smtp_password else 'MISSING'}"
#             )

#     def send_new_jobs_email(self, to_email: str, jobs: List[dict]):
#         if not jobs:
#             return

#         message = MIMEMultipart()
#         message["From"] = f"{self.from_name} <{self.smtp_username}>"
#         message["To"] = to_email
#         message["Subject"] = "New Job Opportunities Available 🚀"

#         job_list_html = ""
#         for job in jobs:
#             raw_title = job.get("title")
#             title = (
#                 raw_title
#                 if raw_title and raw_title.strip() and raw_title != "Title:"
#                 else job.get("job_summary", "New Job Available")[:60]
#             )
#             url = job.get("url") or job.get("link") or "#"

#             job_list_html += f"""
#                 <li style="margin-bottom: 12px;">
#                     <strong>{title}</strong><br/>
#                     {'<a href="' + url + '" target="_blank">View Job</a>' if url != "#" else '<span>No public job link available</span>'}
#                 </li>
#             """

#         html = f"""
#         <!DOCTYPE html>
#         <html>
#         <body style="font-family: Arial, sans-serif; background-color: #f4f7fa; padding: 20px;">
#             <div style="max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 12px;">
#                 <h2 style="color: #111827;">New Jobs Just Posted</h2>
#                 <p>The following new job opportunities have been found:</p>
#                 <ul style="padding-left: 20px;">
#                     {job_list_html}
#                 </ul>
#                 <p style="margin-top: 30px;">
#                     Best regards,<br/>
#                     <strong>Insurance Housing Company Team</strong>
#                 </p>
#             </div>
#         </body>
#         </html>
#         """

#         message.attach(MIMEText(html, "html"))

#         # ✅ PORT 587 = STARTTLS, NOT SSL
#         with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
#             server.ehlo()
#             server.starttls()
#             server.ehlo()
#             server.login(self.smtp_username, self.smtp_password)
#             server.send_message(message)
#             print("DEBUG - server.send_message() completed!")

    # def send_new_jobs_email(self, to_email: str, jobs: List[dict]):
    #     if not jobs:
    #         return

    #     message = MIMEMultipart()
    #     message["From"] = f"{self.from_name} <{self.smtp_username}>"
    #     message["To"] = to_email
    #     message["Subject"] = "New Job Opportunities Available 🚀"

    #     job_list_html = ""
    #     for job in jobs:
    #         # ✅ FIX #1 — defensive mapping
    #         raw_title = job.get("title")
    #         title = (
    #             raw_title
    #             if raw_title and raw_title.strip() and raw_title != "Title:"
    #             else job.get("job_summary", "New Job Available")[:60]
    #         )

    #         url = job.get("url") or job.get("link") or "#"

    #         job_list_html += f"""
    #             <li style="margin-bottom: 12px;">
    #                 <strong>{title}</strong><br/>
    #                 {'<a href="' + url + '" target="_blank">View Job</a>' if url != "#" else '<span>No public job link available</span>'}
    #             </li>
    #         """


    #     html = f"""
    #     <!DOCTYPE html>
    #     <html>
    #     <body style="font-family: Arial, sans-serif; background-color: #f4f7fa; padding: 20px;">
    #         <div style="max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 12px;">
    #             <h2 style="color: #111827;">New Jobs Just Posted</h2>
    #             <p>The following new job opportunities have been found:</p>

    #             <ul style="padding-left: 20px;">
    #                 {job_list_html}
    #             </ul>

    #             <p style="margin-top: 30px;">
    #                 Best regards,<br/>
    #                 <strong>Insurance Housing Company Team</strong>
    #             </p>
    #         </div>
    #     </body>
    #     </html>
    #     """

    #     message.attach(MIMEText(html, "html"))

    #     with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
    #         server.login(self.smtp_username, self.smtp_password)
    #         server.send_message(message)
