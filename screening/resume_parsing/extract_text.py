from pdfminer.converter import TextConverter, HTMLConverter, PDFPageAggregator
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar
from pdfminer.pdfpage import PDFPage
import io
import subprocess
import logging
import re
from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.table import Table, _Cell
import docx
# from sklearn.metrics.pairwise import cosine_similarity
# import spacy
import os
from io import BytesIO

# Set up logging
logging.basicConfig(filename='app.log', level=logging.ERROR)


def convert_to_pdf(pdf_path):
    output_dir = os.path.dirname(pdf_path)
    filename = os.path.basename(pdf_path)
    output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.pdf')      # filename.pdf
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', output_dir, pdf_path], check=True)
    with open(output_path, 'rb') as f:
        doc_content = f.read()
    os.remove(output_path)
    return BytesIO(doc_content)


def extract_text_from_document(content):
    # iterate over all pages of PDF document
    for page in PDFPage.get_pages(content, caching=True, check_extractable=True):
        # creating a resoure manager
        resource_manager = PDFResourceManager()

        device = PDFPageAggregator(resource_manager, laparams=LAParams())
        # creating a page interpreter
        page_interpreter = PDFPageInterpreter(
            resource_manager,
            device
        )

        # process current page
        page_interpreter.process_page(page)
        layout = device.get_result()        # get layout of page
        fake_file_handle,font_info  = get_font_info(layout)     # font info like bold, fontsize

        text = fake_file_handle.getvalue()
        if '\uf0b7' in text:
            text = text.replace('\uf0b7', '•')

        yield text, font_info

        fake_file_handle.close()


def iter_block_items(parent):
    """
    Yield each paragraph and table child within *parent*, in document order.
    Each returned value is an instance of either Table or Paragraph.
    """
    if isinstance(parent, docx.document.Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._element
    else:
        raise ValueError("Parent must be a docx.Document or docx.table._Cell object")

    for child in parent_elm.iterchildren():
        if child.tag == qn('w:p'):
            yield Paragraph(child, parent)
        elif child.tag == qn('w:tbl'):
            yield Table(child, parent)

def extract_text_from_doc(doc_path):
    doc = Document(doc_path)

    # Initialize a list to store the extracted content
    content = []
    font_info = []

    # Iterate through all block-level elements in order
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            for run in block.runs:
                run_info = {
                    "text": run.text,
                    "font_size": int(run.font.size.pt) if run.font.size else None,
                    "bold": run.bold,
                }
                font_info.append(run_info)
            content.append(block.text)
        elif isinstance(block, Table):
            for row in block.rows:
                row_data = []
                for cell in row.cells:
                    cell_texts = []
                    for cell_paragraph in cell.paragraphs:
                        for run in cell_paragraph.runs:
                            run_info = {
                                "text": run.text,
                                "font_size": int(run.font.size.pt) if run.font.size else None,
                                "bold": run.bold,
                            }
                            font_info.append(run_info)
                            # cell_texts.append(run_info)
                    row_data.append(cell.text)
                content.append("\t".join(row_data))
        else:
            continue
    content = '\n'.join(content)
    return content, font_info


def get_font_info(layout):
    font_info = []
    # create a file handle
    fake_file_handle = io.StringIO()
    for element in layout:
        if isinstance(element, LTTextBox):
            for text_line in element:
                if isinstance(text_line, LTTextLine):
                    line_text = ''
                    is_bold = False
                    fontsize = 0

                    for character in text_line:
                        if isinstance(character, LTChar):
                            fontname = character.fontname.lower()
                            fontsize = int(character.size)
                            if 'bold' in fontname or 'bd' in fontname:
                                is_bold = True

                            line_text += character.get_text()

                    fake_file_handle.write(text_line.get_text())
                    if line_text != " " :
                        font_info.append({'text':line_text, 'fontsize':fontsize , 'is_bold':is_bold})

    return fake_file_handle, font_info

def extractText(file_path):
    try:
        text = " "
        fonts_info = []
        text_n = ""
        if ".docx" in file_path:
            text, fonts_info = extract_text_from_doc(file_path)
        elif ".doc" in file_path:
            content = convert_to_pdf(file_path)

            for page, font_info in extract_text_from_document(content):
                text += ' ' + page
                fonts_info += font_info
        elif ".pdf" in file_path:
            with open(file_path, 'rb') as fh:
                content = BytesIO(fh.read())
            # calling above function and extracting text
            for page, font_info in extract_text_from_document(content):
                text += ' ' + page
                fonts_info += font_info

        text = text.replace('\t', ' ')
        text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-:;<=>?[]^_`{|}~"""), ' ', text)  # remove punctuations
        # text = re.sub(r'[^x00-\x7f]',r' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = '\n'.join(text.split('\n\n'))

        return text#, fonts_info

    except Exception as e:
        print("Not a valid file", e)
        logging.error("An error occurred:", exc_info=True)
        return " "

# text, font_info = extractText("/home/nikita/projects/JMS_ATS/screening/resume_parsing/resume/Nikita_Kapadiya.pdf")
# print('text : ', text)
# print('font info : ', font_info)


# nlp = spacy.load('en_core_web_lg')
# cosine_similarity = lambda vec1, vec2 : 1 - spatial.distance.cosine(vec1,vec2)
# computed_similarities = []
# for s in nlp.vocab.vectors:
#     _ = nlp.vocab[s]
# skill = nlp('Expertise').vector
# skills = nlp('Skills').vector
#
# similarity_score = cosine_similarity([skill,skills])
# print(similarity_score)


