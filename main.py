import openai
from os.path import join, dirname, realpath
import json
import os
import PyPDF2
import slate3k as slate


import platform
from tempfile import TemporaryDirectory
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image

openai.api_key_path = "private/openai_api_key.txt"

# Folder target containing the pdfs
FOLDER = "samples"

# Debug mode
DEBUG = False

# Completion length
COMPLETION_LENGTH = 100

def send_to_file(f, data):
    '''
    Send data to a file `f`. Data can be a dict or a list.
    '''
    if data:
        with open(join(dirname(realpath(__file__)), f), "w") as fp:
            json.dump(data, fp, indent=4)
    else:
        fp = open(join(dirname(realpath(__file__)), f), "w")
        fp.close()

def pdf_to_text_pypdf(pdf_path):
    '''
    Extract text from pdf using PyPDF2.
    '''
    with open(pdf_path, 'rb') as f:
        pdf = PyPDF2.PdfReader(f)
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def pdf_to_text_slate(pdf_path):
    '''
    Extract text from pdf using slate.
    '''
    with open(pdf_path, 'rb') as f:
        doc = slate.PDF(f)
        text = "".join(doc)
    return text

def pdf_to_text_ocr(pdf_path):
    '''
    Extract text from pdf using OCR.
    '''


    return 

def openai_generate(text):
    '''
    Generate a response from openai using only text/string data.
    '''

    # check to see if content length is greater than 4097
    if len(text) + COMPLETION_LENGTH > 4097:
        raise Exception("Text length is too long.")

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Return in the json format with the following fields extracted from the input text:\n- date\n- client_name\n- location\n\n\nAdditionally, add a confidence score to the same payload that indicates how certain you are about the correctness of the details.\n\n\nOnly answer with a json and nothing more.\n\n\nHere is the input text: \n```\n{text}\n```",
        temperature=0.7,
        max_tokens=COMPLETION_LENGTH,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    if DEBUG:
        print(json.dumps(response, indent=4))

    return response.get("choices")[0].get("text")

def main(): 

    responses = []

    # extract text from sample folder
    for f in os.listdir(join(dirname(realpath(__file__)), FOLDER)):
        
        # skip non pdf files
        if not f.endswith(".pdf"):
            continue

        # extract text from pdf
        text = pdf_to_text_slate(join(dirname(realpath(__file__)), FOLDER, f))
        if DEBUG:
            print(text)
        
        # send the text to a file that has the same name as the pdf but 
        # with .txt extension to the same folder
        send_to_file(join(dirname(realpath(__file__)), FOLDER, "".join(f.split(".")[:-1]) + ".txt"), text)

        # use openai to generate a response
        try:
            response = openai_generate(text)
        except Exception as e:
            print(e)
            response = ""
        
        # print the response
        try:
            print(json.dumps(json.loads(response), indent=4))
        except:
            print(response)

        # add the response to the list of responses
        responses.append(response)
        
    return {
        "responses": responses
    }

if __name__ == "__main__":
    output = main()
    send_to_file("output.json", output)