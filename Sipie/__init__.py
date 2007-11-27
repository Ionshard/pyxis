
__author__ = 'Eli Criffield pyeli AT zendo Dot NET'
__version__ = '''0.1196144357'''
__copyright__ =  '''(c)Eli Criffield <pyeliATzendoDOTnet>
http://eli.criffield.net/sipie/
Licensed under GPLv2
http://www.gnu.org/licenses/gpl.txt'''



from Factory import *
from Config import *
from StreamHandler import *
from Player import *
from cliPlayer import *
try:
    from gtkPlayer import *
except:
    pass
try:
    from wxPlayer import *
except:
    pass
try:
    from Popup import PlaylistPopup
except:
    pass



#global sipie
global globalSipie
globalSipie = None
