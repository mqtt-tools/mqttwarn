
import sys
#
# To Use this run.py a .env file is needed in the .vscode directory 
# with the location of python path and name/locaiton of the RUNINI file.
# eg
#PYTHONPATH=C:\\Users\\default\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages
#RUNINI=.vscode\\run.ini

sys.path.append('..\\mqttwarn')
sys.path.append('.vscode')
import attr
from docopt import docopt
#from ..mqttwarn import mqttwarn
import mqttwarn.core
import mqttwarn.util
import mqttwarn.context
import mqttwarn.services
import mqttwarn.commands


mqttwarn.commands.run()