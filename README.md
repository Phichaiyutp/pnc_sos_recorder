
## Setup Instructions

### Step 1: Create Required Folders

Create the following folders in the project directory:
-media
-utils
    credentials.json
-nginx
    nginx.conf

### Step 2: Run Docker Compose
Run the following command to start the services:
    docker-compose up -d

### Step 3: Attach to the Backend Container
Attach to the backend container to perform additional setup:
    docker attach [container id backend]
    Call API end-point get_attachments
    Copy url from container to browser and accept 
    Copy code from browser to keybord input
    exit attach
