#-- tests.ripsaw.monitor

''' unit tests
'''

### logging / color
from powertools import AutoLogger
log = AutoLogger()
from powertools import term
term.init_color()
log.print('    ', term.pink('----'), ' ', term.yellow('ripsaw monitor'), ' ', term.pink('----'))

### imports
import pytest

#----------------------------------------------------------------------------------------------#
def test__monitor():
    ''' import test
    '''
    from ripsaw import Monitor

    monitor = Monitor()


#----------------------------------------------------------------------------------------------#
def make_monitor(event_count):
    ''' create a monitor with event handlers for testing using included sample logs'''
    import re
    from pathlib import Path
    from ripsaw import Monitor, Regex, And, Or

    monitor = Monitor(
        target      = Path(__file__).resolve().parents[1] / 'data',
        pattern     = '*.log',
    )

    ######################
    @monitor.event(Regex('ERROR'))
    async def handle_error(prompter):
        log.print(term.green(f'starting match_error for {prompter.file.name} ...'))
        async for event in prompter:
            log.print(prompter.file.name, term.dgreen(f' {prompter.trigger}:'), f' {event.match} | ', term.green(event.line.strip()) )
            event_count['error'] += 1

    ######################
    @monitor.event(Regex('aoeu'))
    async def handle_aoeu(prompter):
        log.print(term.green(f'starting match_aoeu for {prompter.file.name} ...'))
        async for event in prompter:
            log.print(prompter.file.name, term.dgreen(f' {prompter.trigger}:'), f' {event.match} | ', term.green(event.line.strip()) )
            event_count['aoeu'] += 1

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
            event_count['and'] += 1

    ####
    return monitor

#################################################################################
async def tester(monitor):
    ''' replaces the launcher task
        instead of waiting for a signal, just wait a given time before cancelling
    '''
    import curio

    watcher = await curio.spawn(monitor.watcher)
    watcher:curio.Task

    await curio.sleep(5)
    await watcher.cancel()

#################################################################################
def test__watcher():
    ''' event handlers count how many times they got called during the test
    '''
    import curio
    from collections import Counter

    event_count = Counter()
    monitor     = make_monitor(event_count)

    curio.run(tester(monitor))

    log.print(event_count)
    assert event_count['aoeu']  == 3
    assert event_count['and']   == 2
    assert event_count['error'] == 1

    assert False


#----------------------------------------------------------------------------------------------#


