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

    def __repr__(self):
        return f'<{self.__class__.__name__}|{self.key}>'

    def check(self, line):
        ''' return None for no-match, or else return the match '''
        raise NotImplementedError


#----------------------------------------------------------------------------------------------#

class Regex(Trigger):
    ''' match line against a regular expression
    '''
    __slots__ = ('key', 'regex',)

    def __init__(self, pattern:str, *flags):
        import re

        self.key    = pattern
        self.regex  = re.compile(f'^{pattern}$', *flags)

    def check(self, line):
        return self.regex.match(line)


#----------------------------------------------------------------------------------------------#

class And(Trigger):
    ''' true if all trigger arguments are true
        does not short-circuit
    '''
    __slots__ = ('key', 'arguments',)

    def __init__(self, *arguments):
        self.key        = ('AND', *arguments)
        self.arguments  = arguments

    def __repr__(self):
        return f'<{self.__class__.__name__}|{self.key[1:]}>'

    def check(self, line):
        results     = list(('AND',))
        any_none    = False
        for argument in self.arguments:
            argument:Trigger
            result  = argument.check(line)
            if result is None:
                any_none = True
            results.append(result)

        if any_none:
            results = None
        else:
            results = tuple(results)
        return results


#----------------------------------------------------------------------------------------------#

class Or(Trigger):
    ''' true if any trigger arguments are true
        does not short-circuit
    '''
    __slots__ = ('key', 'arguments',)

    def __init__(self, *arguments):
        self.key        = ('OR', *arguments)
        self.arguments  = arguments

    def __repr__(self):
        return f'<{self.__class__.__name__}|{self.key[1:]}>'

    def check(self, line):
        results     = list(('OR',))
        all_none    = True
        for argument in self.arguments:
            argument:Trigger
            result  = argument.check(line)
            if result is not None:
                all_none = False
            results.append(result)

        if all_none:
            results = None
        else:
            results = tuple(results)
        return results


#----------------------------------------------------------------------------------------------#

