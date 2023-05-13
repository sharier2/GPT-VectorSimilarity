# MultiDocumentAnswering

Experiment to answer questions from arbitrary number of sources

## DISCLAIMER: INFORMATIONAL AND EXPERIMENTATION PURPOSES ONLY

Any summarizations or answers made with this code come with no warranty (see MIT license) and should not be used for financial, medical, legal, or any other critical applications.


User’s Guide
How to use the chatbot as a user of the product. To launch the server locally, run website.py, and the web server will use localhost:5000 as the default port.

Feature 1: Asking the bot a question

To ask the bot a question, simply type in your question in the big text box after navigating to localhost:5000 (or the server address), and press submit. The website will start processing the question and will find relevant sources to pull information from. Our bot determines what is close to the prompt by multiplying vectors that make up the question with every vector that makes up all the documents. This is a lengthy process but is pretty accurate. Please refer to the troubleshooting guide when there are bugs.


Feature 2: Document parsing

To add new documents to the index, go to the google drive and upload the document into the pdf folder. The document must be in pdf form The next time the website receives a request for the documents it will get converted into an index and added to the document pool.



Developer Guide
Tech Stack
This application is built in Python and uses Flask to make the web server. The front end is simple HTML and CSS, and the “database” we are using to store the files is Google Drive. The server will receive an HTML form from the user, and will take that and input it to GPT-3 along with the 20 closest vectors from the documents. The output of these queries will be shown on the homepage. GPT will summarize all of the outputs together, but all of the individual outputs are shown below that. Before the requests for the summaries are made, the indexes of the documents are checked to see if the folder is up to date. This program does keep logs of everything that is sent to GPT.
Setup
Three things must be present in order for this project to work. These are:
Prerequisite Libraries
Google drive credentials file
.env file

Prerequisite Libraries

The initial requirement for this project is to pull the github repository. Once you have the repository downloaded onto your local system, install the prerequisite libraries.

This can be done by running the command “pip install -r requirements.txt”. This will recursively install every requirement for the project.




Google Drive Credentials File
Currently, every research paper supported by this program is hosted within a Google Drive folder. This folder is accessed via a library which scans the entire folder to see if there is a new PDF file which does not have a .txt file equivalent yet. To run the program successfully, you must give it access to this google drive account. 
This can be done by putting the “credentials.json” file into the root file directory of “\GPT-VectorSimilarity”.
Follow the directions on this link to get your credential.json file. https://developers.google.com/drive/api/quickstart/python


.Env File

The program works by accessing your OpenAI API key which is stored in a .env file. This file must be created by the user and must contain the following line of code:
APIKEY=”enter-your-api-key”
Place this .env file within the root file directory of “\GPT-VectorSimilarity”.

Once these three things have been done, you will be able to proceed with the rest of the project.

In order to get the API key from OpenAI, log into OpenAI and navigate to the profile. From there find view API keys. Be careful as this program does use a lot of tokens when running a single request. Do not forget to set a payment limit on the API. As of writing there is no way to pay for infinite requests and it is a pay as you go system.

Confidence Limit

The confidence_limit setting in the worker function(used for multiprocessing in the search_index function) adjusts how confident the bot is that the material found is relevant to the user’s question. This value can be set to a float between 0 and 1. A higher confidence_limit value means the bot will be more selective with the data it returns, using only data with a score higher than the confidence_limit. A lower confidence_limit means the bot will be less selective and will return more data from outside sources.

Please keep in mind that setting the confidence_limit too high may cause the bot to miss relevant information in the research documents, while setting it too low could result in irrelevant information being returned. After testing various values, we found that a confidence_limit of 0.69 provides the best balance between relevant and irrelevant data.
