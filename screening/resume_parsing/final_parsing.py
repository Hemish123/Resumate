import spacy, re
from spacy.matcher import Matcher
from django.apps import apps


def parseData(text):
    nlp = apps.get_app_config('candidate').nlp
    nlp_text = nlp(text)
    parsedData = {}

    for ent in nlp_text.ents :
        print(ent.text, ' -----> ', ent.label_)
        if ent.label_ == 'Name' and not parsedData.name:
            parsedData.name = ent.text
        elif ent.label_ == 'Designation' and not parsedData.designation:
            parsedData.designation = ent.text
        elif ent.label_ == 'Location' and not parsedData.location:
            parsedData.location = ent.text
        elif ent.label_ == 'Years of Experience' and not parsedData.total_experience:
            parsedData.total_experience = ent.text

    # regex for phone number
    phone = re.findall(re.compile(
        r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'),
                       text)

    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            parsedData.contact = '+' + number
        else:
            parsedData.contact = number
    parsedData.email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", text)
    return parsedData



