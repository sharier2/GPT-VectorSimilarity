import openai
import json
import textwrap
import os
import io
from decouple import config


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


openai.api_key = config("APIKEY")


def gpt3_embedding(content, engine='text-similarity-ada-001'):
    response = openai.Embedding.create(input=content,engine=engine)
    vector = response['data'][0]['embedding']  # this is a normal list
    return vector

def build_index(research_file = 'research.txt'):
    alltext = open_file(research_file)
    chunks = textwrap.wrap(alltext, 4000)
    result = list()
    for chunk in chunks:
        embedding = gpt3_embedding(chunk.encode(encoding='ASCII', errors='ignore').decode())
        info = {'content': chunk, 'vector': embedding}
        print(info, '\n\n\n')
        result.append(info)
    with open('index.json', 'w') as outfile:
        json.dump(result, outfile, indent=2)

if __name__ == '__main__':
    build_index()

        #test