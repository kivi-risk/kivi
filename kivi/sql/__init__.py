import os
from .SQLengine import *

import platform
if platform.system() == 'Windows':
    os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
