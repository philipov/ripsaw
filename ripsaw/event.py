#-- ripsaw.event

"""--- event handler api
"""

#----------------------------------------------------------------------------------------------#

class Event:
    __slots__ = ('trigger', 'handler')

    def __init__(self, trigger, handler):
        self.trigger = trigger
        self.handler = handler



#----------------------------------------------------------------------------------------------#

_events = dict()

def event(trigger):
    ''' decorate a coroutine that handles a particular trigger
        add it to the list of registered events
    '''
    def event_handler(handler):
        event = Event(trigger, handler)
        _events[trigger] = event

        return handler

    return event_handler


#----------------------------------------------------------------------------------------------#

