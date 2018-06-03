#-- ripsaw.run

"""--- application loop
"""

#from powertools import export
from powertools import AutoLogger
log = AutoLogger()
from powertools import term
from pprint import pformat

from .trigger import Trigger, Regex
from pathlib import Path
from inspect import signature

import curio

### type categories
sequence    = (list, tuple)
triggerlike = (Trigger, str)

#----------------------------------------------------------------------------------------------#

class Monitor:

    class DuplicateTrigger(Exception):
        ''' attempted to add an event handler for the same trigger twice '''


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
    def __init__(self, *,
                 target:                Path = Path('.'),
                 pattern:                str = '*',
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
    def pattern(self) -> sequence:
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

    def event(self, trigger:triggerlike):
        ''' decorator to register a new event for a trigger
        '''

        ### check for duplicate triggers
        if isinstance(trigger, str):
            trigger = Regex(trigger)
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
    #todo: gracefully respond to kill signals

    def run(self):
        ''' start the monitor
        '''
        curio.run( self.watcher() )


    ######################
    async def watcher( self ):
        ''' -- the root task for the monitor
            watch a directory for files matching a pattern
            spawn follower tasks as new files are found
        '''
        log.print(term.pink("begin watching for new files..."))

        async with curio.TaskGroup() as followers :
            prev_dirstate = set()
            while True:
                dirstate        = set(self.target.glob(self.pattern)) #todo: async
                new_files       = dirstate - prev_dirstate
                prev_dirstate   = dirstate

                if new_files:
                    ### create new followers
                    for file in sorted(new_files):
                        follower                    = await followers.spawn( self.follower, file )

                log.print(
                    term.pink('scanned count:'), f' \n',
                    pformat({file.name: count for file, count in self._scannedcount.items()})
                )

                await curio.sleep( self.interval_scandir )


    ######################
    async def follower( self, file:Path ):
        ''' -- monitor a file
            spawn new instances of the registered event handlers
            tail the file and whenever new lines come in,
                dispatch them to the queues that are being
                watched by the prompter tasks for each handler.
        '''
        log.print(term.cyan('new file:'), f' {file.name}')

        async with curio.TaskGroup() as handlergroup:
            self._scannedcount.setdefault(file, 0)
            handlers =  dict()
            queues  =   dict()

            ### create handler tasks
            for trigger, handler in self._events.items():
                log.print(term.dcyan(f'spawn line handler for {file.name}:'), f' {trigger}')

                queue               = curio.Queue()
                queues[trigger]     = queue
                #prompter            = self.make_prompter(queue, trigger)
                prompter           = self.Prompter(queue, trigger)

                ### supported parameters for event handlers:
                kwargs              = dict()
                kwargs['prompter']  = prompter
                kwargs['trigger']   = trigger
                kwargs['filename']  = file.name
                kwargs['target']    = file.root
                kwargs['queue']     = queue

                handlers[trigger]   = await handlergroup.spawn(handler, kwargs)

            ### push new lines to all handlers
            async with curio.aopen( file, 'r' ) as fstream:
                while True:
                    line = await fstream.readline()
                    if line:
                        log.print( term.dpink(file.name),' put ', term.dyellow(line.strip()) )
                        for trigger, queue in queues.items():
                            await queue.put(line)
                        self._scannedcount[file] += 1


    ######################
    @staticmethod
    def make_prompter( queue:curio.Queue, trigger ):
        ''' Used by the follower task to subscribe its event handlers to its updates
            Curry a prompter so that event handler functions
                don't have to carry around their trigger and queue.

                DEPRECATED
        '''

        async def prompter():
            ''' block the event handler; read the queue until a line activating the trigger is found
            '''
            while True:
                line    = await queue.get()
                match   = trigger.check(line)
                if match is not None:
                    # log.print(f'prompt for {trigger} {match} {line.strip()}')
                    return match, line

        return prompter

    ######################
    class Prompter:
        ''' Used by the follower task to subscribe its event handlers to its updates
            Asynchronous Iterable implementation
        '''

        def __init__(self, queue:curio.Queue, trigger):
            self.queue      = queue
            self.trigger    = trigger

        def __aiter__(self):
            ''' Prompter is an async iterator '''
            return self

        async def __call__(self):
            ''' Prompter is an async function '''
            return await self.__anext__()

        async def __anext__(self):
            ''' block the event handler; read the queue until a line activating the trigger is found
            '''
            while True:
                line    = await self.queue.get()
                match   = self.trigger.check(line)
                if match is not None:
                    # log.print(f'prompt for {trigger} {match} {line.strip()}')
                    return match, line

            raise StopAsyncIteration



#----------------------------------------------------------------------------------------------#
