import os

from werkzeug.utils import secure_filename
from deepface import DeepFace

from .logger import logger
from configs import cfg


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def initialize_env():
    if not cfg.api.lazy_load:
        logger.info('Setting enviroment...')
        assets_dir = os.path.abspath(cfg.api.assets)
        img1_path = os.path.join(assets_dir, 'face1.jpg')
        img2_path = os.path.join(assets_dir, 'face2.jpg')

        # initialize face verification
        logger.info('Dry run face verification')
        # DeepFace.verify(img1_path, img2_path)

        # initialize face recognition
        logger.info('Dry run face recognition')
        database_dir = cfg.face_recognition.database.dir
        if not os.path.isdir(database_dir):
            raise FileNotFoundError('Not found face recognition database')
        DeepFace.find(img1_path, database_dir, model_name=cfg.face_recognition.model_name)

        # initialize face analyssi
        logger.info('Dry run face analysis')
        # DeepFace.analyze(img1_path)

        # initialize face detection
        logger.info('Dry run face detection')
        # DeepFace.detectFace(img1_path, detector_backend=cfg.face_detection.model_name)

        logger.info('Dry run stream')
        database_dir = cfg.realtime_stream.database.dir
        if not os.path.isdir(database_dir):
            raise FileNotFoundError('Not found real-time stream database')

        # DeepFace.stream(database_dir, source=stream_sample_video)

        logger.info('Finished setting up the enviroment.')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class FileManager:

    @classmethod
    def get(cls, file):
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            return file_path

    @classmethod
    def clean(cls, file):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if file_path and os.path.isfile(file_path):
            os.remove(file_path)