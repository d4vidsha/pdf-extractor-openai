# pdf-extractor-openai

This is a simple Python script to extract certain information from PDFs using OpenAI's GPT-3 API.

If you would like to use this script, you will need to create an OpenAI account and get an API key. You can do this [here](https://beta.openai.com/).

## Usage

To use this script, you will need to install the requirements using `pip install -r requirements.txt`.

You will also need to create a file called `openai_api_key.txt` and add your OpenAI API key to it. The file should look like this:

```txt
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

It should then be added to the `private` folder.

Then add the PDFs you want to extract information from to the `samples` folder.

Once you have done this, you can run the script using `python main.py` and it will extract the information from the PDFs and save it to the `tests` folder.

There are additional options you can use with the script by editing the `main.py` file. Check the comments in the file for more information.
