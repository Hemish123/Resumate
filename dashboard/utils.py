import string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from recruit_management.settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives

def send_success_email(candidate, job_opening):
    print('in', candidate, job_opening)
    emailOfSender = EMAIL_HOST_USER
    subject = 'Application submitted successfully!'
    message = render_to_string('dashboard/success_email.html', {
        'candidate': candidate,
        'job_opening': job_opening
    })

    
    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[candidate.email, ], reply_to=[emailOfSender, ])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)