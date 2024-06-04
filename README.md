
## Setup Instructions

### Step 1: Create Required Folders

Create the following folders in the project directory:

- `media`
- `utils`
  - `credentials.json`
- `nginx`
  - `nginx.conf`

### Step 2: Run Docker Compose

    Run the following command to start the services:

    ```shell
    docker-compose up -d
    ```

### Step 3: Attach to the Backend Container
    ```shell
    Attach to the backend container to perform additional setup:
        * docker attach [container id backend]
        * Call API end-point get_attachments
        * Copy url from container to browser and accept 
        * Copy code from browser to keybord input
        * Exit attach
    ```


## Project Structure
    ```shell
    .
    ├── README.md
    ├── docker-compose.yml
    ├── media
    ├── sos_voice_record
    │   ├── backend
    │   │   ├── Dockerfile
    │   │   ├── attachment_handler.py
    │   │   ├── main.py
    │   │   ├── media
    │   │   ├── models.py
    │   │   ├── requirements.txt
    │   │   ├── utils
    │   │   └── voice_log.py
    │   └── nginx
    │       └── nginx.conf
    └── utils
        ├── credentials.json
        └── token.json
    ```

## API End-point
    ```
    GET /voice_log/1186
    Body:
    ```

    ```json
    {
        "ok": true,
        "payload": {
            "host_path": "/app/media/sos_voice_record/511/18fe2c7b30c91556_20240604_1724_511.wav",
            "id": 3,
            "timestamp": "2024-06-04T17:24:00",
            "recorded": 100,
            "sos_id": 1186,
            "filename": "18fe2c7b30c91556_20240604_1724_511.wav",
            "static_path": "https://city.planetcloud.cloud/citybackend/planetcomm/voicerecord/media/wav/sos_voice_record/511/18fe2c7b30c91556_20240604_1724_511.wav",
            "message_id": "18fe2c7b30c91556",
            "caller": 511,
            "call_timestamp": "2024-06-04T17:24:41"
        }
    }
    ```
    ```
    GET /voice_log/
    Body:
    ```

    ```json
    {
        "ok": true,
        "payloads": [
            {
                "host_path": "/app/media/sos_voice_record/511/18fe2c7b30c91556_20240604_1724_511.wav",
                "id": 3,
                "timestamp": "2024-06-04T17:24:00",
                "recorded": 100,
                "sos_id": 1186,
                "filename": "18fe2c7b30c91556_20240604_1724_511.wav",
                "static_path": "https://city.planetcloud.cloud/citybackend/planetcomm/voicerecord/media/wav/sos_voice_record/511/18fe2c7b30c91556_20240604_1724_511.wav",
                "message_id": "18fe2c7b30c91556",
                "caller": 511,
                "call_timestamp": "2024-06-04T17:24:41"
            }
        ]
    }
    ```