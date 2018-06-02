#-- monitor.py

""" test case for monitor script
"""

from ripsaw import Monitor
from pathlib import Path

monitor = Monitor(
    target  = Path('.'),
    select  = ['.log',]
)

@monitor.event('.*')
def match_any_line():
    '''handle the event'''
    pass





if __name__ == "__main__":
    monitor.run()


#----------------------------------------------------------------------------------------------#

