# -*- coding: utf-8 -*-
"""aira_code

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/109tjrKYgyYjMpHxsHtj0idCBKtPhOY0y

# Literature review assistant

The aim of this project is to create a literature review assistant

# Libraries
"""

!pip install PyPDF2

from PyPDF2 import PdfReader
import os
import glob
import pandas as pd
import re

from google.colab import drive
drive.mount('/content/drive')

!pip install pdf2image

from PIL import Image
from io import BytesIO
# import pytesseract
# Specify the path where Tesseract-OCR was installed
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import pandas as pd
import numpy as np
import cv2
import matplotlib.pyplot as plt
# from pytesseract import Output
import re
import glob
import os
import PIL.Image
from PIL import Image
from pdf2image import convert_from_path

"""
# Creating the database

We first extract the text from the PDF of our literature review. The final output of this section is a dataframe with two columns, the first one is the name od the PDF, the second one is the extracted text of the"""

def pdf_to_text(pdf_path):
    '''
    Objective:
        This functions transforms a pdf to a text where we can apply text information retrieval

    Input:
        pdf_path (str) : The path where the pdf is located, including the pdf name.

    Output:
        It returns the text of the pdf
    '''
    reader   = PdfReader( pdf_path )
    n_pages  = len( reader.pages )
    print( f'Number of pages: { n_pages }' )

    try:
        extracted_text = [ reader.pages[ i ].extract_text() for i in range( n_pages ) ]
        print( 'Text successfully extracted' )

    except:
        extracted_text = []
        print( 'Text not found' )


    combined_text = '\n'.join( extracted_text )


    return combined_text

def extract_text( combined_text , start_pattern , end_pattern):
    '''
    Objective:
        This function takes a text and extracts the patter indicated by the start_patter and end_patter inputs.

    Input:
        combined_text (str) : The text where we can extract information.

        start_pattern (str) : The starting pattern.

        end_pattern (str) : The ending pattern.
    '''
    start_match   = re.search( start_pattern, combined_text, re.IGNORECASE )
    end_match     = re.search( end_pattern, combined_text[ start_match.end(): ], re.IGNORECASE )

    end_index     = start_match.end() + end_match.start()
    article_text  = combined_text[ start_match.end(): end_index ].strip()

    article_text = article_text.split('\n')

    return article_text

folder_path = '/content/drive/MyDrive/Hackaton QLAB 24/Muestra'
data_dict = {'Filename': [], 'PDF_text': []}

# for pattern in patterns:
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)

    try:
        file_pdf = pdf_to_text(file_path)

    except:
        print(f'{filename} is not a file')
        continue

    data_dict['Filename'].append(filename)
    data_dict['PDF_text'].append(file_pdf)

final_dataframe = pd.DataFrame(data_dict)

final_dataframe



"""#Chunks and ¿tokenization?"""

#Install key packages
!pip install openai tiktoken pypdf chromadb langchain

#Call relevant libaries
from pypdf import PdfReader #stores the information for each page in the PDF document we have loaded, contained within the pages attribute, an iterable.
import requests
import pandas as pd
import numpy as np
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import chromadb
from openai import OpenAI

final_dataframe["PDF_text"][0]

tokenizer = tiktoken.get_encoding("cl100k_base")

#we must separate the text into chunks
def tokenCounter(text):
    return len(tokenizer.encode(text))

textSplitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=20,
    length_function=tokenCounter,
    separators = ["\n\n", ".", "\n", " "]
)

# Función para aplicar textSplitter a cada fila y devolver el resultado en un diccionario
def generate_chunks(row):
    chunks = textSplitter.create_documents([row["PDF_text"]], metadatas=[{"id": f"pdf{row.name + 1}"}])
    return f"pdf{row.name + 1}", chunks

# Aplicamos la función generate_chunks a cada fila del dataframe y convertimos los resultados en un diccionario
chunks_dict = dict(final_dataframe.apply(generate_chunks, axis=1).values)

chunks_dict



OPENAI_API_KEY = "" #own key

openaiEmbedding = OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name="text-embedding-3-small"
)

chromaClient = chromadb.PersistentClient()
collection = chromaClient.create_collection(
    name="aira",
    embedding_function=openaiEmbedding,
    metadata={"hnsw:space": "cosine"}
)

collection.add(
        documents=[document.page_content for document in chunks],
        metadatas=[document.metadata for document in chunks],
        ids=[f"id{i+1}" for i in range(len(chunks))]
)







"""#Funciones y prompts

#Probar
"""
