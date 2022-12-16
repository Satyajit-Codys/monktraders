import sys
sys.path.insert(0, '/var/www/monktraders')

activate_this = ''
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from app import app as application