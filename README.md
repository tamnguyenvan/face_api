# Face API Documentation
## Installation
Install dependencies by running: `pip install -r requirements.txt`. Launch server:
```
# production
STAGE=prod python api.py

# dev
STAGE=dev python api.py
```

## API
|Path|Method|Description|
|---|---|---|
| /v1/verify |  POST | This function verifies an image pair is same person or different persons. Input must be `multipart/form-data`. For example, `curl -F file1=@localfilename1 file2=@localfilename2 http://foo.bar/v1/verify`.|
|/v1/recognize | POST | This function applies verification several times and find an identity in a database. For example, `curl -F file=@localfilename http://foo.bar/v1/recognize` |
|/v1/detect| POST | This function applies pre-processing stages of a face recognition pipeline including detection and alignment. For example, `curl -F file=@localfilename http://foo.bar/v1/detect`|