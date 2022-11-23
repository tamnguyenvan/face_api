import tempfile
import os

from werkzeug.utils import secure_filename
from deepface import DeepFace

from .logger import logger
from configs import cfg


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def initialize_env():
    ecfg = cfg.to_easydict()

    # ecfg = EasyDict(cfg)
    if not ecfg.api.lazy_load:
        logger.info('Setting enviroment...')
        assets_dir = os.path.abspath(ecfg.api.assets)
        img1_path = os.path.join(assets_dir, 'face1.jpg')
        img2_path = os.path.join(assets_dir, 'face2.jpg')

        # initialize face verification
        logger.info('Dry run face verification')
        # DeepFace.verify(img1_path, img2_path)

        # initialize face recognition
        logger.info('Dry run face recognition')
        database_dir = ecfg.face_recognition.database.dir
        if not os.path.isdir(database_dir):
            raise FileNotFoundError('Not found face recognition database')
        # DeepFace.find(img1_path, database_dir, model_name=ecfg.face_recognition.model)

        # initialize face analyssi
        logger.info('Dry run face analysis')
        # DeepFace.analyze(img1_path)

        # initialize face detection
        logger.info('Dry run face detection')
        # DeepFace.detectFace(img1_path, detector_backend=ecfg.face_detection.model_name)

        logger.info('Dry run stream')
        database_dir = ecfg.realtime_stream.database.dir
        if not os.path.isdir(database_dir):
            raise FileNotFoundError('Not found real-time stream database')

        # DeepFace.stream(database_dir, source=stream_sample_video)

        logger.info('Finished setting up the enviroment.')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class File:
    def __init__(self, file):
        self.name = ''
        self.f = None
        if file and allowed_file(file.filename):
            self.f = tempfile.NamedTemporaryFile(mode='wb', suffix='face_api', delete=False)
            file.save(self.f.name)
            self.name = self.f.name

    def clean(self):
        if self.name and self.f and os.path.isfile(self.name):
            # self.f.close()
            os.remove(self.name)


def str2bool(x):
    if str(x).lower() == 'true' or str(x) == '1':
        return True
    return False