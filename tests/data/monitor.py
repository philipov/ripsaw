#-- monitor.py

""" test monitor script
"""

### logging / color
from powertools import AutoLogger
log = AutoLogger()
from powertools import term
term.init_color()
log.print('    ', term.pink('----'), ' ', term.yellow('ripsaw monitor'), ' ', term.pink('----'))

### imports
from ripsaw import Monitor, Regex, And, Or
from pathlib import Path
import re

#----------------------------------------------------------------------------------------------#

monitor = Monitor(
    target      = Path(__file__).resolve().parent,
    pattern     = '*.log',
)

######################
@monitor.event(Regex('ERROR'))
async def handle_error(prompter):
    log.print(term.green(f'starting match_error for {prompter.file.name} ...'))
    async for event in prompter:
        log.print(prompter.file.name, term.dgreen(f' {prompter.trigger}:'), f' {event.match} | ', term.green(event.line.strip()) )

######################
@monitor.event(Regex('aoeu'))
async def handle_aoeu(prompter):
    log.print(term.green(f'starting match_aoeu for {prompter.file.name} ...'))
    async for event in prompter:
        log.print(prompter.file.name, term.dgreen(f' {prompter.trigger}:'), f' {event.match} | ', term.green(event.line.strip()) )

######################
@monitor.event( And(
        Regex('.*ERROR.*', re.IGNORECASE),
        Regex('.*aoeu.*'),
))
async def handle_and(prompter):
    log.print(term.green(f'starting match_and for {prompter.file.name} ...'))
    while True:
        event = await prompter()
        log.print(prompter.file.name, term.dgreen(f' {prompter.trigger}:'), f' {event.match} | ', term.green(event.line.strip()) )

######################
if __name__ == "__main__":
    monitor.run()


#----------------------------------------------------------------------------------------------#

