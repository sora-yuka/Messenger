from config.celery import app
from decouple import config
from django.core.mail import send_mail

from twilio.rest import Client


@app.task
def send_email_verification_code(email, activation_code):
    full_link = f'http://{config("ALLOWED_HOSTS").split(",")[1]}:{config("MAIN_PORT")}/api/v1/account/activate/{activation_code}'
    send_mail(
        'from messenger',
        f'Your activation link {full_link}',
        config('EMAIL_HOST_USER'),
        [email]
    )


@app.task
def send_password_recovery(email, activation_code):
    full_link = f'http://{config("ALLOWED_HOSTS").split(",")[1]}:{config("MAIN_PORT")}/api/v1/account/recovery/{activation_code}'
    send_mail(
        "Password recovery",
        f"Перейдите по ссылке чтобы сбросить пароль:  {full_link}",
        config('EMAIL_HOST_USER'),
        [email]
    )


@app.task
def send_sms_verification_code(code, receiver):
    account_sid = config('ACCOUNT_SID')
    auth_token = config('AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
            body=f'Your verification code: {code}',
            from_=config('PHONE_NUMBER'),
            to=receiver
        )
    except Exception as e:
        # handle any exceptions here
        print(f"Error: {e}")
        return
    return message.sid

