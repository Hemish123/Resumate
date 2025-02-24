import string, json
from django.core.mail import send_mail
from django.template.loader import render_to_string
from recruit_management.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from django.core.mail import EmailMultiAlternatives
from candidate.models import ResumeAnalysis

def send_success_email(candidate, job_opening):
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


def send_stage_change_email(user, candidate, job_opening, stage):
    emailOfSender = user.email
    subject = 'Application status!'
    message = render_to_string('dashboard/stages_email.html', {
        'candidate': candidate,
        'job_opening': job_opening,
        'stage': stage
    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[candidate.email, ], reply_to=[emailOfSender, ])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def send_hired_email(user, candidate, job_opening):
    emailOfSender = user.email
    subject = 'Congratulations!'
    message = render_to_string('dashboard/congratulations_email.html', {
        'candidate': candidate,
        'job_opening': job_opening
    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[candidate.email, ], reply_to=[emailOfSender, ])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def send_rejected_email(user, candidate, job_opening):
    emailOfSender = user.email
    subject = 'Application status!'
    message = render_to_string('dashboard/reject_email.html', {
        'candidate': candidate,
        'job_opening': job_opening
    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[candidate.email, ], reply_to=[emailOfSender, ])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def send_interview_email(user, candidate, job_opening, event):
    emailOfSender = user.email
    subject = 'Interview update!'
    message = render_to_string('dashboard/interview_email.html', {
        'candidate': candidate,
        'job_opening': job_opening,
        'event': event
    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[candidate.email, ], reply_to=[emailOfSender, ])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def send_schedule_interview_email(user, employee, event):
    emailOfSender = user.email
    subject = 'Interview scheduled!'
    message = render_to_string('dashboard/interview_schedule_email.html', {
        'employee': employee,
        'event': event
    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[employee , ], reply_to=[emailOfSender, ])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def send_thankyou_email(user, candidate, job_opening):
    emailOfSender = user.email
    subject = 'Thank You!'
    message = render_to_string('dashboard/thanks_email.html', {
        'candidate': candidate,
        'job_opening': job_opening
    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[candidate.email, ], reply_to=[emailOfSender, ])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def new_application_email(candidate, job_opening, e, site_url):
    emailOfSender = EMAIL_HOST_USER
    subject = 'New Application!'
    approve_url = f"{site_url}/candidate/action/{candidate.id}/approve/"
    reject_url = f"{site_url}/candidate/action/{candidate.id}/reject/"
    response_text = ResumeAnalysis.objects.get(candidate=candidate, job_opening=job_opening).response_text
    text = json.loads(response_text)
    message = render_to_string('dashboard/new_application_email.html', {
        'candidate': candidate,
        'job_opening': job_opening,
        'site_url': site_url,
        'approve_url': approve_url,
        'reject_url': reject_url,
        'text': text
    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[e.user.email, ], reply_to=[emailOfSender, ])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def send_job_opening_email(user, candidate, job_opening, site_url):
    emailOfSender = user.email
    subject = f'Apply for {job_opening.designation} at {job_opening.company}!'
    message = render_to_string('dashboard/share_job_opening_email.html', {
        'candidate': candidate,
        'job_opening': job_opening,
        'required_skills' : job_opening.requiredskills.split(','),
        'site_url': site_url
    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[candidate.email, ], reply_to=[emailOfSender, ])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def new_opening_email(job_opening, e):
    emailOfSender = EMAIL_HOST_USER
    subject = 'New Opening assigned to you!'
    message = render_to_string('dashboard/new_opening_assign.html', {
        'employee': e,
        'job_opening': job_opening,

    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[e.user.email, ], reply_to=[emailOfSender, ])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)