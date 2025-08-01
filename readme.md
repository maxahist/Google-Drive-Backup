# Google Drive Download Script

This script allows download exel files from Google Drive

<ins> The script docs.py </ins>
- Checks for exel files, write down file name and id into g_files.txt 
- Then download these files into 'Google_Drive_Backup {date}' folder

<ins> The script d_to_ftp </ins>
- Upload file to the server via ftp

<ins>For Windows</ins> you may run google_docs.bat to do both


For usage you need to: 
-  Have an access to the files in cloud storage from your email
- Create an application in google cloud console
- Dowload JSON token and save it in creadentials.json into main repositiry

