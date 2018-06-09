import textract
import pdftotext
import os


class DocumentParser:

    def __init__(self, filename, output=None):

        self.filename = filename
        self.path, self.extension = os.path.splitext(filename)
        self.output = output

    def read(self):

        if self.extension == '.pdf':
            with open(str(self.filename), 'rb') as document:
                pages = pdftotext.PDF(document)

            for page in pages:
                print(page)

            return pages

        else:
            print(textract.process(self.filename))