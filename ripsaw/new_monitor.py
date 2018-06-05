#-- monitor.py

""" sample monitor script
"""

### logging / color
from powertools import AutoLogger
log = AutoLogger()
from powertools import term
term.init_color()
log.print('    ', term.pink('----'), ' ', term.yellow('ripsaw monitor'), ' ', term.pink('----'))

### imports
from ripsaw import Monitor, Regex
from pathlib import Path
import re

#----------------------------------------------------------------------------------------------#

monitor = Monitor(
    target      = Path(__file__).resolve().parent,
    pattern     = '*.log',
)

######################
@monitor.event(Regex('.*INFO.*'))
async def handle_info(prompter):
    async for event in prompter:
        log.print(f'[{prompter.file.name}] found info on line {event.ln}: {event.line.strip()}, {event.match}')


@monitor.event(Regex('.*ERROR.*', re.IGNORECASE))
async def handle_error(prompter):
    while True:
        # do something before waiting
        event = await prompter()
        log.print(f'[{prompter.file.name}] found error on line {event.ln}: {event.line.strip()}, {event.match}')


######################
if __name__ == "__main__":
    monitor.run()


#----------------------------------------------------------------------------------------------#

