# pnc_voice_record

Create folder 
-media
-utils
    credentials.json
-nginx
    nginx.conf

Step
    Run Docker compose up -d
    Run Docker attach ["container id backend"]
    Call API end-point get_attachments
    Copy url from container to browser and accept 
    Copy code from browser to keybord input
    exit attach

.
├── README.md
├── credentials.json
├── docker-compose.yml
├── sos_voice_record
│   ├── backend
│   │   ├── Dockerfile
│   │   ├── __pycache__
│   │   │   ├── app.cpython-310.pyc
│   │   │   ├── attachment_handler.cpython-310.pyc
│   │   │   ├── models.cpython-310.pyc
│   │   │   └── voice_log.cpython-310.pyc
│   │   ├── attachment_handler.py
│   │   ├── main.py
│   │   ├── media
│   │   ├── models.py
│   │   ├── requirements.txt
│   │   ├── utils
│   │   └── voice_log.py
│   └── nginx
│       └── nginx.conf
└── token.json

# pnc_sos_recorder
