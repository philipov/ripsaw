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
import curio
from itertools import repeat

#----------------------------------------------------------------------------------------------#

monitor = Monitor(
    target      = Path(__file__).resolve().parent,
    pattern     = '*.log',
)

######################
@monitor.event(Regex('ERROR'))
async def match_error(prompter, filename, trigger):
    log.print(term.green(f'starting match_error for {filename} ...'))
    async for match, line in prompter:
        log.print(filename, term.dgreen(f' {trigger}:'), f' {match} | ', term.green(line.strip()) )
        # await curio.sleep(monitor.interval_scanfile)


######################
@monitor.event(Regex('aoeu'))
async def match_aoeu(prompter, filename, trigger):
    log.print(term.green(f'starting match_aoeu for {filename} ...'))
    async for match, line in prompter:
        log.print(filename, term.dgreen(f' {trigger}:'), f' {match} | ', term.green(line.strip()) )


######################
@monitor.event( And(
        Regex('.*ERROR.*', re.IGNORECASE),
        Regex('.*aoeu.*'),
))
async def match_and(prompter, filename, trigger):
    log.print(term.green(f'starting match_and for {filename} ...'))
    while True:
        match, line = await prompter()
        log.print(filename, term.dgreen(f' {trigger}:'), f' {match} | ', term.green(line.strip()) )



######################
if __name__ == "__main__":
    monitor.run()


#----------------------------------------------------------------------------------------------#

