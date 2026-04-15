import string, json
from django.core.mail import send_mail
from django.template.loader import render_to_string
from recruit_management.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD,DEFAULT_FROM_EMAIL
from django.core.mail import EmailMultiAlternatives
from candidate.models import ResumeAnalysis
from django.utils.html import strip_tags
from django.conf import settings
from .whatsapp_utils import send_whatsapp

_whatsapp_sent_cache = set()

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

    # send_whatsapp(
    #     candidate.contact,
    #     f"Hi {candidate.name},\n\n"
    #     f"Your application for *{job_opening.designation}* at "
    #     f"*{job_opening.company}* has been successfully submitted. ✅\n\n"
    #     f"We will keep you updated on the next steps.\n\n"
    #     f"- JMS Advisory"
    # )
    send_whatsapp(
        candidate.contact,
        f"🎉 *Application Received — JMS Advisory*\n\n"
        f"Hi {candidate.name},\n\n"
        f"Thank you for applying! Your application has been successfully submitted. ✅\n\n"
        f"📋 *Role:* {job_opening.designation}\n"
        f"🏢 *Company:* {job_opening.company}\n\n"
        f"Our team will review your profile and reach out with next steps shortly.\n\n"
        f"Warm regards,\n*JMS Advisory*\n info@jmsadvisory.in"
    )


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

    # send_whatsapp(
    #     candidate.contact,
    #     f"Hi {candidate.name},\n\n"
    #     f"There's an update on your application for "
    #     f"*{job_opening.designation}* at *{job_opening.company}*.\n\n"
    #     f"Current Status: *{stage.name}*\n\n"
    #     f"- JMS Advisory"
    # )
    send_whatsapp(
        candidate.contact,
        f"📢 *Application Update — JMS Advisory*\n\n"
        f"Hi {candidate.name},\n\n"
        f"There's an update on your application:\n\n"
        f"📋 *Role:* {job_opening.designation}\n"
        f"🏢 *Company:* {job_opening.company}\n"
        f"🔄 *Status:* {stage.name}\n\n"
        f"Our team will be in touch with further details soon. Stay tuned!\n\n"
        f"Best,\n*JMS Advisory*\n info@jmsadvisory.in"
    )

    

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

    # send_whatsapp(
    #     candidate.contact,
    #     f"Congratulations {candidate.name}! 🎉\n\n"
    #     f"We are thrilled to inform you that you have been selected "
    #     f"for the *{job_opening.designation}* position at "
    #     f"*{job_opening.company}*.\n\n"
    #     f"Please check your email for further details.\n\n"
    #     f"- JMS Advisory"
    # )
    send_whatsapp(
        candidate.contact,
        f"🎊 *Congratulations — JMS Advisory*\n\n"
        f"Hi {candidate.name},\n\n"
        f"We are delighted to share some *great news* with you! 🌟\n\n"
        f"✅ You have been *selected* for the role of:\n\n"
        f"📋 *Position:* {job_opening.designation}\n"
        f"🏢 *Company:* {job_opening.company}\n\n"
        f"Please check your email for the formal offer details and next steps.\n\n"
        f"Wishing you a wonderful start to this new journey! 🚀\n\n"
        f"Warm regards,\n*JMS Advisory*\n info@jmsadvisory.in"
    )

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

    # send_whatsapp(
    #     candidate.contact,
    #     f"Hi {candidate.name},\n\n"
    #     f"Thank you for your interest in the *{job_opening.designation}* "
    #     f"role at *{job_opening.company}*.\n\n"
    #     f"After careful consideration, we will not be moving forward "
    #     f"with your application at this time.\n\n"
    #     f"We wish you all the best in your job search.\n\n"
    #     f"- JMS Advisory"
    # )

    send_whatsapp(
        candidate.contact,
        f"📩 *Application Update — JMS Advisory*\n\n"
        f"Hi {candidate.name},\n\n"
        f"Thank you for your interest in:\n\n"
        f"📋 *Role:* {job_opening.designation}\n"
        f"🏢 *Company:* {job_opening.company}\n\n"
        f"After careful consideration, we regret that we will not be moving forward "
        f"with your application at this time.\n\n"
        f"We value your effort and your profile will remain on record for future openings. 💪\n\n"
        f"*JMS Advisory*\ninfo@jmsadvisory.in"
    )

    

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

    # send_whatsapp(
    #     candidate.contact,
    #     f"Hi {candidate.name},\n\n"
    #     f"Your interview for *{job_opening.designation}* at "
    #     f"*{job_opening.company}* has been scheduled.\n\n"
    #     f"📅 Date & Time: {event.start_time}\n\n"
    #     f"Please check your email for complete details.\n\n"
    #     f"- JMS Advisory"
    # )
    send_whatsapp(
        candidate.contact,
        f"📅 *Interview Scheduled — JMS Advisory*\n\n"
        f"Hi {candidate.name},\n\n"
        f"Great news! Your interview has been confirmed:\n\n"
        f"📋 *Role:* {job_opening.designation}\n"
        f"🏢 *Company:* {job_opening.company}\n"
        # f"📅 *Date & Time:* {event.start_time}\n\n"
        f"📅 *Date & Time:* {event.start_datetime.strftime('%d %B %Y at %I:%M %p')}\n\n"
        f"🔔 *Quick Tips:*\n"
        f"• Be on time and well-prepared\n"
        f"• Review the job description\n"
        f"• Keep your documents ready\n\n"
        f"Check your email for full details. Best of luck! 🌟\n\n"
        f"*JMS Advisory*\ninfo@jmsadvisory.in"
    )

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

    # send_whatsapp(
    #     candidate.contact,
    #     f"Hi {candidate.name},\n\n"
    #     f"Thank you for your time and effort throughout the hiring process "
    #     f"for *{job_opening.designation}* at *{job_opening.company}*.\n\n"
    #     f"We truly appreciate your interest.\n\n"
    #     f"- JMS Advisory"
    # )
    send_whatsapp(
        candidate.contact,
        f"🙏 *Thank You — JMS Advisory*\n\n"
        f"Hi {candidate.name},\n\n"
        f"We sincerely *thank you* for your time and enthusiasm throughout the hiring process for:\n\n"
        f"📋 *Role:* {job_opening.designation}\n"
        f"🏢 *Company:* {job_opening.company}\n\n"
        f"Your professionalism has been greatly appreciated. We'll stay in touch for future opportunities.\n\n"
        f"Wishing you continued success! 🌟\n\n"
        f"Warm regards,\n*JMS Advisory*\ninfo@jmsadvisory.in"
    )

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

    send_whatsapp(
        candidate.contact,
        f"🎙️ *Interview Invitation — JMS Advisory*\n\n"
        f"Hi {candidate.name},\n\n"
        f"You've been invited to complete an *online AI-powered interview*. 🤖\n\n"
        f"🔗 Your interview link has been sent to your registered email.\n\n"
        f"📌 *Before you begin:*\n"
        f"• Find a quiet place with good lighting\n"
        f"• Ensure a stable internet connection\n"
        f"• Keep your resume handy\n\n"
        f"{'📝 *Note:* ' + additional_notes + chr(10) + chr(10) if additional_notes else ''}"
        f"Best of luck! 💼\n\n"
        f"*JMS Advisory*\n info@jmsadvisory.in"
    )
    
    return send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[candidate.email],
        fail_silently=False,
    )

    # send_whatsapp(
    #     candidate.contact,
    #     f"Hi {candidate.name},\n\n"
    #     f"You have been invited to complete an online interview. 🎙️\n\n"
    #     f"Please use the link sent to your email to begin.\n\n"
    #     f"{'Note: ' + additional_notes + chr(10) + chr(10) if additional_notes else ''}"
    #     f"- JMS Advisory"
    # )



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
from weasyprint import HTML

def send_stage_to_client_email(request,recruiter, candidate, job_opening, cc_list=None, recipient_type="client"):

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
    import os
    import tempfile

    resume_file_path = None

    if candidate.upload_resume:
        try:
            extension = os.path.splitext(candidate.upload_resume.name)[1] or ".pdf"

            temp_resume = tempfile.NamedTemporaryFile(delete=False, suffix=extension)

            candidate.upload_resume.open("rb")
            temp_resume.write(candidate.upload_resume.read())
            candidate.upload_resume.close()

            temp_resume.close()
            resume_file_path = temp_resume.name

        except Exception as e:
            print("Resume handling failed:", str(e))
            resume_file_path = None
            
        final_pdf = merge_ai_pdf_with_resume(
            ai_pdf,
            resume_file_path
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