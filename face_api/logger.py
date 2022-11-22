import os
import logging


level = logging.INFO if os.getenv('STAGE') == 'prod' else logging.DEBUG
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', level=level)
logger = logging.getLogger('face_api')