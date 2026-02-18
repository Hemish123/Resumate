import string, json
from django.core.mail import send_mail
from django.template.loader import render_to_string
from recruit_management.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD,DEFAULT_FROM_EMAIL
from django.core.mail import EmailMultiAlternatives
from candidate.models import ResumeAnalysis
from django.utils.html import strip_tags
from django.conf import settings

def send_success_email(candidate, job_opening):
    emailOfSender = DEFAULT_FROM_EMAIL
    subject = 'Application submitted successfully!'
    message = render_to_string('dashboard/success_email.html', {
        'candidate': candidate,
        'job_opening': job_opening
    })

    
    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[candidate.email, ], reply_to=['info@jmsadvisory.in'])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)


def send_stage_change_email(user, candidate, job_opening, stage):
    emailOfSender = DEFAULT_FROM_EMAIL
    subject = 'Application status!'
    message = render_to_string('dashboard/stages_email.html', {
        'candidate': candidate,
        'job_opening': job_opening,
        'stage': stage
    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[candidate.email, ], reply_to=['info@jmsadvisory.in'])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def send_hired_email(user, candidate, job_opening):
    emailOfSender = DEFAULT_FROM_EMAIL
    subject = 'Congratulations!'
    message = render_to_string('dashboard/congratulations_email.html', {
        'candidate': candidate,
        'job_opening': job_opening
    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[candidate.email, ], reply_to=['info@jmsadvisory.in'])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def send_rejected_email(user, candidate, job_opening):
    emailOfSender = DEFAULT_FROM_EMAIL
    subject = 'Application status!'
    message = render_to_string('dashboard/reject_email.html', {
        'candidate': candidate,
        'job_opening': job_opening
    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[candidate.email, ], reply_to=['info@jmsadvisory.in'])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def send_interview_email(user, candidate, job_opening, event):
    emailOfSender = DEFAULT_FROM_EMAIL
    subject = 'Interview update!'
    message = render_to_string('dashboard/interview_email.html', {
        'candidate': candidate,
        'job_opening': job_opening,
        'event': event
    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[candidate.email, ], reply_to=['info@jmsadvisory.in'])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def send_schedule_interview_email(user, employee, event):
    emailOfSender = DEFAULT_FROM_EMAIL
    subject = 'Interview scheduled!'
    message = render_to_string('dashboard/interview_schedule_email.html', {
        'employee': employee,
        'event': event
    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[employee , ], reply_to=['info@jmsadvisory.in'])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def send_thankyou_email(user, candidate, job_opening):
    emailOfSender = DEFAULT_FROM_EMAIL
    subject = 'Thank You!'
    message = render_to_string('dashboard/thanks_email.html', {
        'candidate': candidate,
        'job_opening': job_opening
    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[candidate.email, ], reply_to=['info@jmsadvisory.in'])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def new_application_email(candidate, job_opening, e, site_url):
    emailOfSender = DEFAULT_FROM_EMAIL
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
                                          to=[e.user.email, ], reply_to=['info@jmsadvisory.in'])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def send_job_opening_email(user, candidate, job_opening, site_url):
    emailOfSender = DEFAULT_FROM_EMAIL
    subject = f'Apply for {job_opening.designation} at {job_opening.company}!'
    message = render_to_string('dashboard/share_job_opening_email.html', {
        'candidate': candidate,
        'job_opening': job_opening,
        'required_skills' : job_opening.requiredskills.split(','),
        'site_url': site_url
    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[candidate.email, ], reply_to=['info@jmsadvisory.in'])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

def new_opening_email(job_opening, e):
    emailOfSender = DEFAULT_FROM_EMAIL
    subject = 'New Opening assigned to you!'
    message = render_to_string('dashboard/new_opening_assign.html', {
        'employee': e,
        'job_opening': job_opening,

    })

    emailMessage = EmailMultiAlternatives(subject=subject, body='text_content', from_email=emailOfSender,
                                          to=[e.user.email, ], reply_to=['info@jmsadvisory.in'])
    emailMessage.attach_alternative(message, "text/html")
    emailMessage.send(fail_silently=False)

from django.contrib.sites.models import Site
def send_interview_invitation_email(candidate, job_opening_id, additional_notes=''):
    """
    Send interview invitation email to candidate
    """
    current_site = Site.objects.get_current()
    
    # Determine protocol (http for local, https for production)
    protocol = 'https' if not settings.DEBUG else 'http'
    
    # Handle domain formatting
    domain = current_site.domain
    if domain.startswith('http://'):
        domain = domain.replace('http://', '')
    elif domain.startswith('https://'):
        domain = domain.replace('https://', '')
    
    # interview_url = f"{protocol}://{domain}/interviewbot/?job_opening={job_opening_id}&candidate={candidate.id}"
    interview_url = f"{protocol}://jivihire.com/interviewbot/?job_opening={job_opening_id}&candidate={candidate.id}"
    
    context = {
        'candidate_name': candidate.name,
        'interview_url': interview_url,
        'additional_notes': additional_notes,
        
    }
    
    # Render HTML email template
    html_message = render_to_string('dashboard/interview_invitation.html', context)
    plain_message = strip_tags(html_message)
    
    subject = f"Interview Invitation for {candidate.name}"
    
    return send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[candidate.email],
        fail_silently=False,
    )



# def create_single_candidate_pdf_weasy(candidate, job_opening):
#     # Render HTML from your template
#     html_string = render_to_string('candidate/candidate_analysis_pdf.html', {
#         'candidate': candidate,
#         'job_opening': job_opening,
#         'text': candidate.analysis.filter(job_opening=job_opening).first(),
#     })

#     # Create a temporary PDF file
#     tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
#     HTML(string=html_string, base_url=".").write_pdf(tmp_pdf.name)
#     tmp_pdf.close()
    
#     return tmp_pdf.name

from django.core.mail import EmailMessage
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from PyPDF2 import PdfMerger
import tempfile, os
from django.conf import settings
from django.utils.html import strip_tags
import mimetypes
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_stage_to_client_email(request,recruiter, candidate, job_opening, cc_list=None, recipient_type="client"):
    from weasyprint import HTML

    # # Fetch AI analysis safely
    # analysis = candidate.analysis.filter(job_opening=job_opening).first()

    # text = analysis  # In your templates, you use 'text' variable
    analysis_obj = candidate.analysis.filter(job_opening=job_opening).first()

    if analysis_obj and analysis_obj.response_text:
        if isinstance(analysis_obj.response_text, str):
            try:
                analysis = json.loads(analysis_obj.response_text)
            except json.JSONDecodeError:
                analysis = {}
        else:
            analysis = analysis_obj.response_text
    else:
        analysis = {}

    client = job_opening.client

    tracker_data = {
        "Candidate Name": candidate.name,
        "Current Profile": candidate.current_designation or "N/A",
        "Current Company": candidate.current_organization or "N/A",
        "Total Work Experience": f"{candidate.experience} years",
        "Current Location": candidate.location or "N/A",
        "Preferred Location": candidate.preferred_location or "N/A",
        "Education": candidate.education,
        "Number": candidate.contact,
        "Email ID": candidate.email,
        "Current CTC": candidate.current_ctc,
        "Expected CTC": candidate.expected_ctc,
        "Notice Period": f"{candidate.notice_period} days",
        "Share Date": candidate.share_date or "N/A",
        # "Recruiter": recruiter.user.get_full_name(),
    }

    assigned_recruiters = job_opening.assignemployee.all()
    recruiter_emails = [r.user.email for r in assigned_recruiters if r.user.email]

    recipients = [client.email] + recruiter_emails

    recipient_name = client.name if recipient_type == "client" else recruiter.user.get_full_name()

    # ✅ CREATE AI PDF
    ai_pdf = create_ai_analysis_pdf(candidate, job_opening,analysis=analysis)

    # ✅ MERGE AI PDF + RESUME
    final_pdf = merge_ai_pdf_with_resume(
        ai_pdf,
        candidate.upload_resume.path if candidate.upload_resume else None
    )

    html_message = render_to_string(
        "dashboard/sent_to_client_email.html",
        {
            "recipient_name": recipient_name,
            "candidate": candidate,
            "job_opening": job_opening,
            "tracker_data": tracker_data,
        },
    )

    subject = f"Candidate Sent to {recipient_name} | {job_opening.designation}"

    email = EmailMultiAlternatives(
        subject=subject,
        body="Please find attached candidate report + resume.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
        cc=cc_list or [],
    )

    # ✅ Read the PDF content and attach with specific filename
    with open(final_pdf, "rb") as f:
        pdf_content = f.read()
    # Example filename: "Candidate_Report_John_Doe.pdf"
    pdf_filename = f"Candidate_Report_{candidate.name.replace(' ', '_')}.pdf"

    email.attach(
        pdf_filename,
        pdf_content,
        mimetypes.guess_type(pdf_filename)[0] or "application/pdf"
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)

def create_ai_analysis_pdf(candidate, job_opening,analysis=None):
     # Use passed analysis or fetch it
    if not isinstance(analysis, dict):
        analysis = {}
        
    logo_path = os.path.join(
            settings.BASE_DIR,
            "dashboard/static/dashboard/img/icons/jmslogo.png"
        )
    clean_logo_path = logo_path.replace("\\", "/")

    html = render_to_string(
        "candidate/candidate_analysis_pdf.html",
        {
            "candidate": candidate,
            "job_opening": job_opening,
            # "analysis": candidate.analysis.filter(job_opening=job_opening).first(),
            "text":analysis,
            "logo_path": "file:///" + clean_logo_path,
        }
    )

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    HTML(string=html, base_url=settings.BASE_DIR).write_pdf(tmp.name)
    return tmp.name

def merge_ai_pdf_with_resume(ai_pdf, resume_path):
    merger = PdfMerger()
    merger.append(ai_pdf)

    if resume_path and os.path.exists(resume_path):
        merger.append(resume_path)

    final_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    merger.write(final_pdf.name)
    merger.close()

    return final_pdf.name
