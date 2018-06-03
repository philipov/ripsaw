#-- ripsaw.run

"""--- application loop
"""

#from powertools import export
from powertools import AutoLogger
log = AutoLogger()
from powertools import term

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
        '_file_queues',
        '_followers',
        '_handlers',
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
        self._events            = dict()
        self._file_queues       = dict()
        self._followers         = dict()
        self._handlers          = dict()

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


    ######################
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
                ''' use the handler signature to construct its arglist by matching sig names to kwargs keys '''
                sig = [ name
                    for name, param in signature(handler).parameters.items()
                        if  param.kind == param.POSITIONAL_ONLY
                        or  param.kind == param.POSITIONAL_OR_KEYWORD
                ]
                newargs = list()
                for name in sig:
                    newargs.append(kwargs.get(name, None))

                return await handler(*newargs)

            ### register wrapped handler, don't change the deffed function
            self._events[trigger] = wrapped_handler


            return handler

        ####
        return event_handler


    ######################
    def run(self):
        log.print(f'{term.pink("begin watching for new files...")}')
        curio.run( self.watcher() )


    ######################
    async def watcher( self ):
        prev_dirstate = set()
        async with curio.TaskGroup() as followers :
            while True:
                dirstate        = set(self.target.glob(self.pattern)) #todo: async
                new_files       = dirstate - prev_dirstate
                prev_dirstate   = dirstate

                if new_files:
                    ### create new followers
                    for file in sorted(new_files):
                        log.print(f'{term.cyan("new file:")} {file.name}')
                        follower                    = await followers.spawn( self.follower, file )
                        self._followers[file]   = follower

                await curio.sleep( self.interval_scandir )


    ######################
    async def follower( self, file:Path ):

        handlers =  dict()
        queues  =   dict()
        async with curio.TaskGroup() as handlergroup:
            ### setup handlers
            for trigger, handler in self._events.items():
                log.print(f'{term.dcyan(f"spawn line handler for {file.name}:")} {trigger} ')

                queue                               = curio.Queue()
                queues[trigger]                     = queue
                self._file_queues[(file, trigger)]  = queue

                prompter            = await self.make_prompter(queue, trigger)

                ### supported parameters for event handlers
                kwargs              = dict()
                kwargs['prompter']  = prompter
                kwargs['trigger']   = trigger
                kwargs['filename']  = file.name
                kwargs['target']    = file.root
                kwargs['queue']     = queue

                handlers[trigger]   = await handlergroup.spawn(handler, kwargs)
                #todo: determine which parameters to pass above by checking handler's signature; only do it once

            ### push new lines to all handlers
            async with curio.aopen( file, 'r' ) as fstream:
                while True:
                    line = await fstream.readline()
                    if line:
                        log.print( term.dpink(file.name),' ', term.dyellow(line.strip()) )
                        for trigger, queue in queues.items():
                            await queue.put(line)


    ######################
    async def make_prompter( self, queue:curio.Queue, trigger ):
        ''' curry a prompter with the queue inside it by closure
            pass it into the task that wants to wait for the queue to trigger
        '''
        if False:
            print( queue )
            print(self)

        async def prompter():
            ''' watch the queue until a trigger is activated '''
            while True:
                line    = await queue.get()
                match   = trigger.check(line)
                if match is not None:
                    # log.print(f'prompt for {trigger} {match} {line.strip()}')
                    return match, line

        return prompter


#----------------------------------------------------------------------------------------------#
