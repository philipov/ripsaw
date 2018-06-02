#-- ripsaw.run

"""--- application loop
"""

from .trigger import Trigger, Regex
from pathlib import Path

### type categories
sequence    = (list, tuple)
triggerlike = (Trigger, str)

#----------------------------------------------------------------------------------------------#
class Monitor:

    class DuplicateTrigger(Exception):
        ''' attempted to add an event handler for the same trigger twice '''

    __slots__ = (
        'target',
        'select',
        '_events',
        '_dirstate'
    )

    ######################
    def __init__(self, *,
                 target:   Path = None,
                 select:   sequence = None,
                ):
        ''' configure monitor settings
        '''
        self.target     = target
        self.select     = select
        self._events    = dict()
        self._dirstate  = set()

    ######################
    def event(self, trigger:triggerlike):
        ''' decorate a coroutine that handles a particular trigger
            add it to the list of registered events
        '''
        if isinstance(trigger, str):
            trigger = Regex(trigger)
        def event_handler(handler):
            self._events[trigger] = handler
            return handler

        return event_handler


    ######################
    async def watch_dir(self, loop):

        while True:
            dirstate = set(self.target)


    ######################
    def run(self):
        import asyncio

        ioloop = asyncio.get_event_loop()
        wait_tasks = asyncio.wait()
        ioloop.run_until_complete(wait_tasks)
        ioloop.close()

        pass


#----------------------------------------------------------------------------------------------#
