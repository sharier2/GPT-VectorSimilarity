import openai
import json
import numpy as np
import textwrap
import re
from pdf_to_txt_to_index import update_google_drive_folders, get_files_from_drive_folder, download_file_from_drive, \
    get_pdf_link, INDEX_FOLDER_ID
from time import time, sleep
import os
import io
from decouple import config
import multiprocessing as mp


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def gpt3_embedding(content, engine='text-similarity-ada-001'):
    try:
        content = content.encode(encoding='ASCII', errors='ignore').decode()
        response = openai.Embedding.create(input=content, engine=engine)
        vector = response['data'][0]['embedding']  # this is a normal list
    except Exception as error:
        print('An error occurred: {}'.format(error))


    return vector


def similarity(v1, v2):  # return dot product of two vectors
    return np.dot(v1, v2)


# confidence for relevant data is typically around 0.70, irrelevant data is typically below 0.68
def worker(data, file_name, vector, confidence_limit=0.69):
    scores = []
    for i in data:
        score = similarity(vector, i['vector'])
        if score >= confidence_limit:
            scores.append(
                {'content': i['content'], 'score': score, 'source': file_name, 'link': get_pdf_link(file_name)})
    return scores


def search_index(text, index_files, source_count=5):
    vector = gpt3_embedding(text)
    scores = []
    jobs = []
    # create a pool of workers
    pool = mp.Pool(processes=9)
    # Loop through each index file in index folder
    for index_file in index_files:
        # Download and open index file
        print("Downloading")
        download_file_from_drive(index_file['id'], "index.json")
        print("Done Downloading")
        with open('index.json', 'r') as infile:
            data = json.load(infile)

        file_name = os.path.splitext(os.path.basename(index_file['name']))[0]
        print("Scoring")
        # submit job to worker pool
        job = pool.apply_async(worker, args=(data, file_name, vector))
        jobs.append(job)
    # wait for all jobs to complete
    pool.close()
    pool.join()

    # combine all the scores
    for job in jobs:
        scores.extend(job.get())

    print("Done Scoring")
    ordered = sorted(scores, key=lambda d: d['score'], reverse=True)
    return ordered[0:source_count]


def gpt3_completion(prompt, engine='text-davinci-002', temp=0.6, top_p=1.0, tokens=2000, freq_pen=0.25, pres_pen=0.0,
                    stop=['<<END>>']):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII', errors='ignore').decode()
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            with open('gpt3_logs/%s' % filename, 'w') as outfile:
                outfile.write('PROMPT:\n\n' + prompt + '\n\n==========\n\nRESPONSE:\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)

def get_summary_of_answers(chunk, prompt_summary_path):
    print("Chunk")
    prompt = open_file(prompt_summary_path).replace('<<SUMMARY>>', chunk)
    return gpt3_completion(prompt)

def queryGPT(text):
    openai.api_key = config("APIKEY")
    # Update txt folder with new pdf's plaved in google drive
    update_google_drive_folders()
    # Get all files within the index folder
    index_files = get_files_from_drive_folder(INDEX_FOLDER_ID)
    #Get chunk size from env
    chunk_size = int(config("CHUNK_SIZE"))
    while True:
        # Get search results, searching through every index in the index folder
        results = search_index(text, index_files)
        answers = list()
        prompt_answer_path = config("PROMPT_ANS_PATH")
        # answer the same question for all returned chunks
        for result in results:

            prompt = open_file(prompt_answer_path).replace('<<PASSAGE>>', result['content']).replace('<<QUERY>>', text)
            answer = gpt3_completion(prompt)
            print('\n\n', answer)
            answers.append({'answer': answer, 'source': result['source'], 'link': result['link']})
            print("Score: " + str(result['score']))
        # summarize the answers together
        all_answers = '\n\n'.join([answer_dict['answer'] for answer_dict in answers])
        if len(answers) == 0:
            all_answers = "No research within the database is relevant to your question."
        chunks = textwrap.wrap(all_answers, chunk_size)
        final = list()
        prompt_summary_path = config("PROMPT_SUMM_PATH")
        for chunk in chunks:
            final.append(get_summary_of_answers(chunk, prompt_summary_path))
        print('\n\n=========\n\n', '\n\n'.join(final))
        return final, answers


if __name__ == '__main__':
    queryGPT()
