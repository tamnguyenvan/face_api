# Face API Documentation
## Installation
Install dependencies by running: `pip install -r requirements.txt`. Launch server:
```
# production
STAGE=prod gunicorn --bind 0.0.0.0:5000 wsgi:app

# dev
STAGE=dev gunicorn --bind 0.0.0.0:5000 wsgi:app
```

## Settings

## Setup face recognition database
You can edit face images folder of the face recognition in config file `face_recognition.database.dir`.

## API
All inferences only accept `multipart/form-data` inputs.
|Path|Method|Description|
|---|---|---|
| /v1/verify |  POST | This function verifies an image pair is same person or different persons. Sample request, `curl -F file1=@localfilename1 file2=@localfilename2 http://foo.bar/v1/verify`.|
|/v1/recognize | POST | This function applies verification several times and find an identity in a database. Sample request, `curl -F file=@localfilename http://foo.bar/v1/recognize` |
|/v1/detect| POST | This function applies pre-processing stages of a face recognition pipeline including detection and alignment. Sample request, `curl -F file=@localfilename http://foo.bar/v1/detect`|
|/v1/change-settings| GET |Change API settings. You can change the recognition model, the detector backend, and the distance metric. Sample request, `http://foo.bar/v1/change-settings?endpoint=face-verification&model=facenet&distance-metric=cosine&save=true`. Available recognition models: `facenet`, `openface`, `deepid`, `arcface`, `dlib`. Available detector backends: `opencv`, `ssd, `dlib`, `retinaface`, 'mtcnn`. Available distance metrics: `cosine`, `euclidean`, `euclidean-l2`|