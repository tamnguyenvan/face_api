import numpy as np
from flask import Flask, request
from deepface import DeepFace

from configs import cfg
from face_api.logger import logger
from face_api.utils import initialize_env
from face_api.utils import FileManager


initialize_env()

app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>Greetings, this is Face API</h1>'


@app.route('/v1/verify', methods=['POST'])
def verify():
    if request.files:
        file1 = request.files['file1']
        file2 = request.files['file2']

        result = DeepFace.verify(FileManager.get(file1), FileManager.get(file2))
        FileManager.clean(file1)
        FileManager.clean(file1)
        if result:
            return {
                'status': 'ok',
                'data': result,
                'message': 'ok'
            }

        return {
            'status': 'error',
            'data': [],
            'message': 'Could not verify the given faces'
        }

    return {
        'status': 'error',
        'data': [],
        'message': 'Not found attached files'
    }


@app.route('/v1/recognize', methods=['POST'])
def recognize():
    if request.files:
        file = request.files['file']
        file_path = FileManager.get(file)
        facerec_cfg = cfg.face_recognition
        result = DeepFace.find(
            img_path=file_path,
            db_path=facerec_cfg.database.dir,
            model_name=facerec_cfg.model_name)
        FileManager.clean(file)

        values = result.values
        if len(values):
            results = {
                'status': 'ok',
                'data': [],
                'message': 'ok'
            }
            for filename, score in values:
                results['data'].append({
                    'matched_filename': filename,
                    'score': score,
                    'score_type': 'cosine'
                })
            return results

        return {
            'status': 'error',
            'data': [],
            'message': 'could not recognize the given face'
        }

    return {
        'status': 'error',
        'data': [],
        'message': 'not found attached files'
    }


@app.route('/v1/analyze', methods=['POST'])
def analysis():
    result = DeepFace.analyze('assets/face1.jpg')
    DeepFace.verify()


@app.route('/v1/detect', methods=['POST'])
def detect():
    if request.files:
        file = request.files['file']
        file_path = FileManager.get(file)
        result = DeepFace.detectFace(
            file_path,
            detector_backend=cfg.face_detection.model_name)
        FileManager.clean(file)

        if isinstance(result, np.ndarray) and len(result):
            results = {
                'status': 'ok',
                'data': result.tolist()
            }
            return results

        return {
            'status': 'error',
            'data': [],
            'message': 'could not detect the given face'
        }

    return {
        'status': 'error',
        'data': [],
        'message': 'not found attached files'
    }


@app.route('/v1/stream', methods=['POST'])
def stream():
    result = DeepFace.stream(cfg.realtime_stream.database.dir, source='')
    return 'ok'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)