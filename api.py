import base64

import cv2
import numpy as np
from flask import Flask, request
from deepface import DeepFace

from configs import cfg
from face_api.utils import initialize_env, File, str2bool
from face_api.exceptions import VerificationError, RecognitionError, DetectionError


initialize_env()

app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>Greetings, this is Face API</h1>'


@app.route('/v1/verify', methods=['POST'])
def verify():
    if request.files:
        if 'file1' not in request.files or 'file2' not in request.files:
            return {
                'status': 'failed',
                'data': [],
                'message': 'Request is missing either `file1` or `file2`'
            }
        file1 = request.files['file1']
        file2 = request.files['file2']

        facever_cfg = cfg['endpoints']['face-verification']
        args = request.args

        file1 = File(file1)
        file2 = File(file2)
        try:
            result = DeepFace.verify(
                img1_path=file1.name,
                img2_path=file2.name,
                model_name=args['model'] if args['model'] else facever_cfg['model'],
                distance_metric=args['distance-metric'] if args['distance-metric'] else facever_cfg['distance-metric'],
                detector_backend=args['detector-backend'] if args['detector-backend'] else facever_cfg['detector-backend'],
                enforce_detection=args['enforce-detection'] == 'true' if args['enforce-detection'] else facever_cfg['enforce-detection'])
        except Exception:
            file1.clean()
            file2.clean()
            return {
                'status': 'failed',
                'data': [],
                'message': 'Internal sever error'
            }
        finally:
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
        if 'file' not in request.files:
            return {
                'status': 'failed',
                'data': [],
                'message': 'Request is missing `file`'
            }
        file = request.files['file']
        file = File(file)
        facerec_cfg = cfg['endpoints']['face-recognition']

        try:
            result = DeepFace.find(
                img_path=file.name,
                db_path=facerec_cfg['db-path'],
                model_name=facerec_cfg['model'],
                distance_metric=facerec_cfg['distance_metric'],
                detector_backend=facerec_cfg['detector_backend'],
                enforce_detection=facerec_cfg['enforce_detection'])
        except Exception:
            file.clean()
            return {
                'status': 'failed',
                'data': [],
                'message': 'Internal sever error'
            }
        finally:
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
        if 'file' not in request.files:
            return {
                'status': 'failed',
                'data': [],
                'message': 'Request is missing `file`'
            }

        file = request.files['file']
        file = File(file)
        facedet_cfg = cfg['endpoints']['face-detection']

        args = dict(request.args)
        detector_backend = args['detector-backend'] if args.get('detector-backend') else facedet_cfg['detector-backend']
        enforce_detection = args['enforce-detection'] == 'true' if args.get('enforce-detection') else facedet_cfg['enforce-detection']
        try:
            result = DeepFace.detectFace(
                file.name,
                detector_backend=detector_backend,
                enforce_detection=enforce_detection)
        except Exception:
            file.clean()
            return {
                'status': 'failed',
                'data': [],
                'message': 'Internal sever error'
            }
        finally:
            file.clean()

        if isinstance(result, np.ndarray) and len(result):
            restored_face = np.clip(result * 255, 0, 255).astype(np.uint8)
            encoded = cv2.imencode('.jpeg', restored_face)[1]
            b64img = base64.b64encode(encoded).decode('utf-8')

            results = {
                'status': 'ok',
                'data': {
                    'image': b64img,
                    'dtype': 'base64',
                    'detector-backend': detector_backend,
                    'enforce-detection': enforce_detection
                }
            }
            return results

        return {
            'status': 'error',
            'data': [],
            'message': 'could not detect face in given image'
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