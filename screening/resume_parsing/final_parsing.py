from extract_text import extractText
import spacy
from spacy.matcher import Matcher

# load pre-trained model
nlp = spacy.load('model-best')

# initialize matcher with a vocab

file_path = 'resume/Intelliveer -ChandraKantPaliwal[9y_0m].pdf'
text = extractText(file_path)
text.strip()
text = " ".join(text.split())

nlp_text = nlp(text)


for ent in nlp_text.ents :
    print(ent.text, ' -----> ', ent.label_)



#print("extraxted text:", extract_name(text)[0], "person:", extract_name(text)[1])
# regex for phone number
# x = re.findall(r"([+]?\d{2}.?\s?)?(\d{10})", txt)