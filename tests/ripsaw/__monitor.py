#-- tests.ripsaw.monitor

''' unit tests
'''

### logging / color
from powertools import AutoLogger
log = AutoLogger()
from powertools import term
term.init_color()
log.print('    ', term.pink('----'), ' ', term.yellow('ripsaw monitor'), ' ', term.pink('----'))


#----------------------------------------------------------------------------------------------#
#   TEST CASE 1

def test__monitor():
    ''' null test
    '''
    from ripsaw import Monitor

    monitor = Monitor()


#----------------------------------------------------------------------------------------------#
#   TEST CASE 2

def make_monitor(directory, event_count):
    ''' create a monitor with event handlers that count the number of times they're called
    '''
    import re
    from ripsaw import Monitor, Regex, And, Or

    monitor = Monitor(
        target          = directory,
        pattern         = '*.log',
        dir_interval    = 0.5
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
class TestTimeout(Exception):
        '''didn't finish reading test files before timeout'''

def test__watcher(path_testdata, path_log1, path_log2):
    ''' event handlers count how many times they got called during the test
    '''
    import curio
    from collections import Counter
    from ripsaw import Monitor

    ######################
    async def tester(monitor:Monitor, goal):
        ''' replace the launcher task
        '''
        watcher = await curio.spawn(monitor.watcher)
        watcher:curio.Task

        await until_test_finished(monitor, goal)
        await watcher.cancel()

    ######################
    async def until_test_finished(monitor:Monitor, goal):
        ''' wait until the scancount reaches the goal state
            a TestTimeout is raised if the read isn't complete in 10 seconds
        '''
        duration = 0.0
        while True:
            if all( monitor.scannedcount.get(file, -1) >= goal[file] for file in goal):
                break
            elif duration > 10.0:
                raise TestTimeout(monitor.scannedcount)
            else:
                await curio.sleep(0.1)
                duration += 0.1

    ######################

    event_count = Counter()
    monitor0    = make_monitor(path_testdata, event_count)

    goal = {
        path_log1:  7,
        path_log2:  7
    }

    curio.run(tester(monitor0, goal))

    log.print(event_count)
    assert event_count['aoeu']  == 3
    assert event_count['and']   == 2
    assert event_count['error'] == 1

    # assert False


#----------------------------------------------------------------------------------------------#


