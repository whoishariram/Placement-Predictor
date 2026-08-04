"""
Placement Predictor - Mentor Alert System
Automatically detects at-risk students and sends email notifications to mentors
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional


class MentorAlertSystem:
    """
    Mentor Alert System for detecting at-risk students and notifying mentors

    Automatically detects:
    - Low CGPA
    - Poor Resume Score
    - Low Programming Score
    - Low Communication Score
    - Not Eligible for Companies
    - Low Placement Probability
    """

    def __init__(self, config=None):
        """
        Initialize mentor alert system

        Args:
            config: Configuration object with email and threshold settings
        """
        self.config = config or self._get_default_config()
        self.alerts_sent = 0
        self.alerts_failed = 0

    def _get_default_config(self):
        """Get default configuration values"""
        class DefaultConfig:
            MAIL_SERVER = 'smtp.gmail.com'
            MAIL_PORT = 587
            MAIL_USE_TLS = True
            MAIL_USE_SSL = False
            MAIL_USERNAME = ''
            MAIL_PASSWORD = ''
            MAIL_DEFAULT_SENDER = 'placement.predictor@edu.in'
            ALERT_LOW_CGPA = 7.0
            ALERT_LOW_RESUME = 40
            ALERT_LOW_PROGRAMMING = 40
            ALERT_LOW_COMMUNICATION = 40
            ALERT_LOW_PROBABILITY = 35.0

        return DefaultConfig()

    # ============================================================
    # ALERT DETECTION
    # ============================================================

    def detect_alerts(self, student_data: dict, prediction_result: dict = None) -> List[dict]:
        """
        Detect all applicable alerts for a student

        Args:
            student_data: Dict with student information
            prediction_result: Optional prediction result from PredictionEngine

        Returns:
            List of alert dicts with type, message, weak_areas, suggestions
        """
        alerts = []

        # 1. Low CGPA check
        alert = self._check_low_cgpa(student_data)
        if alert:
            alerts.append(alert)

        # 2. Low Resume Score check
        alert = self._check_low_resume(student_data)
        if alert:
            alerts.append(alert)

        # 3. Low Programming Score check
        alert = self._check_low_programming(student_data)
        if alert:
            alerts.append(alert)

        # 4. Low Communication Score check
        alert = self._check_low_communication(student_data)
        if alert:
            alerts.append(alert)

        # 5. Low Placement Probability check
        if prediction_result:
            alert = self._check_low_probability(student_data, prediction_result)
            if alert:
                alerts.append(alert)

        # 6. No mentor email check
        mentor_email = student_data.get('mentor_email', '')
        if not mentor_email:
            alerts.append({
                'alert_type': 'no_mentor',
                'alert_message': f"Student {student_data.get('name', 'Unknown')} has no mentor email assigned",
                'weak_areas': ['Mentor Assignment'],
                'suggestions': ['Assign a mentor email to this student for future alerts'],
                'prediction_result': prediction_result.get('prediction_label', 'N/A') if prediction_result else 'N/A'
            })

        return alerts

    def _check_low_cgpa(self, student_data: dict) -> Optional[dict]:
        """Check if student has low CGPA"""
        cgpa = float(student_data.get('cgpa', 10))
        threshold = float(self.config.ALERT_LOW_CGPA)

        if cgpa < threshold:
            weak_areas = ['Academic Performance']
            suggestions = [
                'Attend extra tutorials and remedial classes',
                'Meet with academic advisors for guidance',
                'Focus on improving grades in core subjects',
                'Form study groups with high-performing students'
            ]

            return {
                'alert_type': 'low_cgpa',
                'alert_message': f"Student has low CGPA ({cgpa}/{threshold}). Academic performance needs attention.",
                'weak_areas': weak_areas,
                'suggestions': suggestions,
                'prediction_result': 'At Risk'
            }
        return None

    def _check_low_resume(self, student_data: dict) -> Optional[dict]:
        """Check if student has poor resume score"""
        resume_score = int(student_data.get('resume_score', 100))
        threshold = int(self.config.ALERT_LOW_RESUME)

        if resume_score < threshold:
            weak_areas = ['Resume Quality', 'Profile Presentation']
            suggestions = [
                'Improve resume with quantifiable achievements',
                'Add more technical projects and skills',
                'Include relevant certifications and internships',
                'Get resume reviewed by placement cell',
                'Use ATS-friendly resume template'
            ]

            return {
                'alert_type': 'low_resume',
                'alert_message': f"Student has poor resume score ({resume_score}/{threshold}). Resume needs significant improvement.",
                'weak_areas': weak_areas,
                'suggestions': suggestions,
                'prediction_result': 'Needs Improvement'
            }
        return None

    def _check_low_programming(self, student_data: dict) -> Optional[dict]:
        """Check if student has low programming skill score"""
        prog_skill = int(student_data.get('programming_skill', 100))
        threshold = int(self.config.ALERT_LOW_PROGRAMMING)

        if prog_skill < threshold:
            weak_areas = ['Programming Skills', 'Technical Competence']
            suggestions = [
                'Practice coding daily on LeetCode, HackerRank, CodeChef',
                'Enroll in a structured programming course',
                'Work on hands-on coding projects',
                'Focus on data structures and algorithms',
                'Participate in coding contests and hackathons'
            ]

            return {
                'alert_type': 'low_programming',
                'alert_message': f"Student has low programming skill score ({prog_skill}/{threshold}). Technical skills need urgent improvement.",
                'weak_areas': weak_areas,
                'suggestions': suggestions,
                'prediction_result': 'At Risk'
            }
        return None

    def _check_low_communication(self, student_data: dict) -> Optional[dict]:
        """Check if student has low communication skill score"""
        comm_skill = int(student_data.get('communication_skill', 100))
        threshold = int(self.config.ALERT_LOW_COMMUNICATION)

        if comm_skill < threshold:
            weak_areas = ['Communication Skills', 'Soft Skills']
            suggestions = [
                'Practice mock interviews and group discussions',
                'Participate in debate clubs and presentations',
                'Work on verbal and written communication',
                'Take online courses in business communication',
                'Practice with peers and record for self-review'
            ]

            return {
                'alert_type': 'low_communication',
                'alert_message': f"Student has low communication skill score ({comm_skill}/{threshold}). Soft skills need development.",
                'weak_areas': weak_areas,
                'suggestions': suggestions,
                'prediction_result': 'Needs Improvement'
            }
        return None

    def _check_low_probability(self, student_data: dict, prediction_result: dict) -> Optional[dict]:
        """Check if student has low placement prediction probability"""
        probability = float(prediction_result.get('probability', 100))
        threshold = float(self.config.ALERT_LOW_PROBABILITY)

        if probability < threshold:
            weak_areas = ['Placement Readiness', 'Overall Profile']
            suggestions = [
                'Create a structured 3-month preparation plan',
                'Focus on improving weakest areas identified in prediction',
                'Attend all placement training sessions',
                'Practice company-specific mock interviews',
                'Connect with placed alumni for guidance',
                'Improve technical and aptitude skills simultaneously'
            ]

            return {
                'alert_type': 'low_probability',
                'alert_message': f"Student has low placement probability ({probability:.1f}%/{threshold:.1f}%). Immediate intervention recommended.",
                'weak_areas': weak_areas,
                'suggestions': suggestions,
                'prediction_result': prediction_result.get('prediction_label', 'Not Placed')
            }
        return None

    # ============================================================
    # EMAIL NOTIFICATIONS
    # ============================================================

    def send_alert_email(self, mentor_email: str, student_data: dict, alert: dict) -> bool:
        """
        Send an alert email to the mentor

        Args:
            mentor_email: Mentor's email address
            student_data: Student details
            alert: Alert details

        Returns:
            bool: True if email sent successfully
        """
        if not self._is_email_configured():
            print("⚠️  Email not configured. Enable SMTP settings to send alerts.")
            return False

        try:
            # Create email
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config.MAIL_DEFAULT_SENDER
            msg['To'] = mentor_email
            msg['Subject'] = f"🚨 Mentor Alert: {student_data.get('name', 'Student')} - {alert['alert_type'].replace('_', ' ').title()}"

            # Generate HTML content
            html_body = self._generate_alert_email_html(student_data, alert)
            text_body = self._generate_alert_email_text(student_data, alert)

            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP(self.config.MAIL_SERVER, self.config.MAIL_PORT) as server:
                if self.config.MAIL_USE_TLS:
                    server.starttls()
                if self.config.MAIL_USERNAME and self.config.MAIL_PASSWORD:
                    server.login(self.config.MAIL_USERNAME, self.config.MAIL_PASSWORD)
                server.send_message(msg)

            self.alerts_sent += 1
            print(f"✅ Alert email sent to {mentor_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            print(f"❌ SMTP Authentication failed. Check email credentials.")
            self.alerts_failed += 1
            return False
        except smtplib.SMTPException as e:
            print(f"❌ SMTP Error: {str(e)}")
            self.alerts_failed += 1
            return False
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            self.alerts_failed += 1
            return False

    def send_alert_batch(self, alerts_data: List[tuple]) -> Dict:
        """
        Send multiple alert emails in batch

        Args:
            alerts_data: List of (mentor_email, student_data, alert) tuples

        Returns:
            Dict with send statistics
        """
        results = {
            'total': len(alerts_data),
            'sent': 0,
            'failed': 0,
            'details': []
        }

        for mentor_email, student_data, alert in alerts_data:
            success = self.send_alert_email(mentor_email, student_data, alert)
            if success:
                results['sent'] += 1
            else:
                results['failed'] += 1
            results['details'].append({
                'mentor_email': mentor_email,
                'student_name': student_data.get('name', 'Unknown'),
                'alert_type': alert.get('alert_type', 'unknown'),
                'sent': success
            })

        return results

    def send_comprehensive_alert(self, mentor_email: str, student_data: dict,
                                  alerts: List[dict]) -> bool:
        """
        Send a comprehensive alert email with all detected issues

        Args:
            mentor_email: Mentor's email address
            student_data: Student details
            alerts: List of all detected alerts

        Returns:
            bool: True if email sent successfully
        """
        if not alerts:
            return False

        # Create a consolidated alert
        consolidated = {
            'alert_type': 'comprehensive',
            'alert_message': f"Multiple areas need attention for student {student_data.get('name', 'Unknown')}",
            'weak_areas': list(set(
                area for alert in alerts
                for area in alert.get('weak_areas', [])
            )),
            'suggestions': list(set(
                sugg for alert in alerts
                for sugg in alert.get('suggestions', [])
            )),
            'prediction_result': alerts[0].get('prediction_result', 'N/A'),
            'alerts_count': len(alerts),
            'individual_alerts': alerts
        }

        return self.send_alert_email(mentor_email, student_data, consolidated)

    def _is_email_configured(self) -> bool:
        """Check if email configuration is set up"""
        return bool(self.config.MAIL_USERNAME and self.config.MAIL_PASSWORD)

    # ============================================================
    # EMAIL TEMPLATES
    # ============================================================

    def _generate_alert_email_text(self, student_data: dict, alert: dict) -> str:
        """Generate plain text email body"""
        student_name = student_data.get('name', 'Unknown')
        student_id = student_data.get('student_id', 'N/A')
        department = student_data.get('department', 'N/A')
        alert_type = alert['alert_type'].replace('_', ' ').title()
        alert_message = alert['alert_message']

        lines = [
            f"🚨 MENTOR ALERT NOTIFICATION",
            f"=" * 50,
            f"",
            f"Dear Mentor,",
            f"",
            f"This is an automated alert from the Placement Predictor System.",
            f"",
            f"─" * 40,
            f"ALERT TYPE: {alert_type}",
            f"─" * 40,
            f"",
            f"Alert: {alert_message}",
            f"",
            f"─" * 40,
            f"STUDENT DETAILS",
            f"─" * 40,
            f"",
            f"  Name:            {student_name}",
            f"  Student ID:      {student_id}",
            f"  Department:      {department}",
            f"  Email:           {student_data.get('email', 'N/A')}",
            f"  CGPA:            {student_data.get('cgpa', 'N/A')}",
            f"  Programming:     {student_data.get('programming_skill', 'N/A')}/100",
            f"  Communication:   {student_data.get('communication_skill', 'N/A')}/100",
            f"  Resume Score:    {student_data.get('resume_score', 'N/A')}/100",
            f"  Aptitude:        {student_data.get('aptitude_score', 'N/A')}/100",
            f"  Technical:       {student_data.get('technical_score', 'N/A')}/100",
            f""
        ]

        # Weak areas
        weak_areas = alert.get('weak_areas', [])
        if weak_areas:
            lines.extend([
                f"─" * 40,
                f"WEAK AREAS IDENTIFIED",
                f"─" * 40,
                f""
            ])
            for area in weak_areas:
                lines.append(f"  ⚠️  {area}")

        # Suggestions
        suggestions = alert.get('suggestions', [])
        if suggestions:
            lines.extend([
                f"",
                f"─" * 40,
                f"IMPROVEMENT SUGGESTIONS",
                f"─" * 40,
                f""
            ])
            for i, suggestion in enumerate(suggestions, 1):
                lines.append(f"  {i}. {suggestion}")

        # Prediction result
        prediction = alert.get('prediction_result', 'N/A')
        if prediction != 'N/A':
            lines.extend([
                f"",
                f"─" * 40,
                f"PREDICTION RESULT: {prediction}",
                f"─" * 40,
            ])

        lines.extend([
            f"",
            f"─" * 40,
            f"RECOMMENDED ACTION",
            f"─" * 40,
            f"",
            f"Please schedule a meeting with this student to discuss",
            f"their progress and provide guidance on the areas above.",
            f"",
            f"Generated by: Placement Predictor System",
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"─" * 50,
            f"This is an automated notification. Please do not reply.",
            f""
        ])

        return '\n'.join(lines)

    def _generate_alert_email_html(self, student_data: dict, alert: dict) -> str:
        """Generate HTML email body"""
        student_name = student_data.get('name', 'Unknown')
        student_id = student_data.get('student_id', 'N/A')
        department = student_data.get('department', 'N/A')
        alert_type = alert['alert_type'].replace('_', ' ').title()
        alert_message = alert['alert_message']

        # Build weak areas HTML
        weak_areas_html = ''
        for area in alert.get('weak_areas', []):
            weak_areas_html += f'<li style="margin: 8px 0; color: #dc2626;">⚠️ {area}</li>'

        # Build suggestions HTML
        suggestions_html = ''
        for i, suggestion in enumerate(alert.get('suggestions', []), 1):
            suggestions_html += f'<li style="margin: 8px 0; color: #374151;">{i}. {suggestion}</li>'

        # Student info rows
        info_rows = [
            ('Name', student_name),
            ('Student ID', student_id),
            ('Department', department),
            ('Email', student_data.get('email', 'N/A')),
            ('CGPA', str(student_data.get('cgpa', 'N/A'))),
            ('Programming', f"{student_data.get('programming_skill', 'N/A')}/100"),
            ('Communication', f"{student_data.get('communication_skill', 'N/A')}/100"),
            ('Resume Score', f"{student_data.get('resume_score', 'N/A')}/100"),
        ]

        info_html = ''
        for label, value in info_rows:
            info_html += f"""
            <tr>
                <td style="padding: 8px 12px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-weight: 600;">{label}</td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #e5e7eb; color: #111827;">{value}</td>
            </tr>"""

        severity_color = '#dc2626' if alert['alert_type'] in ['low_cgpa', 'low_probability', 'low_programming'] else '#f59e0b'
        badge_class = 'critical' if alert.get('prediction_result') == 'At Risk' else 'warning'

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f3f4f6; }}
                .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #1e40af, #3b82f6); padding: 30px; text-align: center; }}
                .header h1 {{ color: #ffffff; margin: 0; font-size: 22px; }}
                .header p {{ color: #bfdbfe; margin: 8px 0 0; font-size: 14px; }}
                .alert-banner {{ background: {severity_color}; padding: 16px 24px; text-align: center; }}
                .alert-banner h2 {{ color: #ffffff; margin: 0; font-size: 18px; }}
                .alert-banner p {{ color: #fef3c7; margin: 8px 0 0; font-size: 14px; }}
                .section {{ padding: 20px 24px; }}
                .section h3 {{ color: #1e40af; font-size: 16px; margin: 0 0 16px; padding-bottom: 8px; border-bottom: 2px solid #e5e7eb; }}
                table {{ width: 100%; border-collapse: collapse; }}
                ul {{ padding-left: 20px; margin: 0; }}
                .footer {{ background: #f9fafb; padding: 20px 24px; text-align: center; color: #9ca3af; font-size: 12px; }}
                .badge {{ display: inline-block; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 600; }}
                .badge-critical {{ background: #fef2f2; color: #dc2626; }}
                .badge-warning {{ background: #fffbeb; color: #d97706; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Mentor Alert Notification</h1>
                    <p>Placement Predictor System</p>
                </div>

                <div class="alert-banner">
                    <h2>{alert_type}</h2>
                    <p>{alert_message}</p>
                </div>

                <div class="section">
                    <h3>👤 Student Details</h3>
                    <table>
                        {info_html}
                    </table>
                </div>

                <div class="section">
                    <h3>⚠️ Weak Areas Identified</h3>
                    <ul>
                        {weak_areas_html if weak_areas_html else '<li style="color: #6b7280;">No specific weak areas identified</li>'}
                    </ul>
                </div>

                <div class="section">
                    <h3>💡 Improvement Suggestions</h3>
                    <ul>
                        {suggestions_html if suggestions_html else '<li style="color: #6b7280;">No suggestions available</li>'}
                    </ul>
                </div>

                <div class="section" style="background: #f0fdf4; border-top: 2px solid #22c55e;">
                    <h3 style="color: #16a34a;">✅ Recommended Action</h3>
                    <p style="color: #374151; line-height: 1.6;">
                        Please schedule a meeting with <strong>{student_name}</strong> to discuss
                        their progress and provide guidance on the areas mentioned above.
                    </p>
                    <p style="color: #6b7280; font-size: 13px; margin-top: 12px;">
                        Prediction Result: <span class="badge badge-{badge_class}">{alert.get('prediction_result', 'N/A')}</span>
                    </p>
                </div>

                <div class="footer">
                    <p>Generated by Placement Predictor System</p>
                    <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p style="margin-top: 8px; color: #d1d5db;">This is an automated notification. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    # ============================================================
    # ALERT MANAGEMENT
    # ============================================================

    def process_student(self, student_data: dict, prediction_result: dict = None) -> Dict:
        """
        Process a single student: detect alerts and send email to mentor

        Args:
            student_data: Dict with student information
            prediction_result: Optional prediction result

        Returns:
            Dict with processing results
        """
        result = {
            'student_name': student_data.get('name', 'Unknown'),
            'student_id': student_data.get('student_id', 'N/A'),
            'mentor_email': student_data.get('mentor_email', 'Not assigned'),
            'alerts_detected': 0,
            'email_sent': False,
            'alerts': []
        }

        # Detect alerts
        alerts = self.detect_alerts(student_data, prediction_result)

        # Filter out 'no_mentor' alert for processing
        actionable_alerts = [a for a in alerts if a['alert_type'] != 'no_mentor']
        result['alerts_detected'] = len(actionable_alerts)
        result['alerts'] = alerts

        if actionable_alerts:
            mentor_email = student_data.get('mentor_email', '')
            if mentor_email:
                # Send comprehensive alert
                email_sent = self.send_comprehensive_alert(
                    mentor_email, student_data, actionable_alerts
                )
                result['email_sent'] = email_sent

        return result

    def process_students_batch(self, students_data: List[dict],
                                predictions: List[dict] = None) -> Dict:
        """
        Process multiple students for alert detection

        Args:
            students_data: List of student dicts
            predictions: Optional list of prediction results (aligned with students)

        Returns:
            Dict with batch processing statistics
        """
        results = {
            'total_students': len(students_data),
            'students_with_alerts': 0,
            'emails_sent': 0,
            'total_alerts': 0,
            'alert_type_counts': {},
            'student_results': []
        }

        for i, student in enumerate(students_data):
            prediction = predictions[i] if predictions and i < len(predictions) else None
            proc_result = self.process_student(student, prediction)

            results['student_results'].append(proc_result)

            if proc_result['alerts_detected'] > 0:
                results['students_with_alerts'] += 1
                results['total_alerts'] += proc_result['alerts_detected']

            if proc_result['email_sent']:
                results['emails_sent'] += 1

            # Count alert types
            for alert in proc_result.get('alerts', []):
                alert_type = alert['alert_type']
                results['alert_type_counts'][alert_type] = \
                    results['alert_type_counts'].get(alert_type, 0) + 1

        return results

    def get_alert_statistics(self, students_processed: List[dict]) -> Dict:
        """
        Get statistics from processed students

        Args:
            students_processed: List of process_student results

        Returns:
            Dict with alert statistics
        """
        stats = {
            'total_students': len(students_processed),
            'students_with_alerts': 0,
            'total_alerts': 0,
            'email_success_rate': 0,
            'common_weak_areas': {},
            'alert_type_distribution': {}
        }

        total_emails_attempted = 0
        total_emails_sent = 0

        for result in students_processed:
            if result['alerts_detected'] > 0:
                stats['students_with_alerts'] += 1
                stats['total_alerts'] += result['alerts_detected']

            if result.get('mentor_email') != 'Not assigned':
                total_emails_attempted += 1
                if result.get('email_sent'):
                    total_emails_sent += 1

            # Count weak areas
            for alert in result.get('alerts', []):
                alert_type = alert['alert_type']
                stats['alert_type_distribution'][alert_type] = \
                    stats['alert_type_distribution'].get(alert_type, 0) + 1

                for area in alert.get('weak_areas', []):
                    stats['common_weak_areas'][area] = \
                        stats['common_weak_areas'].get(area, 0) + 1

        stats['email_success_rate'] = round(
            (total_emails_sent / total_emails_attempted * 100) if total_emails_attempted > 0 else 0,
            2
        )

        # Sort weak areas by frequency
        stats['common_weak_areas'] = dict(
            sorted(stats['common_weak_areas'].items(),
                   key=lambda x: x[1], reverse=True)
        )

        return stats

    def format_alert_email(self, mentor_email, student_name, alerts, prediction_result=None):
        """
        Format a comprehensive alert email (convenience method for testing)

        Args:
            mentor_email: Mentor's email address
            student_name: Student's name
            alerts: List of alert dicts
            prediction_result: Optional prediction result dict

        Returns:
            Formatted email HTML as string
        """
        # Create a consolidated alert from all alerts
        consolidated = {
            'alert_type': 'comprehensive',
            'alert_message': f"Multiple areas need attention for student {student_name}",
            'weak_areas': list(set(
                area for alert in alerts
                for area in alert.get('weak_areas', [])
            )),
            'suggestions': list(set(
                sugg for alert in alerts
                for sugg in alert.get('suggestions', [])
            )),
            'prediction_result': prediction_result.get('prediction_label', 'N/A') if prediction_result else 'N/A',
            'alerts_count': len(alerts),
            'individual_alerts': alerts
        }

        student_data = {'name': student_name, 'mentor_email': mentor_email}
        return self._generate_alert_email_html(student_data, consolidated)

    def format_email_subject(self, student_name, alert_types):
        """
        Format an email subject line (convenience method for testing)

        Args:
            student_name: Student's name
            alert_types: List of alert type strings

        Returns:
            Formatted subject string
        """
        primary_type = alert_types[0].replace('_', ' ').title() if alert_types else 'Alert'
        return f"🚨 Mentor Alert: {student_name} - {primary_type}"

    def generate_alert_report(self, batch_results: Dict) -> str:
        """
        Generate a human-readable alert report

        Args:
            batch_results: Results from process_students_batch

        Returns:
            Formatted report string
        """
        lines = [
            "=" * 60,
            "📊 MENTOR ALERT SYSTEM REPORT",
            "=" * 60,
            f"",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"📈 Summary:",
            f"  Total Students Processed: {batch_results.get('total_students', 0)}",
            f"  Students with Alerts:     {batch_results.get('students_with_alerts', 0)}",
            f"  Total Alerts Detected:    {batch_results.get('total_alerts', 0)}",
            f"  Emails Sent Successfully: {batch_results.get('emails_sent', 0)}",
            f""
        ]

        # Alert type distribution
        alert_counts = batch_results.get('alert_type_counts', {})
        if alert_counts:
            lines.extend([
                f"📋 Alert Type Distribution:",
            ])
            for alert_type, count in sorted(alert_counts.items(), key=lambda x: x[1], reverse=True):
                label = alert_type.replace('_', ' ').title()
                bar = '█' * min(count, 20)
                lines.append(f"  {label:<25} {bar} {count}")
            lines.append("")

        # Student details
        student_results = batch_results.get('student_results', [])
        alert_students = [r for r in student_results if r['alerts_detected'] > 0]

        if alert_students:
            lines.extend([
                f"👤 Students Needing Attention:",
                f"  {'─' * 50}"
            ])
            for result in alert_students[:10]:  # Show top 10
                lines.append(
                    f"  • {result['student_name']:<20} | "
                    f"{result['alerts_detected']} alert(s) | "
                    f"Email: {'✅ Sent' if result['email_sent'] else '❌ Failed'}"
                )

            if len(alert_students) > 10:
                lines.append(f"  ... and {len(alert_students) - 10} more students")

        lines.extend([
            f"",
            f"=" * 60,
            f"✅ Report Generated Successfully",
            f"=" * 60
        ])

        return '\n'.join(lines)

    def test_email_connection(self) -> Dict:
        """
        Test the SMTP email connection

        Returns:
            Dict with connection test results
        """
        result = {
            'configured': False,
            'server_reachable': False,
            'authenticated': False,
            'error': None
        }

        if not self._is_email_configured():
            result['error'] = 'Email not configured. Set MAIL_USERNAME and MAIL_PASSWORD.'
            return result

        result['configured'] = True

        try:
            with smtplib.SMTP(self.config.MAIL_SERVER, self.config.MAIL_PORT, timeout=10) as server:
                server.ehlo()
                if self.config.MAIL_USE_TLS:
                    server.starttls()
                    server.ehlo()

                result['server_reachable'] = True

                if self.config.MAIL_USERNAME and self.config.MAIL_PASSWORD:
                    server.login(self.config.MAIL_USERNAME, self.config.MAIL_PASSWORD)
                    result['authenticated'] = True

        except smtplib.SMTPAuthenticationError as e:
            result['error'] = f'Authentication failed: {str(e)}'
        except smtplib.SMTPException as e:
            result['error'] = f'SMTP error: {str(e)}'
        except ConnectionRefusedError:
            result['error'] = f'Connection refused to {self.config.MAIL_SERVER}:{self.config.MAIL_PORT}'
        except Exception as e:
            result['error'] = str(e)

        return result


def check_and_alert_student(student_data: dict, prediction_result: dict = None,
                             config=None) -> Dict:
    """
    Convenience function to detect alerts and notify mentor for a single student

    Args:
        student_data: Dict with student information
        prediction_result: Optional prediction results
        config: Optional config object

    Returns:
        Dict with processing results
    """
    system = MentorAlertSystem(config)
    return system.process_student(student_data, prediction_result)


def batch_check_and_alert(students_data: List[dict], predictions: List[dict] = None,
                           config=None) -> Dict:
    """
    Convenience function for batch processing

    Args:
        students_data: List of student dicts
        predictions: Optional list of prediction results
        config: Optional config object

    Returns:
        Dict with batch processing results
    """
    system = MentorAlertSystem(config)
    return system.process_students_batch(students_data, predictions)


if __name__ == '__main__':
    print("=" * 60)
    print("🚨 MENTOR ALERT SYSTEM TEST")
    print("=" * 60)

    # Initialize alert system with default config
    alert_system = MentorAlertSystem()

    # Test email configuration
    print("\n📧 Testing email configuration...")
    email_test = alert_system.test_email_connection()
    print(f"   Configured: {email_test['configured']}")
    print(f"   Server Reachable: {email_test['server_reachable']}")
    if email_test.get('error'):
        print(f"   Error: {email_test['error']}")
    if not email_test['configured']:
        print("   ℹ️  Set MAIL_USERNAME and MAIL_PASSWORD env vars to enable email")

    # Test student with low performance
    test_student = {
        'student_id': 'STU1001',
        'name': 'Test Student',
        'email': 'test.student@college.edu',
        'mentor_email': 'mentor@college.edu',
        'department': 'Computer Science',
        'cgpa': 6.2,
        'programming_skill': 35,
        'communication_skill': 40,
        'resume_score': 30,
        'aptitude_score': 55,
        'technical_score': 45,
        'internships': 0,
        'projects': 1,
        'backlogs': 2,
        'attendance': 72
    }

    test_prediction = {
        'prediction': 0,
        'prediction_label': 'Not Placed ❌',
        'probability': 28.5,
        'confidence': 78.2
    }

    print(f"\n👤 Testing alerts for: {test_student['name']}")
    print(f"   CGPA: {test_student['cgpa']}")
    print(f"   Programming: {test_student['programming_skill']}")
    print(f"   Communication: {test_student['communication_skill']}")
    print(f"   Resume Score: {test_student['resume_score']}")

    # Detect alerts
    alerts = alert_system.detect_alerts(test_student, test_prediction)
    print(f"\n🔍 Alerts detected: {len(alerts)}")
    for alert in alerts:
        print(f"\n   {'─' * 40}")
        print(f"   Type: {alert['alert_type'].replace('_', ' ').title()}")
        print(f"   Message: {alert['alert_message']}")
        print(f"   Weak Areas: {', '.join(alert.get('weak_areas', []))}")
        print(f"   Suggestions:")
        for s in alert.get('suggestions', [])[:3]:
            print(f"      • {s}")

    # Process student (without sending email)
    print(f"\n{'=' * 60}")
    print(f"📊 Processing test student...")
    result = alert_system.process_student(test_student, test_prediction)
    print(f"   Alerts Detected: {result['alerts_detected']}")
    print(f"   Email Sent: {result['email_sent']}")

    # Generate report
    print(f"\n{'=' * 60}")
    print(alert_system.generate_alert_report({
        'total_students': 1,
        'students_with_alerts': 1,
        'total_alerts': len(alerts),
        'emails_sent': 0,
        'alert_type_counts': {a['alert_type']: 1 for a in alerts},
        'student_results': [result]
    }))
