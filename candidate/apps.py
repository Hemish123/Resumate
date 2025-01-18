from django.apps import AppConfig
import spacy, os
from django.conf import settings

class CandidateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'candidate'

    def ready(self):
        # Load the model when the application is ready

        # Path to your model after extracting
        if settings.DEBUG :
            path = os.path.join(settings.BASE_DIR, 'candidate/resume_parsing/model-best')
        else:
            path = os.path.join(os.getcwd(), "model-best", "model-best")
        # path = os.path.join(settings.BASE_DIR, 'candidate/resume_parsing/model-best')

        self.nlp = spacy.load(path)
