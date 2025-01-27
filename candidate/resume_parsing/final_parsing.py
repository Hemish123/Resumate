import spacy, re, json
from django.apps import apps
from spacy.lang.en import stop_words


def parse_data(text):
    nlp = apps.get_app_config('candidate').nlp
    nlp_text = nlp(text)
    stop_words_set = stop_words.STOP_WORDS

    parsed_data = {'name': None,
    'email': None,
    'designation': None,
    'location': None,
    'education': None,
    'contact': None,
    'total_experience': None}
    with open("candidate/resume_parsing/education.json") as f:
        education = json.load(f)
        education = [e.lower() for e in education]

    for tex in text.split():
        if tex.lower() in education and tex not in stop_words_set:
            parsed_data['education'] = tex
            break

    for ent in nlp_text.ents:
        if ent.label_ == 'Name' and not parsed_data.get('name'):
            parsed_data['name'] = ent.text
        elif ent.label_ == 'Designation' and not parsed_data.get('designation'):
            parsed_data['designation'] = ent.text
        elif ent.label_ == 'Location' and not parsed_data.get('location'):
            parsed_data['location'] = ent.text
        elif ent.label_ == 'Years of Experience' and not parsed_data.get('total_experience'):
            if "year" in ent.text.lower():
                match = re.search(r'\d+', ent.text)
                if match:
                    parsed_data['total_experience'] = int(match.group())
        elif ent.label_ == 'Degree' and not parsed_data.get('education'):
            parsed_data['education'] = ent.text

    # regex for phone number
    phone = re.findall(re.compile(
        r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'),
        text)

    if phone:
        number = ''.join(phone[0])

        for n in phone:
            nm = ''.join(n)
            if len(nm) >= 10:
                number = nm
                break
        # number = ''.join(phone[0])

        if len(number) > 10:
            parsed_data['contact'] = '+' + number
        else:
            parsed_data['contact'] = number
    email = re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", text)
    if len(email) :
        parsed_data['email'] = email[0].split()[0].strip(';')
    return parsed_data



