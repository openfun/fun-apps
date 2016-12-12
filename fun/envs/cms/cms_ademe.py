# -*- coding: utf-8 -*-


# FUN_BASE_ROOT should be added to Python PATH before importing this file
import sys
from path import path
BASE_ROOT = path('/edx/app/edxapp/')
FUN_BASE_ROOT = BASE_ROOT / "fun-apps"
sys.path.append(FUN_BASE_ROOT)



from .common_wb import *
