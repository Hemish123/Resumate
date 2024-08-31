import spacy, re
from spacy.matcher import Matcher
from django.apps import apps


def parse_data(text):
    nlp = apps.get_app_config('candidate').nlp
    nlp_text = nlp(text)
    parsed_data = {'name': None,
    'email': None,
    'designation': None,
    'location': None,
    'contact': None,
    'total_experience': None}

    for ent in nlp_text.ents:
        print(ent.text, ' -----> ', ent.label_)
        if ent.label_ == 'Name' and not parsed_data.get('name'):
            parsed_data['name'] = ent.text
        elif ent.label_ == 'Designation' and not parsed_data.get('designation'):
            parsed_data['designation'] = ent.text
        elif ent.label_ == 'Location' and not parsed_data.get('location'):
            parsed_data['location'] = ent.text
        elif ent.label_ == 'Years of Experience' and not parsed_data.get('total_experience'):
            parsed_data['total_experience'] = ent.text

    # regex for phone number
    phone = re.findall(re.compile(
        r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'),
        text)

    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            parsed_data['contact'] = '+' + number
        else:
            parsed_data['contact'] = number
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", text)
    parsed_data['email'] = email[0].split()[0].strip(';')
    print('parsed', parsed_data)
    return parsed_data



