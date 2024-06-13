from extract_text import extractText
import os

# file_path = "KaziSharik.doc"
def convertText(file_path):
    text = extractText(file_path)
    # text = " ".join(text.split())
    file_path = file_path.replace("/resumes/", "/text/")
    if (".pdf" or ".docx") in file_path:
        if ".pdf" in file_path:
            write_file = file_path.replace(".pdf", ".txt")
        elif ".docx" in  file_path:
            write_file = file_path.replace(".docx", ".txt")

        with open(write_file, 'w', encoding="utf-8") as f:
            f.write(text)

    elif ".doc" in  file_path:
        txt_file = file_path.replace(".doc", ".txt")
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(text.stdout.decode('utf-8'))

    else:
        pass
