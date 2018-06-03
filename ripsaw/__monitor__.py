#-- __monitor__.py

""" new ripsaw monitor script
"""

from powertools import AutoLogger
log = AutoLogger()
from powertools import term
term.init_color()
log.print('    ', term.pink('----'), ' ', term.yellow('ripsaw monitor'), ' ', term.pink('----'))

from ripsaw import Monitor, Regex
from pathlib import Path

#----------------------------------------------------------------------------------------------#

monitor = Monitor(
    target      = Path(__file__).resolve().parent,
    pattern     = '*.log',
)

######################
@monitor.event(Regex('.*'))
async def match_any_line(prompter, filename, trigger):
    log.print(term.green('starting match_any_line ...'))
    while True:
        match, line = await prompter()
        log.print(filename, term.dgreen(f' event[{trigger}]:'), f' {match} | {line.strip()}' )
        # await curio.sleep(monitor.interval_scanfile)


######################
if __name__ == "__main__":
    monitor.run()


#----------------------------------------------------------------------------------------------#

