DHO2 MINUTE SHARE
Secure OTP-Based Encrypted File Transfer System
-----------------------------------------------


## PROJECT OVERVIEW

Dho2 Minute Share is a secure, time-bound file transfer platform built using Django.
A user can upload any file and receive a unique 6-digit OTP.
The OTP is valid for 2 minutes and allows authorized recipients to download the file.
Files are AES-encrypted and stored temporarily in an ephemeral environment compatible
with Render’s free hosting limitations.

No permanent files are stored on the server, ensuring data privacy and security.


## KEY FEATURES

1. Secure File Encryption

   * Uses AES-GCM for confidentiality and integrity.
   * Original files are never stored; only encrypted binaries are saved.

2. Time-Bound OTP System

   * Generates a unique 6-digit code.
   * OTP is valid for 2 minutes and non-reusable.
   * Automatically deleted upon expiry.

3. Temporary Storage 

   * Stores encrypted files in /tmp/encrypted/
   * Ensures compatibility with Render’s ephemeral storage.

4. Auto Cleanup Process

   * Deletes expired encrypted files.
   * Removes associated database entries.
   * Ensures zero long-term file retention.

5. Cancel Sharing

   * The sender can manually cancel the sharing link.
   * Removes encrypted file instantly.

6. User-Friendly Interface

   * Separate “Send File” and “Receive File” workflows.
   * Live countdown timer for code validity.
   * Professional layout and simple UI.


## TECHNOLOGIES USED

Backend Framework : Django 5.x
Frontend          : HTML, CSS
Encryption        : AES-GCM (cryptography library)
Deployment        : Render Web Service
Storage           : /tmp/encrypted directory (ephemeral)
Language          : Python 3.10.13


## SYSTEM ARCHITECTURE (Summary)

Client → Uploads File → Server Encrypts File →
Server Generates OTP →
Recipient Enters OTP → Server Verifies → Decrypts → Downloads File →
File expires after 2 minutes or manual cancellation.


## PROJECT STRUCTURE

Dho2_Minute_Share/
│   manage.py
│   settings.py
│   urls.py
│   wsgi.py
│   requirements.txt
│
├── fileapp/
│   ├── views.py
│   ├── models.py
│   ├── forms.py
│   ├── encryption.py
│   ├── cleaners.py
│   └── templates/
│       └── fileapp/
│           home.html
│           upload.html
│           success.html
│           download.html
│           cancelled.html
│
└── staticfiles/


## DEPLOYMENT CONFIGURATION (Render)

Build Command:
pip install -r requirements.txt

Start Command:
gunicorn wsgi:application

Required Environment Variables:
SECRET_KEY=<your_django_secret_key>
DEBUG=False
PYTHON_VERSION=3.10.13

Notes:

* Render free instances reset storage; /tmp is used for encrypted file storage.
* ALLOWED_HOSTS must include your Render domain.


## USER WORKFLOW

Sender:

1. Open application
2. Click “Send File”
3. Upload file
4. Receive a 6-digit OTP
5. Share OTP with receiver
6. OTP expires in 2 minutes

Receiver:

1. Open application
2. Click “Receive File”
3. Enter the OTP
4. Download decrypted file


## SECURITY HIGHLIGHTS

* AES-GCM encryption for confidentiality & integrity
* No plaintext file storage
* OTP-based access control
* Auto-expiry ensures timely cleanup
* Resistant to unauthorized access


## LICENSE & USAGE

This project is intended for educational and personal use.
Commercial usage requires permission.


## CREDITS

Developed by: Chanikya
GitHub Repository: [https://github.com/ChanikyaPonduri/Dho2_Minute_Share](https://github.com/ChanikyaPonduri/Dho2_Minute_Share)

