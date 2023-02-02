# pdf-extractor-openai

This is a simple Python script to extract certain information from PDFs using OpenAI's GPT-3 API.

## Prerequisites

- Python
- OpenAI API key
- PDFs to extract information from

## Usage

1. Install the requirements using `pip install -r requirements.txt`.
2. You will also need to create a file called `openai_api_key.txt` and add your OpenAI API key to it. The file should look like this:

    ```txt
    sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```

3. It should then be added to the `private` folder.
4. Add any PDFs to the `samples` folder.
5. Run the script using `python main.py` and it will extract the information from the PDFs and save it to the `tests` folder.

There are additional options you can use with the script by editing the `main.py` file. Check the comments in the file for more information.
