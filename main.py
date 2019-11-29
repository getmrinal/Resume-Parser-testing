from fastapi import FastAPI, File, Form, UploadFile
import spacy
import os
from pydantic import BaseModel
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import requests

def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/nlp/")
async def create_item(url: str):
    r = requests.get(url, stream = True) 
    with open("python.pdf","wb") as pdf:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                pdf.write(chunk) 
    resume_text = convert_pdf_to_txt('python.pdf')
    output_dir = 'results1'
    results ={}
    nlp = spacy.load(output_dir)
    doc_to_test=nlp(resume_text)
    d={}
    for ent in doc_to_test.ents:
        d[ent.label_]=[]
    for ent in doc_to_test.ents:
        d[ent.label_].append(ent.text)
    for i in set(d.keys()):
        results[i] = d[i]
    return results
