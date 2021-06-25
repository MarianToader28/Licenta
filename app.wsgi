#!/usr/bin/env python3
#acest fisier face legatura intre site-ul Flask si serverul Apache2 
import sys

activate_venv = '/var/www/html/FlaskWeb/env/bin/activate_this.py'

with open(activate_venv) as file_:
        exec(file_.read(), dict(__file__=activate_venv))

sys.path.insert(0, '/var/www/html/FlaskWeb')

from web import app as application