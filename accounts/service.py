# tasks.py
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from decouple import config
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_verification_task(self, receiver_email, first_name, code):
    """
    Celery task to send email verification
    """
    try:
        subject = 'Email Verification Required'
        text_content = f'''
        Hello {first_name},

        Thank you for signing up! To secure your account, please verify your email address.

        Your 4-digit verification code is: {code}

        Enter this code on our website to complete the verification process.

        If you didn't request this, please ignore this email.

        Best regards,  
        Your Company Team
        '''

        from_email = config("EMAIL_HOST_USER")
        to = [receiver_email]
        html_content = f"""
            <div style="font-family: 'Helvetica Neue', Arial, sans-serif; background: #f9f9f9; padding: 40px 20px;">
              <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #6D5DF6, #1E90FF); padding: 20px; text-align: center;">
                  <h1 style="color: #fff; margin: 0; font-size: 28px;">Verify Your Email 🚀</h1>
                </div>
                <!-- Main Content -->
                <div style="padding: 30px; text-align: center;">
                  <p style="color: #555; font-size: 16px; margin-bottom: 20px;">
                    You're just one step away from activating your account!
                  </p>
                  <div style="background: #F4F8FF; border-radius: 8px; padding: 15px 20px; display: inline-block; margin-bottom: 20px;">
                    <span style="color: #1E90FF; font-size: 20px; font-weight: bold;">Your Verification Code:</span>
                    <div style="color: #6D5DF6; font-size: 36px; font-weight: bold; margin-top: 10px;">
                      {code}
                    </div>
                  </div>
                  <p style="color: #555; font-size: 16px; margin-bottom: 30px;">
                    Enter this code on our website to complete the verification process.
                  </p>
                </div>
                <!-- Footer -->
                <div style="background: #f1f1f1; padding: 15px 20px; text-align: center;">
                  <p style="color: #888; font-size: 12px; margin: 0;">
                    If you didn't request this email, please ignore it.
                  </p>
                  <p style="color: #888; font-size: 12px; margin: 5px 0 0;">
                    Need help? <a href="mailto:support@yourcompany.com" style="color: #1E90FF; text-decoration: none;">Contact our support team</a>.
                  </p>
                  <p style="color: #888; font-size: 12px; margin: 15px 0 0;">
                    Best regards,<br>
                    <strong>Your Company Team</strong>
                  </p>
                </div>
              </div>
            </div>
            """

        email = EmailMultiAlternatives(subject, text_content, from_email, to)
        email.attach_alternative(html_content, 'text/html')
        email.send()

        logger.info(f"Email verification sent successfully to {receiver_email}")
        return f"Email sent to {receiver_email}"

    except Exception as exc:
        logger.error(f"Failed to send email verification to {receiver_email}: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_password_verification_task(self, email, first_name, code):
    """
    Celery task to send password reset verification
    """
    try:
        subject = 'Password Reset Request'
        to = [email]
        from_email = config("EMAIL_HOST_USER")

        text_content = f'''
        Hello {first_name},

        We received a request to reset the password for your account.

        Your 4-digit password reset code is: {code}

        Enter this code on our website to set a new password.

        If you did not request a password reset, you can safely ignore this email and no changes will be made.

        For your security, do not share this code with anyone. If you need assistance, please contact our support team.

        Best regards,  
        Your Company Team
        '''

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #333;">Hello, {first_name} 👋</h2>
            <p style="color: #555; font-size: 16px;">
                We received a request to reset the password for your account.
            </p>
            <p style="color: #333; font-size: 18px; font-weight: bold; text-align: center;">
                Your 4-digit reset code: <span style="color: #007BFF;">{code}</span>
            </p>
            <p style="color: #555; font-size: 16px;">
                Enter this code on our website to choose a new password for your account.
            </p>
            <p style="color: #777; font-size: 14px;">
                <strong>Note:</strong> For security, do not share this code with anyone. The code is valid for a limited time.
            </p>
            <p style="color: #777; font-size: 14px;">
                If you did not request a password reset, you can safely ignore this email and your password will remain unchanged.
            </p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="color: #888; font-size: 12px;">
                Need help? Contact our <a href="https://yourcompany.example.com/support" style="color: #007BFF; text-decoration: none;">Support Team</a>.
            </p>
            <p style="color: #888; font-size: 12px;">
                Best regards, <br>
                <strong>Your Company Team</strong>
            </p>
        </div>
        """

        email_msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        email_msg.attach_alternative(html_content, 'text/html')
        email_msg.send()

        logger.info(f"Password reset email sent successfully to {email}")
        return f"Password reset email sent to {email}"

    except Exception as exc:
        logger.error(f"Failed to send password reset email to {email}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_email_change_verification_task(self, receiver_new_email, first_name, code):
    """
    Celery task to send email change verification
    """
    try:
        subject = 'Confirm Your New Email Address'
        from_email = config("EMAIL_HOST_USER")
        to = [receiver_new_email]

        text_content = f'''
            Hello {first_name},

            You've requested to change your email address associated with your account. 

            To verify your new email, please enter the following 4-digit verification code:

            {code}

            If you didn't request this change, please ignore this email.

            Best regards,  
            Your Company Team
            '''

        html_content = f"""
                <div style="font-family: 'Helvetica Neue', Arial, sans-serif; background: #f9f9f9; padding: 40px 20px;">
                  <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                    <!-- Header -->
                    <div style="background: linear-gradient(135deg, #6D5DF6, #1E90FF); padding: 20px; text-align: center;">
                      <h1 style="color: #fff; margin: 0; font-size: 24px;">Confirm Your New Email Address</h1>
                    </div>
                    <!-- Main Content -->
                    <div style="padding: 30px; text-align: center;">
                      <p style="color: #555; font-size: 16px; margin-bottom: 20px;">
                        You've requested to update your email address. To proceed, please enter the following code:
                      </p>
                      <div style="background: #F4F8FF; border-radius: 8px; padding: 15px 20px; display: inline-block; margin-bottom: 20px;">
                        <span style="color: #1E90FF; font-size: 20px; font-weight: bold;">Your Verification Code:</span>
                        <div style="color: #6D5DF6; font-size: 36px; font-weight: bold; margin-top: 10px;">
                          {code}
                        </div>
                      </div>
                      <p style="color: #555; font-size: 16px; margin-bottom: 30px;">
                        Enter this code on our website to verify your new email.
                      </p>
                    </div>
                    <!-- Footer -->
                    <div style="background: #f1f1f1; padding: 15px 20px; text-align: center;">
                      <p style="color: #888; font-size: 12px; margin: 0;">
                        If you didn't request this email change, you can ignore this email.
                      </p>
                      <p style="color: #888; font-size: 12px; margin: 5px 0 0;">
                        Need help? <a href="mailto:support@yourcompany.com" style="color: #1E90FF; text-decoration: none;">Contact our support team</a>.
                      </p>
                      <p style="color: #888; font-size: 12px; margin: 15px 0 0;">
                        Best regards,<br>
                        <strong>Your Company Team</strong>
                      </p>
                    </div>
                  </div>
                </div>
            """

        email = EmailMultiAlternatives(subject, text_content, from_email, to)
        email.attach_alternative(html_content, 'text/html')
        email.send()

        logger.info(f"Email change verification sent successfully to {receiver_new_email}")
        return f"Email change verification sent to {receiver_new_email}"

    except Exception as exc:
        logger.error(f"Failed to send email change verification to {receiver_new_email}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


def send_email_verification(receiver_email, first_name, code):
    """
    Queue email verification task
    """
    return send_email_verification_task.delay(receiver_email, first_name, code)


def send_password_verification(email, first_name, code):
    """
    Queue password verification task
    """
    return send_password_verification_task.delay(email, first_name, code)


def send_email_to_verify_email(receiver_new_email, first_name, code):
    """
    Queue email change verification task
    """
    return send_email_change_verification_task.delay(receiver_new_email, first_name, code)