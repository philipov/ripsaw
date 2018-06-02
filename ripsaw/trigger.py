#-- ripsaw.trigger

"""--- event triggers
"""

#----------------------------------------------------------------------------------------------#

class Trigger:
    '''
    '''
    __slots__ = ('key', )

    def __hash__(self):
        return hash(self.key)

    def check(self, line):
        ''' return None on no-match, or else return the match '''
        raise NotImplementedError


#----------------------------------------------------------------------------------------------#

class Regex(Trigger):
    '''
    '''
    __slots__ = ('key', 'regex',)

    def __init__(self, pattern:str):
        import re

        self.key    = pattern
        self.regex  = re.compile(pattern)

    def check(self, line):
        return self.regex.match(line)



#----------------------------------------------------------------------------------------------#

