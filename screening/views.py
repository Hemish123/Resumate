from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from .models import ScreeningMetrics
from django.contrib import messages
from .forms import CategoryForm,ContactForm
# from candidate.models import Resume

from django.views.generic import ListView, CreateView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .resume_screening.extract_text import extractText
from .resume_screening.resume_screening import ResumeScreening
from .resume_screening.suggestions import GiveSuggestion
from datetime import datetime
from random import randint
from django.http import JsonResponse
from django.views.generic import FormView
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm

def about(request):
    return render(request, 'screening/about.html', context={'title':'About'})



# def resumes(request):
#     return render(request,'screening/resumes.html',context={'title':'Resumes'})

class ResumeListView(LoginRequiredMixin, TemplateView):
    template_name = 'screening/home.html'
    title = 'Home'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        category_form = CategoryForm()
        context['category_form'] = category_form
        context['category_choices'] = category_form.category_choices
        return context

    def post(self, request, *args, **kwargs):
        category_form = CategoryForm(request.POST)
        category_value = None
        if category_form.is_valid():
            field = category_form.cleaned_data['field']
            category = category_form.cleaned_data['category']
            categories = (CategoryForm.category_choices)[field]
            category_value = dict(categories).get(category)

        # if request.POST:
            # resumes = Resume.objects.filter(uploaded_by=self.request.user)
            # if category_value:
                # results, suggest_resume = ScreenResume(resumes, category_value, self.request.user)
                # redirect_url = reverse('parsing-screening') + '?category=' + category + '&results=' + ','.join(results) + '&suggest_resumes=' + ','.join(suggest_resume)
                # return redirect(redirect_url + '&next=' + reverse('parsing-home'))
                # return redirect(redirect_url)

        return render(request, self.template_name, context=self.get_context_data())

class ResumeView(LoginRequiredMixin, TemplateView):
    template_name = 'screening/resumes.html'
    title = 'Resumes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        # context['resume_list'] = Resume.objects.filter(uploaded_by=self.request.user).order_by('-updated_on')
        return context

class ResumeCreateView(LoginRequiredMixin, CreateView):
    # model = Resume
    fields = {'upload_resume'}
    template_name = 'screening/upload_resume.html'
    title = 'Upload Resumes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_form = CategoryForm()
        category_form.fields['category'].required = False
        category_form.fields['field'].required = False
        context['category_form'] = category_form
        context['category_choices'] = category_form.category_choices
        context['title'] = self.title
        return context

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def form_valid(self, form):
        if self.request.POST:
            category_form = CategoryForm(self.request.POST)
            files = self.request.FILES.getlist('upload_resume')
            message = []
            resumes = []
            # for file in files:
            #     if not Resume.objects.filter(filename=file.name, uploaded_by=self.request.user).exists():
            #         resume = Resume(upload_resume=file, uploaded_by=self.request.user, filename=file.name)
            #         resume.save()
            #         file_path = resume.upload_resume.path
            #         text = extractText(file_path)
            #         if text.strip() == "":
            #             resume.delete()
            #             form.add_error('upload_resume', (file.name + ' cannot be parsed'))
            #         else:
            #             resume.text_content = text
            #             resume.save(update_fields=['text_content'])
            #             resumes.append(file.name)
            #
            #             if len(files) <= 3:
            #                 message += [str(file.name) + ' uploaded successfully!']
            #             elif len(files) > 3:
            #                 message = ['All files uploaded successfully!']
            #     else:
            #         resumes.append(file.name)
            #         if "upload_button" in self.request.POST:
            #             form.add_error('upload_resume', (file.name + ' already exists.'))

            if form.errors:
                if self.is_ajax():
                    return JsonResponse({'errors': form.errors}, status=400)
                return self.form_invalid(form)

            if "upload_button" in self.request.POST:
                for text in message:
                    messages.success(self.request, message=text)
                return redirect(reverse('parsing-resumes'))

            elif "start_screening" in self.request.POST:
                category_form.fields['category'].required = True
                category_form.fields['field'].required = True
                category_value = None

                if category_form.is_valid():
                    field = category_form.cleaned_data['field']
                    category = category_form.cleaned_data['category']
                    categories = (CategoryForm.category_choices)[field]
                    category_value = dict(categories).get(category)

                    # resume = Resume.objects.filter(filename__in=resumes, uploaded_by=self.request.user)
                    # results, suggest_resume = ScreenResume(resume, category_value, self.request.user)
                    # redirect_url = reverse('parsing-screening') + '?category=' + category + '&results=' + ','.join(results) + '&suggest_resumes=' + ','.join(suggest_resume)
                    # return redirect(redirect_url + '&next=' + reverse('parsing-upload'))
                    # return redirect(redirect_url)
                else:
                    return self.form_invalid(form)



    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        if self.is_ajax():
            return JsonResponse({'errors': form.errors}, status=400)
        return self.render_to_response(context)


class ResumeDeleteView(LoginRequiredMixin, DeleteView):
    # model = Resume
    success_url = reverse_lazy('parsing-resumes')

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)


class ScreeningListView(LoginRequiredMixin, TemplateView):
    template_name = 'screening/screening.html'
    title = 'Screening'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        category_key = self.request.GET.get('category')
        category_value = dict(CategoryForm.category_choices).get(category_key)
        context['category'] = category_value

        results = self.request.GET.get('results', '')
        selected_resume_ids = [int(id) for id in results.split(',') if id.isdigit()]
        # selected_resumes = Resume.objects.filter(id__in=selected_resume_ids).order_by('-updated_on')
        # context['resume_list'] = selected_resumes

        suggest = self.request.GET.get('suggest_resumes', '')
        suggest_resume_ids = [int(id) for id in suggest.split(',') if id.isdigit()][:10]
        # suggested_resumes = Resume.objects.filter(id__in=suggest_resume_ids).order_by('-updated_on')
        # context['suggest_resume_list'] = suggested_resumes

        # # Add next parameter for Go Back button
        # context['next'] = self.request.GET.get('next', reverse('parsing-home'))

        return context


class AnalyticsTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'screening/analytics.html'
    title = 'Analytics'

    def get_context_data(self, **kwargs):
        total_resumes = 0
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        screening_analysis = ScreeningMetrics.objects.all()
        labels = []
        data = []
        colors = []
        for i in screening_analysis:
            total_resumes += i.total_resumes_processed
            if i.for_role in labels:
                index = labels.index(i.for_role)
                data[index] += i.total_resumes_processed
            else:
                labels.append(i.for_role)
                data.append(i.total_resumes_processed)
                r = (randint(0,255),randint(0,230),randint(50,255))
                if (r or (r+20) or (r-20)) in colors:
                    r = (randint(0, 255), randint(0, 230), randint(50, 255))
                colors.append('rgb'+str(r))
        context['resumes_total'] = total_resumes
        context['labels'] = labels
        context['data'] = data
        context['colors'] = colors
        return context

def ScreenResume(resumes, category_value, user):
    results = []
    suggest_resume = []
    count_resume = 0
    screen_time = 0
    for resume in resumes:
        text = resume.text_content
        screen_starttime = datetime.now()
        result = ResumeScreening(text)
        screen_endtime = datetime.now()
        screen_time = screen_endtime - screen_starttime
        if result['category'] == category_value:
            results.append(str(resume.id))
            count_resume += 1
        else:
            similar_roles = GiveSuggestion(category_value)
            suggest_resume += [str(resume.id) for role in similar_roles if result['category'] == role]

    suggest_resume = suggest_resume[:10]

    if results:
        today = datetime.now().date()
        screening_metrics, _ = ScreeningMetrics.objects.get_or_create(date=today,
                                                                      for_role=category_value,
                                                                      user=user)
        screening_metrics.total_resumes_processed += count_resume
        screening_metrics.total_screening_time += screen_time
        screening_metrics.save()
    return results, suggest_resume

class ContactUsView(FormView):
    template_name = 'screening/contactus.html'
    form_class = ContactForm
    success_url = '/contactus/'  # Adjust this as needed

    def form_valid(self, form):
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']

        # Send email
        send_mail(
            'New Contact Us Submission',
            f'Name: {name}\nEmail: {email}\nMessage: {message}',
            settings.DEFAULT_FROM_EMAIL,
            ['resumate1nfo1@gmail.com'],
            fail_silently=False,
        )

        return JsonResponse({'success': True})

    def form_invalid(self, form):
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)