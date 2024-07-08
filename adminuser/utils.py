# employees/utils.py (create a new file)
import random
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

def generate_random_password():
    chars = string.ascii_lowercase + string.digits + string.punctuation
    return ''.join(random.choice(chars) for i in range(7))

def send_activation_email(employee, site_url, password):
    emailOfSender = 'resumate1nfo1@gmail.com'
    subject = 'Login to Your Account on ResuMate'
    message = render_to_string('adminuser/activation_email.html', {
        'employee': employee,
        'site_url': site_url,
        'password': password
    })
    print(site_url)
    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[employee.user.email, ], reply_to=[emailOfSender, ])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

    # send_mail(subject, message, '', [employee.email])
