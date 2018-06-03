#-- monitor.py

""" ripsaw monitor """

from powertools import AutoLogger
log = AutoLogger()
from powertools import term
term.init_color()
log.print('    ', term.pink('----'), ' ', term.yellow('ripsaw monitor'), ' ', term.pink('----'))

from ripsaw import Monitor, Regex, And, Or
import re
from pathlib import Path

#----------------------------------------------------------------------------------------------#

monitor = Monitor(
    target      = Path(__file__).resolve().parent,
    pattern     = '*.log',
)

######################
@monitor.event(Regex('ERROR'))
async def match_error(prompter):
    log.print(term.green(f'starting match_error for {prompter.file.name} ...'))
    async for event in prompter:
        log.print(prompter.file.name, term.dgreen(f' {prompter.trigger}:'), f' {event.match} | ', term.green(event.line.strip()) )
        # await curio.sleep(monitor.interval_scanfile)


######################
@monitor.event(Regex('aoeu'))
async def match_aoeu(prompter):
    log.print(term.green(f'starting match_aoeu for {prompter.file.name} ...'))
    async for event in prompter:
        log.print(prompter.file.name, term.dgreen(f' {prompter.trigger}:'), f' {event.match} | ', term.green(event.line.strip()) )


######################
@monitor.event( And(
        Regex('.*ERROR.*', re.IGNORECASE),
        Regex('.*aoeu.*'),
))
async def match_and(prompter):
    log.print(term.green(f'starting match_and for {prompter.file.name} ...'))
    while True:
        event = await prompter()
        log.print(prompter.file.name, term.dgreen(f' {prompter.trigger}:'), f' {event.match} | ', term.green(event.line.strip()) )


######################
if __name__ == "__main__":
    monitor.run()


#----------------------------------------------------------------------------------------------#

