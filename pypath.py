'''
The idea here is that directories are paths for other directories and
files, files are paths for data (and it would be reasonable to extend
the data into yet other paths/children based on the file type).

* Need to support both absolute and relative
** are '.' and '..' important to this?
* Need to support all of the os(.path) functionality
** http://docs.python.org/library/filesys.html
** set operators to correspond to filecmp/dircmp classes?
* Also support open() functionality?
'''

import abc
import os
from types import NoneType


class Path(object):
    '''
    Abstract base clase for data paths
    '''
    __metaclass__ = abc.ABCMeta
    __slots__ = ('_parent', '_str', '_hierarchy', 'name', 'base')

    def __init__(self, parent, name, base=None):
        self._parent = None
        self._str = None
        self._hierarchy = None

        self.parent = parent
        self.name = name
        self.base = base

    @property
    def parent(self):
        '''method used to turn a (possibly) textual representation of
        _parent into a Path '''
        return self.get_parent()

    @parent.setter
    def parent(self, val):
        if isinstance(val, (NoneType, basestring, Path)):
            self._parent = val
        else:
            raise ValueError("Expected string, path, or None")

    @abc.abstractmethod
    def get_parent(self):
        pass

    def hierarchy(self):
        if self._hierarchy is not None:
            return self._hierarchy
        try:
            ret_val = list(self.parent.hierarchy())
        except AttributeError:
            ret_val = []
        ret_val.append(self)
        try:
            # TODO: an ordered set would do better here
            new_rv = []
            for i in ret_val:
                for j in self.base.hierarchy():
                    if i is j:
                        break
                else:
                    new_rv.append(i)
        except AttributeError:
            #base is None...
            new_rv = ret_val
        self._hierarchy = new_rv
        return self._hierarchy

    def __repr__(self):
        if self.base is None:
            base = ''
        else:
            base = ', ' + repr(self.base)

        if self.parent is None:
            parent = None
        else:
            parent = str(self.parent)

        return "{0.__class__.__name__}({1!r}, {0.name!r}{2})".format(
                self, parent, base)

    def __str__(self):
        # if self._str is None:
        #     if self.parent is None:
        #         self._str = self.name
        #     else:
        try:
            # return self.join(self.parent.relpath(self.base), self.name)
            return self.join(*(i.name for i in self.hierarchy()))
        except AttributeError:
            return self.name
                # return self.join(str(self.parent).replace(str(self.base), '', 1),
                #         self.name)
        # return self._str

    def raw_str(self):
        try:
            return self.join(self.parent.raw_str(), self.name)
        except AttributeError:
            return self.name

    def __cmp__(self, other):
        return cmp(str(self), str(other))
        # rv = cmp(str(self.parent), str(other.parent))
        # if rv == 0:
        #     rv = cmp(self.name, other.name)
        # return rv

    def __sub__(self, other):
        return str(self).replace(str(other), '', 1)
    # def __sub__(self, other):
    #     return type(self)(self.parent, self.name, other)

    # def __isub__(self, other):
    #     self.base = other
    #     return self

    def __and__(self, other):
        for num, i in enumerate(zip(self.hierarchy(), other.hierarchy())):
            #TODO: use '==' (relative) or 'is' (absolute)?...
            if i[0].relpath(self.base) != i[1].relpath(other.base):
                if num == 0:
                    # There are no common elements in the hierarchy
                    rv = ''
                else:
                    rv = i[0].parent.relpath(self.base)
                break
        else:
            # Everything is in common
            rv = i[0].relpath(self.base)

        return rv

    # def __and__(self, other):
    #     rv = list(set(self.hierarchy()) & set(other.hierarchy()))
    #     rv.sort()
    #     return rv[-1]

    def __hash__(self):
        return id(self)

    @abc.abstractmethod
    def join(self, *parts):
        ''' used to join the parent to the path in its
            textual representation '''
        pass

    @abc.abstractmethod
    def __iter__(self):
        '''should allow iteration through child objects'''
        pass

    @abc.abstractmethod
    def relpath(self, start):
        pass


FS_CACHE = {}
def get_fs_path(*args, **kwargs):
    '''FS Path Factory'''
    full_path = os.path.abspath(os.path.join(*args))
    parent, name = os.path.split(full_path)
    if os.path.isdir(full_path):
        cont = Directory
    elif os.path.isfile(full_path):
        cont = File
    else:
        return None
    if name == '':
        parent, name = None, parent
    return FS_CACHE.setdefault(full_path,
            cont(parent, name, **kwargs))


class FSPath(Path):
    def join(self, *parts):
        return os.path.join(*parts)

    def relpath(self, start):
        if start is None:
            return str(self)
        try:
            return os.path.relpath(str(self), str(start))
        except ValueError:
            return str(self).replace(str(start), '', 1)

    def get_parent(self):
        if isinstance(self._parent, basestring):
            self._parent = get_fs_path(self._parent)
        if self._parent is self:
            self._parent = None
        return self._parent

class Directory(FSPath):
    def __iter__(self):
        for sub in os.listdir(self.raw_str()):
            yield get_fs_path(self.raw_str(), sub)


# TODO: add a hook list based on file extensions, to allow customizing what
#   FilePath returns when you iterate through it

class File(FSPath):
    def __iter__(self):
        # return (i for i in tuple())
        with open(self.raw_str()) as in_file:
            for line in in_file:
                yield line

class RelPath(FSPath):
    def to_abs(self):
        pass


def cmppath(p1, p2, cutoff=0.6):
    pass

def cmpchildren(p1):
    pass

def bestmatch(p1, possibilities, cutoff):
    if not n >  0:
        raise ValueError("n must be > 0: %r" % (n,))
    if not 0.0 <= cutoff <= 1.0:
        raise ValueError("cutoff must be in [0.0, 1.0]: %r" % (cutoff,))
    result = []
    for p2 in possibilities:
        ratio =cmppath(p1, p2)
        if ratio >= cutoff:
            ratio += cmpchildren(p1, p2)
            ratio /= 2
            if ratio >= cutoff:
                result.append((ratio, p2))
            
    # Move the best scorers to head of list
    result = heapq.nlargest(1, result)
    # Strip scores for the best n matches
    return result[0][1]

