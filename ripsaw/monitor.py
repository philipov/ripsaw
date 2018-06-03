#-- ripsaw.run

"""--- application loop
"""

#from powertools import export
from powertools import AutoLogger
log = AutoLogger()
from powertools import term
term.init_color()

from .trigger import Trigger, Regex
from pathlib import Path

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
        ''' decorate a coroutine that handles a particular trigger
            add it to the list of registered events
        '''
        if isinstance(trigger, str):
            trigger = Regex(trigger)
            if trigger in self._events:
                raise Monitor.DuplicateTrigger(trigger)
        def event_handler(handler):
            self._events[trigger] = handler
            return handler

        return event_handler


    ######################
    def run(self):
        log.print(f'    {term.pink("----")} {term.yellow("ripsaw")} {term.pink("----")}')
        log.print(f'{term.white("begin monitoring on:")} {self.target}')
        log.print(f'{term.white("file pattern:")}        {self.pattern}')
        log.print(f'{term.white("savepath:")}            {self.savepath}')
        log.print(f'{term.white("dir scan interval:")}   {self.interval_scandir}' )
        curio.run(self.watch_for_new())


    ######################
    async def watch_for_new(self):
        prev_dirstate = set()
        async with curio.TaskGroup() as followers :
            while True:
                dirstate        = set(self.target.glob(self.pattern)) #todo: async
                new_files       = dirstate - prev_dirstate
                prev_dirstate   = dirstate

                if new_files:
                    for file in new_files:
                        log.print(f'{term.cyan("new file:")} {file.name}')
                        follower                    = await followers.spawn(self.follow_file, file)
                        self._followers[file]   = follower

                await curio.sleep( self.interval_scandir )


    ######################
    async def follow_file( self, file:Path, ):

        trigger_handlers = dict()
        async with curio.TaskGroup() as handlers:
            # setup handlers
            for trigger, handler in self._events.items():
                log.print(f'{term.dcyan(f"spawn line handler for {file.name}:")} {trigger} : {handler}')

                handler_queue                           = curio.Queue()
                self._file_queues[(file, trigger)]  = handler_queue

                trigger_task        = await self.make_trigger( handler_queue, trigger )
                # handlers[trigger]   = await handlers.spawn(handler, trigger_task)

            # push new lines to all handlers
            async with curio.aopen( file, 'r' ) as fstream:
                #async for line in file:
                while True:
                    line = await fstream.readline()
                    if line:
                        log.print( f'{term.dpink(file.name)} {line.strip()}' )


    ######################
    async def make_trigger(self, handler_queue, trigger):
        if False:
            print(handler_queue)
            print(self)

        async def trigger_task():
            return "Trigger"

        return trigger_task









#----------------------------------------------------------------------------------------------#
