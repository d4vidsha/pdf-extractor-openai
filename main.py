import json
import os
from os.path import join, dirname, realpath
from tempfile import TemporaryDirectory
import re

import openai
import PyPDF2
import slate3k as slate
from pdf2image import convert_from_path
import pytesseract

# OpenAI API key path
OPENAI_API_KEY_PATH = "private/openai_api_key.txt"

# Folder target containing the pdfs
FOLDER = "samples"

# Folder where all the output files will be stored
OUTPUT_FOLDER = "tests"

# Debug mode
DEBUG = True

# Do one PDF only
DO_ONE = True

# Completion length
COMPLETION_LENGTH = 300

# Summarization length
SUMMARIZATION_LENGTH = 300

# Maximum content length
MAX_CONTENT_LENGTH = 4097

# Chunk size
CHUNK_SIZE = MAX_CONTENT_LENGTH - SUMMARIZATION_LENGTH

# Fields to extract
FIELDS = [
    "date",
    "client_name",
    "location"
]

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
    with TemporaryDirectory() as path:
        images_from_path = convert_from_path(pdf_path, output_folder=path, fmt="jpg")
        text = ""
        for image in images_from_path:
            text += pytesseract.image_to_string(image)
    return text

def chunkify(text, chunk_size=CHUNK_SIZE):
    '''
    Split a text into chunks of size `chunk_size`. The split is done on a new line.
    '''
    chunks = []
    while len(text) > chunk_size:
        index = text[:chunk_size].rfind("\n")
        chunks.append(text[:index])
        text = text[index:]
    chunks.append(text)
    return chunks

def openai_summarize_helper(text):
    '''
    Summarize a text using openai.
    '''
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Summarize the following text ensuring that details are still specific:\n```\n{text}\n```",
        temperature=0.7,
        max_tokens=SUMMARIZATION_LENGTH,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    if response.get("choices")[0].get("finish_reason") == "length":
        print("Summarization was cut short. Consider increasing the `SUMMARIZATION_LENGTH` variable. Continuing...")

    if DEBUG:
        print(json.dumps(response, indent=4))

    return response.get("choices")[0].get("text")

def openai_summarize(text):
    '''
    Summarize a given text using openai. If the text is too long, split it
    into smaller chunks and summarize each chunk.
    '''
    if len(text) > CHUNK_SIZE:
        
        # split the text into chunks
        chunks = chunkify(text)
        
        # summarize each chunk
        summaries = [openai_summarize_helper(chunk) for chunk in chunks]
        
        # return the summarized text
        return "\n".join(summaries)
    else:
        return openai_summarize_helper(text)

def format_fields(fields):
    '''
    Format the fields to be used in the prompt.
    The format is:
    - field1
    - field2
    - field3
    '''
    return "\n".join([f"- {field}" for field in fields])

def openai_generate(text, filename):
    '''
    Generate a response from openai using only text/string data.
    '''
    # summarize in order to reduce the size of the text
    while len(text) + COMPLETION_LENGTH > MAX_CONTENT_LENGTH:
        print("Summarizing text...")
        text = openai_summarize(text)

    # make the request
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Return in json format with the following fields extracted from the input text:\n{format_fields(FIELDS)}\n\n\nAdditionally, add a confidence score between 0 and 1 to the same payload that indicates how certain you are about the correctness of the details.\n\n\nIf you couldn't find certain details, make them `null`.\n\n\nNormalise the date to YYYY-mm-dd.\n\n\nNormalise the location to \"number street, city, state, postcode\"\n\n\nOnly reply with json and nothing more.\n\n\nHere is the input text: \n```\n{text}\n```\n\n\nHere is also the input text's filename: \n```\n{filename}\n```\n",
        temperature=0.7,
        max_tokens=COMPLETION_LENGTH,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    if response.get("choices")[0].get("finish_reason") == "length":
        print("Completion was cut short. Consider increasing the `COMPLETION_LENGTH` variable. Continuing...")

    if DEBUG:
        print(json.dumps(response, indent=4))

    return response.get("choices")[0].get("text")

def extract(f):
    '''
    Extract text from a pdf file and send it to openai to generate a response.
    '''
    # extract text from pdf
    text = pdf_to_text_ocr(join(dirname(realpath(__file__)), FOLDER, f))
    if DEBUG:
        print(text)
    
    # send the text to a file that has the same name as the pdf but 
    # with .txt extension to the same folder
    send_to_file(join(dirname(realpath(__file__)), FOLDER, "".join(f.split(".")[:-1]) + ".txt"), text)

    # use openai to generate a response
    try:
        response = openai_generate(text, f)
    except Exception as e:
        print(e)
        response = ""
    
    # print the response
    if DEBUG:
        try:
            print(json.dumps(json.loads(response), indent=4))
        except:
            print(response)

    # match the json from the string of text,
    # the json is surrounded by curly braces
    try:
        # remove new lines so that the regex works
        response = response.replace("\n", "")

        response = re.search(r"{.*}", response).group(0)
    except:
        pass

    return response

def main(): 

    openai.api_key_path = OPENAI_API_KEY_PATH

    responses = []

    # extract text from sample folder
    for f in os.listdir(join(dirname(realpath(__file__)), FOLDER)):
        
        # skip non pdf files
        if not f.endswith(".pdf"):
            continue

        # extract text and generate a response
        response = extract(f)

        # add the response to the list of responses
        try:
            responses.append(json.loads(response))
        except:
            responses.append(response)

        if DO_ONE:
            break
        
    return {
        "responses": responses
    }

if __name__ == "__main__":
    output = main()
    
    # send the output to a file called output#.json. If the file already 
    # exists, create a new file with a number appended to the end
    send_to_file(f"{OUTPUT_FOLDER}/output" + str(len(os.listdir(join(dirname(realpath(__file__)), OUTPUT_FOLDER))) + 1) + ".json", output)