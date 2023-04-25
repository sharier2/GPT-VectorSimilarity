import os
import io
import shutil
from build_index import build_index
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import fitz # PyMuPDF

# ID of folder containing pdf's
PDF_FOLDER_ID = '1rBMK7jStTpsJDNLIJaznlJH3cMB218h-'

# ID of folder for txt's
TXT_FOLDER_ID = '1rNZrv06u_kg9zdoa6D-i82zFfk1QE1tB'

# ID of folder for indexes
INDEX_FOLDER_ID = '1Jsn9j_Sp_nvpiY1ZiACpDf_nAQkI98sQ'

# Service account credentials
CREDS = service_account.Credentials.from_service_account_file('credentials.json')

# Connect to the Google Drive API
SERVICE = build('drive', 'v3', credentials=CREDS)


def get_pdf_link(file_name):
    try:
        file_name  = file_name + ".pdf"
        # Query the PDF folder to retrieve the PDF files
        query = f"'{PDF_FOLDER_ID}' in parents and trashed = false and mimeType = 'application/pdf' and name = '{file_name}'"
        response = SERVICE.files().list(q=query, fields='files(id, webContentLink)').execute()
        pdf_files = response.get('files', [])
    except HttpError as error:
        print(f'An error occurred while retrieving the PDF files: {error}')

    if len(pdf_files) == 0:
        # PDF file not found
        return None
    elif len(pdf_files) > 1:
        # More than one PDF file found with the same name
        print(f'Multiple PDF files found with the name "{file_name}". Returning the first one.')

    # Return the web content link of the first PDF file found
    return pdf_files[0]['webContentLink']


def pdf_to_txt(pdf_path, txt_path):
    with fitz.open(pdf_path) as pdf:
        text = ""
        for page in pdf:
            text += page.get_text()
    with open(txt_path, "w", encoding="utf-8") as txt:
        txt.write(text)
    return txt_path

def pdf_exists_as_txt(pdf_name, txt_files):
    for txt_file in txt_files:
        txt_file_name_without_ext = os.path.splitext(os.path.basename(txt_file['name']))[0]
        if pdf_name == os.path.splitext(os.path.basename(txt_file['name']))[0]:
            return True

    return False

def upload_file_to_drive_folder(folder_id, file_path, actual_file_name, ext):
    try:
        # Define file metadata
        file_name = os.path.basename(file_path)
        file_metadata = {'name': actual_file_name + ext, 'parents': [folder_id]}

        # Upload file to the folder
        media = MediaFileUpload(file_path, resumable=True)
        file = SERVICE.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f'File ID: {file["id"]} uploaded to folder ID: {folder_id}')
    except HttpError as error:
        print(f'An error occurred: {error}')

def download_file_from_drive(file_id, file_path):
    # Download the PDF file contents
    request = SERVICE.files().get_media(fileId=file_id)
    file_contents = io.BytesIO(request.execute())

    # Write the PDF file contents to a file
    with open('./{}'.format("./" + file_path), 'wb') as f:
        shutil.copyfileobj(file_contents, f)

def get_files_from_drive_folder(folder_id):
    # Define the query to search for files in the folder
    query = "'{}' in parents".format(folder_id)

    # Execute the query
    results = SERVICE.files().list(q=query, fields="nextPageToken, files(id, name, mimeType)").execute()
    return results.get('files', [])


def update_google_drive_folders():
    # Get all files within the pdf folder
    pdf_files = get_files_from_drive_folder(PDF_FOLDER_ID)

    # Get all files within the txt folder
    txt_files = get_files_from_drive_folder(TXT_FOLDER_ID)

    if not pdf_files:
        print('No files found in the specified folder.')
    else:
        # Convert new files to txt then index
        for pdf_file in pdf_files:
            try:
                file_id = pdf_file['id']
                file_name = pdf_file['name']
                file_name_without_ext = os.path.splitext(os.path.basename(file_name))[0]
                file_mime_type = pdf_file.get('mimeType', '')

                # Check if the file is a PDF and doesnt already exitst as a txt
                if file_mime_type == 'application/pdf' and not pdf_exists_as_txt(file_name_without_ext, txt_files):

                    print('Converting \"' + file_name_without_ext + '\" to txt...')

                    download_file_from_drive(file_id, "research.pdf")

                    pdf_to_txt("research.pdf", "research.txt")

                    # Upload txt file to google drive folder
                    upload_file_to_drive_folder(TXT_FOLDER_ID, "research.txt", file_name_without_ext, '.txt')

                    print('Converted file: {} to txt'.format(file_name))

                    print('Converting \"' + file_name_without_ext + '\" to index...')

                    build_index('research.txt')

                    # Upload index to google drive folder
                    upload_file_to_drive_folder(INDEX_FOLDER_ID, "index.json", file_name_without_ext, '.json')

                    print('Converted file: {} to index'.format(file_name))

            except HttpError as error:
                print('An error occurred: {}'.format(error))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    update_google_drive_folders()


