#-- monitor.py

""" test case for monitor script
"""

from ripsaw import Monitor, Regex
from pathlib import Path
import curio

monitor = Monitor(
    target      = Path(__file__).resolve().parent,
    pattern     = '*.log',
)

@monitor.event(Regex('.*'))
async def match_any_line(trigger):
    '''handle the event'''
    print('match_any_line')
    a = list((1, 2))

    while True:
        match, lines = await trigger()
        print(f'{match}')
        print(f'{lines}')


if __name__ == "__main__":
    monitor.run()



#----------------------------------------------------------------------------------------------#

