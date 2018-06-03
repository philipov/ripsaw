#-- ripsaw.new

"""--- create a blank monitor script
"""

from pathlib import Path
import shutil

#----------------------------------------------------------------------------------------------#

template_file = Path(__file__).resolve().parent / '__monitor__.py'

def main(target:Path):
    '''copy template from package location to target location'''


    shutil.copyfile(str(template_file), str(target))


#----------------------------------------------------------------------------------------------#
if __name__ == "__main__":
    import sys
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')/'monitor.py'

    main(target)


#----------------------------------------------------------------------------------------------#

