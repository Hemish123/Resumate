
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
import os
from io import BytesIO

# Set up logging
logging.basicConfig(filename='app.log', level=logging.ERROR)



def doc_to_txt(doc_file):
    # Run antiword command to convert .doc to plain text
    result = subprocess.run(['antiword', doc_file], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as fh:
        # iterate over all pages of PDF document
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            # creating a resoure manager
            resource_manager = PDFResourceManager()

            # create a file handle
            fake_file_handle = io.StringIO()

            # creating a text converter object
            converter = TextConverter(
                resource_manager,
                fake_file_handle,
                # codec='utf-8',
                laparams=LAParams()
            )

            # creating a page interpreter
            page_interpreter = PDFPageInterpreter(
                resource_manager,
                converter
            )

            # process current page
            page_interpreter.process_page(page)

            # extract text
            text = fake_file_handle.getvalue()
            yield text

            # close open handles
            converter.close()
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
    # font_info = []

    # Iterate through all block-level elements in order
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            content.append(block.text)
        elif isinstance(block, Table):
            for row in block.rows:
                row_data = []
                for cell in row.cells:
                    row_data.append(cell.text)
                content.append("\t".join(row_data))
        else:
            continue
    content = '\n'.join(content)
    return content



def extractText(file_path):
    try:
        text = " "
        if ".docx" in file_path:
            text = extract_text_from_doc(file_path)
        elif ".doc" in file_path:
            text = doc_to_txt(file_path)
        elif ".pdf" in file_path:
            # calling above function and extracting text
            for page in extract_text_from_pdf(file_path):
                text += ' ' + page
        # print(text)
        text = text.replace('\t', ' ')
        text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-:;<=>?[]^_`{|}~"""), ' ', text)  # remove punctuations
        # text = re.sub(r'[^x00-\x7f]',r' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = '\n'.join(text.split('\n\n'))
        return text
    except Exception as e:
        print("Not a valid file", e)
        logging.error("An error occurred:", exc_info=True)
        return " "


