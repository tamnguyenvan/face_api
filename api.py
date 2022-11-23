import numpy as np
from flask import Flask, request
from easydict import EasyDict
from deepface import DeepFace

from configs import cfg, translate
from face_api.utils import initialize_env, File, str2bool


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

        facever_cfg = cfg.to_easydict().face_verification

        file1 = File(file1)
        file2 = File(file2)
        result = DeepFace.verify(
            img1_path=file1.name,
            img2_path=file2.name,
            model_name=translate(cfg, facever_cfg.model),
            distance_metric=translate(cfg, facever_cfg.distance_metric),
            detector_backend=translate(cfg, facever_cfg.detector_backend))
        file1.clean()
        file2.clean()
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
        file = File(file)
        facerec_cfg = cfg.to_easydict().face_recognition
        result = DeepFace.find(
            img_path=file.name,
            db_path=facerec_cfg.database.dir,
            model_name=translate(cfg, facerec_cfg.model),
            distance_metric=translate(cfg, facerec_cfg.distance_metric),
            detector_backend=translate(cfg, facerec_cfg.detector_backend))
        file.clean()

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
        file = File(file)
        facedet_cfg = cfg.to_easydict().face_detection
        backend = facedet_cfg.detector_backend
        backend = backend + '_det' if backend == 'dlib' else backend
        result = DeepFace.detectFace(
            file.name,
            detector_backend=translate(cfg, backend))
        file.clean()

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
    stream_cfg = cfg.to_easydict().realtime_stream
    result = DeepFace.stream(stream_cfg.database.dir, source='')
    return 'ok'


@app.route('/v1/change-settings', methods=['POST', 'GET'])
def change_settings():
    args = request.args
    result = cfg.update_cfg(args)
    save_cfg = str2bool(args.get('save', True))
    if save_cfg:
        cfg.save()
    cfg.reload()

    results = {
        'status': 'ok',
        'data': result,
    }
    return results


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)