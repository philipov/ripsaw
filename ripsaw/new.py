#-- ripsaw.new

"""--- create a blank monitor script
"""

from pathlib import Path
import shutil
import sys


#----------------------------------------------------------------------------------------------#

if __name__ == "__main__":

    ### copy template from package location to target location
    template_file = Path(__file__).resolve().parent / 'new_monitor.py'

    target = Path(sys.argv[1]) \
        if len(sys.argv) > 1 \
        else Path('.') / 'monitor.py'

    shutil.copyfile(str(template_file), str(target))


#----------------------------------------------------------------------------------------------#

