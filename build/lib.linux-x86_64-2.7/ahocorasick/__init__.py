## fixme: add documentation

import _ahocorasick


__all__ = ['KeywordTree']


## A high level version of the keyword tree.  Most of the methods here
## are just delegated over to the underlying C KeywordTree.  But we
## add a few more convenience functions here.

## Note: we do not do an inheritance here because that would violate
## the Liskov substitution principle: this high-level KeywordTree
## returns 2-tuples (start, end), while the low-level one returns
## 3-tuples.


class KeywordTree(object):
    def __init__(self):
        """Initializes an empty keyword tree."""
        self.__tree = _ahocorasick.KeywordTree();


    def add(self, s):
        """add(string)
        Adds a new keyword to the automaton.  The keyword must be
        nonempty."""
        return self.__tree.add(s)


    def make(self):
        """make()
        Finalizes construction of the automaton.  This must be called
        before doing any searching, and can only be done if at least
        one keyword has been added.  If called before adding at least
        one keyword, we'll raise an AssertionError.
        """
        return self.__tree.make()


    def zerostate(self):
        """zerostate()
        Returns the initial start state of the constructed automaton.
        """
        return self.__tree.zerostate()


    def __search_helper(self, query, startpos, initstate, search_function):
        """Utility function that captures common code between both
        search functions.

        Subtle note: the underlying search functions actually return
        three-tuples: (start_pos, end_pos, last_matching_state).  So
        much of this merely strips off the last element of the tuple.
        """
        # fixme: assert that the initstate is a legal state?
        if initstate == None: initstate = self.zerostate()
        match = search_function(query, startpos, initstate)
        if match:
            return match[:2]
        else:
            return None
                

    def search(self, query, startpos=0, initstate=None):
        """search(query, [startpos=0, initstate=None])

        Searches the query for the leftmost occuring keyword that the
        automaton knows.  If a match is made, returns the 2-tuple
        (startIndex, endIndex).  If no match can be found, returns
        None.

        'initstate' allows one to start the search from an arbitrary
        state in the automaton, and by default, searches start off at
        the initial zerostate() of a tree.
        """
        return self.__search_helper(query, startpos, initstate,
                                    self.__tree.search)


    def search_long(self, query, startpos=0, initstate=None):
        """search_long(query, [startpos=0, initstate=None])

        Searches the query for the longest leftmost occuring keyword
        that the automaton knows.  If a match is made, returns the
        2-tuple (startIndex, endIndex).  If no match can be found,
        returns None.

        'initstate' allows one to start the search from an arbitrary
        state in the automaton, and by default, searches start off at
        the initial zerostate() of a tree.
        """
        return self.__search_helper(query, startpos, initstate,
                                    self.__tree.search_long)


    def chases(self, sourceStream):
        """chases(sourceStream)

        Given an iterator of text blocks, returns an iterator of
        matches, using search().  Each match result is a 2-tuple
        (text_block, (start, end)).
        """
        for block in sourceStream:
            for match in self.findall(block):
                yield (block, match[0:2])


    def chases_long(self, sourceStream):
        """chases_long(sourceStream)

        Given an iterator of text blocks, returns an iterator of
        matches, using search_long().  Each match result is a 2-tuple
        (text_block, (start, end)).
        """
        for block in sourceStream:
            for match in self.findall_long(block):
                yield (block, match[0:2])



    def __findall_helper(self, sourceBlock, allow_overlaps, search_function):
        """Helper function that captures the common logic behind the
        two findall methods."""
        startpos = 0
        startstate = self.zerostate()
        while True:
            match = search_function(sourceBlock, startpos, startstate)
            if not match:
                break
            yield match[0:2]
            startpos = match[1]
            if allow_overlaps:
                startstate = match[2]
            else:
                startstate = self.zerostate()


    def findall(self, sourceBlock, allow_overlaps=0):
        """Returns all the search matches in the source block.

        If allow_overlaps is true, then we allow subsequent matches to
        overlap."""
        return self.__findall_helper(sourceBlock, allow_overlaps,
                                     self.__tree.search)
        

    def findall_long(self, sourceBlock, allow_overlaps=0):
        """Returns all the search matches in the source block.

        If allow_overlaps is true, then we allow subsequent matches to
        overlap.  """
        return self.__findall_helper(sourceBlock, allow_overlaps,
                                     self.__tree.search_long)
