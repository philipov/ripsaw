#-- ripsaw.monitor

""" Monitor class
    Monitor.event handler decorator
    Monitor.run method
    Monitor.launcher task
    Monitor.watcher task
    Monitor.follower task
    Monitor.Prompter async iterator
    Monitor.Prompter.Event datatype

"""

### logging / color
from powertools import AutoLogger
log = AutoLogger()
from powertools import term
from pprint import pformat

### imports
import signal
import curio

from pathlib import Path
from inspect import signature
from functools import namedtuple

from .trigger import Trigger, Regex

### type annotation categories
patternlike = (tuple, str)
triggerlike = (Trigger, str)

#----------------------------------------------------------------------------------------------#

class Monitor:
    ''' A class to encapsulate an instance of the application.
        A user wishing to modify the internals of the monito can subclass Monitor,
            override just the pieces they wish to extend,
            and the rest of the system will use it
    '''

    class DuplicateTrigger(Exception):
        ''' attempted to add an event handler for the same trigger twice
        '''

    ######################
    __slots__ = (
        '_target',
        '_pattern',
        '_savepath',
        '_interval_scandir',
        '_interval_scanfile',

        '_events',
        '_scannedcount',
    )
    def __init__(   self, *,
                    target:                Path = Path('.'),
                    pattern:        patternlike = '*.log',
                    savepath:              Path = None,
                    interval_scandir:       int = 5,
                    interval_scanfile:      int = 5,
        ):
        ''' an instance of a monitor watches multiple files inside a single directory
        '''

        ### private state
        self._events:dict       = dict()
        self._scannedcount:dict = dict()

        ### read-only config settings
        self._target            = target
        self._pattern           = pattern
        self._savepath          = savepath
        self._interval_scandir  = interval_scandir
        self._interval_scanfile = interval_scanfile

        log.print(f'{term.white("new monitor on:     ")} {self.target}')
        log.print(f'{term.white("file pattern:")}        {self.pattern}')
        log.print(f'{term.white("savepath:")}            {self.savepath}')
        log.print(f'{term.white("dir scan interval:")}   {self.interval_scandir}' )
        log.print(f'{term.white("file scan interval:")}  {self.interval_scandir}' )

    ######################

    @property
    def target(self) -> Path:
        return self._target

    @property
    def pattern(self) -> patternlike:
        return self._pattern

    @property
    def savepath(self) -> Path:
        return self._savepath

    @property
    def interval_scandir( self ) -> int:
        return self._interval_scandir

    @property
    def interval_scanfile( self ) -> int:
        return self._interval_scanfile


    #-------------------------------------------------------------------#

    def event(  self,
                trigger:    triggerlike,
                *,
                name:       str = None,
        ):
        ''' decorator to register a new event for a trigger
        '''

        ### strings default to regex patterns
        if isinstance(trigger, str):
            trigger = Regex(trigger)

        ### check for duplicate triggers
        if trigger in self._events:
            raise Monitor.DuplicateTrigger(trigger)

        def event_handler(handler):
            ''' decorate the handler coroutine '''

            log.print(f'{term.dcyan("new handler:")}         {trigger} {term.dcyan("->")} <{handler.__class__.__name__} {handler.__name__}>')
            async def wrapped_handler(kwargs):
                ''' need to
                    use the handler's function signature to construct its arglist by matching sig names to kwargs keys '''

                sig = [ name
                        for name, param in signature(handler).parameters.items()
                            if  param.kind == param.POSITIONAL_ONLY
                            or  param.kind == param.POSITIONAL_OR_KEYWORD
                        ]
                newargs = list()
                for name in sig:
                    newargs.append(kwargs.get(name, None))

                return await handler(*newargs)

            ### register wrapped handler for use by follower
            self._events[trigger] = wrapped_handler

            ### don't alter the defined function
            return handler

        ####
        return event_handler


    #-------------------------------------------------------------------#

    def run(self):
        ''' start the application
        '''
        curio.run( self.launcher() )

    ######################
    async def launcher(self):
        ''' -- the root task
            start a watcher, then waits for a shutdown signal
        '''

        watcher = await curio.spawn(self.watcher)

        shutdown = curio.SignalEvent(signal.SIGINT, signal.SIGTERM)
        await shutdown.wait()
        raise SystemExit()


    ######################
    async def watcher( self ):
        ''' -- monitor a directory
            watch a directory for files matching a pattern
            spawn follower tasks when new files are found
        '''
        log.print(term.pink("begin watching for new files..."))

        async with curio.TaskGroup() as followergroup :
            followers       = dict()
            prev_dirstate   = set()
            while True:

                ### find new files todo: if pattern is a tuple, its elements are patterns
                dirstate        = set(self.target.glob(self.pattern)) #todo: async
                new_files       = dirstate - prev_dirstate
                prev_dirstate   = dirstate

                ### create new followers
                if new_files:
                    for file in sorted(new_files):
                        follower        = await followergroup.spawn( self.follower, file )
                        followers[file] = follower

                ### status report
                log.print(
                    term.pink('scanned count:'), f' \n',
                    pformat({file.name: count for file, count in self._scannedcount.items()})
                )
                await curio.sleep( self.interval_scandir )


    ######################
    async def follower( self, file:Path ):
        ''' -- monitor a file
            spawn new instances of the registered event handlers
            tail the file, whenever new lines come in,
                use queues to dispatch them to the prompter tasks for each handler.
        '''
        log.print(term.cyan('new file:'), f' {file.name}')

        async with curio.TaskGroup() as handlergroup:
            handlers =  dict()
            queues  =   dict()

            ### create handler tasks
            for trigger, handler in self._events.items():
                log.print(term.dcyan(f'spawn line handler for {file.name}:'), f' {trigger}')
                queue               = curio.Queue()
                queues[trigger]     = queue
                prompter            = self.Prompter(queue, trigger, file)

                ### supported parameters for event handlers:
                kwargs              = dict()
                kwargs['prompter']  = prompter

                handlers[trigger]   = await handlergroup.spawn(handler, kwargs)

            ### process the file
            async with curio.aopen( file, 'r' ) as fstream:
                ### fast-forward through already-scanned lines todo
                self._scannedcount.setdefault(file, 0)

                ### follow the file and push new lines to prompter queues
                while True:
                    line = await fstream.readline()
                    if line:
                        log.print( term.dpink(file.name),' put ', term.dyellow(line.strip()) )
                        self._scannedcount[file] += 1
                        for trigger, queue in queues.items():
                            await queue.put((line, self._scannedcount[file]))


    ######################
    class Prompter:
        ''' -- read the queue and wait until the trigger fires
            used by the follower task to subscribe its event handlers to line updates
            asynchronous Iterator; may be directly called to get next
            there is no way to reach StopAsyncIteration at the moment
        '''

        Event = namedtuple('Event', ('match', 'line', 'ln'))


        __slots__ = (
            'queue',
            '_trigger',
            '_file',
        )
        def __init__(   self,
                        queue:      curio.Queue,
                        trigger:    Trigger,
                        file:       Path,
            ):
            self.queue      = queue
            self._trigger   = trigger
            self._file      = file

        @property
        def trigger(self):
            return self._trigger

        @property
        def file(self):
            return self._file


        async def __anext__(self):
            ''' async block until the queue produces a line that activates the trigger.
            '''
            while True:
                (line, ln)  = await self.queue.get()
                match       = self.trigger.check(line)
                if match is not None:
                    return self.Event(match, line, ln)

            raise StopAsyncIteration

        def __aiter__(self):
            ''' Prompter object is an async iterator '''
            return self

        async def __call__(self):
            ''' Prompter object is an async function '''
            return await self.__anext__()


#----------------------------------------------------------------------------------------------#
