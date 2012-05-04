'''
The idea here is that directories are paths for other directories and
files, files are paths for data (and it would be reasonable to extend
the data into yet other paths/children based on the file type).

Comparison to existing (failed) path modules:
    PathModule -- http://wiki.python.org/moin/PathModule
    AlternativePathModule -- http://wiki.python.org/moin/AlternativePathModule
These modules tend to focus on th

Part of the difficulty is that we are generally dealing with two things:
    * The textual representation of where an object can be found (path)
    * The object itself.
I think that these concepts should be separated, so that manipulations on the
object are distinct from manipulations on the path that happens to resolve to
that object.
'''

#TODO: many instances check for isinstance(..., RelPath).  Because of this,
#       strings passed in are being interpreted automatically as absolute
#       paths, instead of relative.  Is this a problem?  I don't know...  Eg:
# >> os.getcwd()
# '/a/b'
# >> p1 = Directory('/a/b/c/d', 'e')
# >> p1 + '..'
#### if default is to interpret strings as relative paths first:
#   Directory('/a/b/c', 'd')
#### if default is to interpret strings as absolute:
#   Directory('/a/b/c/d/e', 'a')
# I think I prefer to assume relative paths...


import abc
import os
from types import NoneType


# call_list = []
# 
# def string2path(str_path):
#     for fn in call_list:
#         try:
#             return fn(str_path)
#         except SomeSpecificError:
#             pass
# 
# def fs_path(str_path):
#     if os.path.isabs(str_path) and os.path.exists(str_path):
#         if os.path.isdir(str_path):
#             return Directory(*os.path.split(str_path))
#         if os.path.isfile(str_path):
#             return File(*os.path.split(str_path))
#     raise SomeSpecificError
# 
# call_list.append(fs_path)

class Path(object):
    '''
    Abstract base clase for data paths
    '''
    __metaclass__ = abc.ABCMeta
    __slots__ = ('_parent', '_str', '_hierarchy', 'name')

    def __init__(self, parent, name):
        self._parent = None
        self._str = None
        self._hierarchy = None

        self.parent = parent
        self.name = name

    @abc.abstractproperty
    def _factory(self):
        pass

    @property
    def parent(self):
        '''method used to turn a (possibly) textual representation of
        _parent into a Path '''
        return self.get_parent()

    @parent.setter
    def parent(self, val):
        if not isinstance(val, (NoneType, basestring, Path)):
            raise ValueError("Expected string, path, or None")
        self._parent = val

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
        self._hierarchy = ret_val
        return self._hierarchy

    def __repr__(self):
        if self.parent:
            parent = str(self.parent)
        else:
            parent = self.parent

        return "{0.__class__.__name__}({1!r}, {0.name!r})".format(
                self, parent)

    @abc.abstractmethod
    def __str__(self):
        pass
        # try:
        #     return self.join(*(i.name for i in self.hierarchy()))
        # except AttributeError:
        #     return self.name

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

    #TODO: support len(Path) calls?

    def __sub__(self, other):
        '''
        >> p1 = '/abcd/efg/hi/p1'
        >> p2 = 'hi/p1'
        >> p1 - p2
        '/abcd/efg'
        >> p3 = '/abcd'
        >> p1 - p3
        'efg/hi/p1'
        >> p3 - p1
        None  # or '' or RelPath(None, ''), or something else?
        >> p4 = 'gfe/hi/p1'
        >> p1 - p4
        '/abcd/efg/hi/p1'
        >> p1 - '..'
        '/abcd/efg/hi/p1'
        >> p1 - '.'
        '/abcd/efg/hi/p1'
        >> p1 - 1  #TODO: should I implement this?
        '/abcd/efg/hi'
        '''
        if not other:
            return self
        if isinstance(other, RelPath):
            try:
                return self._rsub(other)
            except NotImplementedError:
                try:
                    return self._lsub(other):
                except NotImplementedError:
                    return self
        return self.relpath(other)

    def _rsub(self, other):
        if self.name == other.name:
            try:
                return self.parent._rsub(other.parent)
            except AttributeError:
                return self.parent
        if other.name in (None, '', '.', '..'):
            return self
        raise NotImplementedError

    def _lsub(self, other):
        if self.hierarchy()[0] == other.hierarchy()[0]:
            try:
                return self.parent._lsub(other.parent)
            except AttributeError:
                return self.parent
        if other.name in (None, '', '.', '..'):
            return self
        raise NotImplementedError

    def __add__(self, other):
        return self._factory(str(self), str(other))

    def __and__(self, other):
        for num, i in enumerate(zip(self.hierarchy(), other.hierarchy())):
            #TODO: use '==' (relative) or 'is' (absolute)?...
            # if i[0].relpath(self.base) != i[1].relpath(other.base):
            if i[0] != i[1]:
                if num == 0:
                    # There are no common elements in the hierarchy
                    rv = ''
                else:
                    rv = i[0].parent
                break
        else:
            # Everything is in common
            rv = i[0]
        return rv

    # def __and__(self, other):
    #     rv = list(set(self.hierarchy()) & set(other.hierarchy()))
    #     rv.sort()
    #     return rv[-1]

    def __hash__(self):
        return id(self)

    # @abc.abstractmethod
    # def join(self, *parts):
    #     ''' used to join the parent to the path in its
    #         textual representation '''
    #     pass

    @abc.abstractmethod
    def __iter__(self):
        '''should allow iteration through child objects'''
        pass

    @abc.abstractmethod
    def relpath(self, start):
        '''return a relative path object
        >> p1 = '/abc/de/fghi/jk.l'
        >> p2 = '/abc/de'
        >> p1.relpath(p2)
        RelPath('fghi', 'jk.l')
        >> p1.relpath(None)
        ... #TODO: figure this out!
        >> p1.relpath('')
        ... #TODO: figure this out!
        >> p1.relpath('.')
        ... #TODO: figure this out!
        >> p1.relpath('..')
        ... #TODO: figure this out!
        >> p2.relpath(p1)
        RelPath('../..', '.')
        >> p3 = '/foo/bar'
        >> p1.relpath(p3)
        RelPath('../../abc/de/fghi', 'jk.l')
        >> p1.relpath(RelPath(***))
        ... #TODO: figure this out!
        '''
        if isinstance(start, RelPath):
            raise NotImplementedError


class RelPath(Path):
    '''
    FileSystem relative path?
    More specific relative paths? eg CRelativePath?
    Support '..', '.', etc?
    >> p1 = get_fs_path('/foo/bar/baz')
    >> p2 = p1.relpath(p1.parent)
    >> p2.children
    None
    >> p2.parent
    XXXPath(...)
    >> p2.parent.children
    None
    >> p2.parent.parent
    None
    >> p1 + p2
    OSError: ...
    >> p1 + p1.parent
    NotImplemented: ... # adding requires at least one relative path
    >> p3 = p1.parent.parent + p2
    XXXPath(...)
    >> p1 is p3
    True
    '''
    def __iter__(self):
        # Relative paths don't have children
        yield None

    def __add__(self, other):
        # should this be in Path?
        # if isinstance(other, RelPath):
        # return other.__class__(other.join(self.parent), self.name)
        pass

    def relpath(self, start):
        # Doesn't make sense to get the relative path of a relative path.
        # How would you know if they were the same?  Eg:
        # >> p1 = 'foo/bar/baz'
        # >> p2 = 'foo'
        # How can we know that both 'foo' are the same thing?
        raise NotImplementedError


FS_CACHE = {}
def get_fs_path(*args, **kwargs):
    '''FS Path Factory'''
    full_path = os.path.join(*args)
    if not full_path:
        return None
    if os.path.isdir(full_path):
        path = Directory
    elif os.path.isfile(full_path):
        path = File
    # elif not os.path.isabs(full_path):
    else:
        # don't cache relative paths!
        parent, name = os.path.split(full_path)
        return RelFSPath(parent, name, **kwargs)
        # TODO: return full_path?  None?
        # return None
    full_path = os.path.abspath(full_path)
    parent, name = os.path.split(full_path)
    if name == '':
        parent, name = None, parent

    return FS_CACHE.setdefault(full_path,
            path(parent, name, **kwargs))


class FSPath(Path):
    _factory = staticmethod(get_fs_path)

    def __str__(self):
        if self.parent:
            return os.path.join(str(self.parent), self.name)
        return self.name

    def relpath(self, start):
        rv = super(FSPath, self).relpath(start)
        if isinstance(rv, RelPath):
            return rv
        if start is None:
            return self
        return RelFSPath._factory(str(self), start=str(start))
        # Don't use self._factory here, or it would find the dir and convert it
        # to an absolute path
        # parent, head = os.path.split(os.path.relpath(str(self), str(start)))
        # return RelFSPath(parent, head)

    def get_parent(self):
        if isinstance(self._parent, basestring):
            self._parent = self._factory(self._parent)
        if self._parent is self:
            self._parent = None
        return self._parent


class Directory(FSPath):
    def __iter__(self):
        for sub in os.listdir(str(self)):
            yield self + sub


# TODO: add a hook list based on file extensions, to allow customizing what
#   FilePath returns when you iterate through it

class File(FSPath):
    def __iter__(self):
        with open(str(self)) as in_file:
            for line in in_file:
                yield line


def relpath(*paths, **kwargs):
    #TODO: generalize this and move it to RelPath
    path = os.path.join(*tuple(str(i) for i in paths))
    if kwargs.get('start', ''):
        path = os.path.relpath(path, str(kwargs['start']))
    if not path:
        return None
    if os.path.isabs(path):
        return get_fs_path(path)
    parent, name = os.path.split(path)
    if name == '':
        parent, name = None, parent
    return RelFSPath(parent, name)

class RelFSPath(FSPath, RelPath):
    _factory = staticmethod(relpath)


# def cmppath(p1, p2, cutoff=0.6):
#     pass
# 
# def cmpchildren(p1):
#     pass
# 
# def bestmatch(p1, possibilities, cutoff):
#     if not n >  0:
#         raise ValueError("n must be > 0: %r" % (n,))
#     if not 0.0 <= cutoff <= 1.0:
#         raise ValueError("cutoff must be in [0.0, 1.0]: %r" % (cutoff,))
#     result = []
#     for p2 in possibilities:
#         ratio =cmppath(p1, p2)
#         if ratio >= cutoff:
#             ratio += cmpchildren(p1, p2)
#             ratio /= 2
#             if ratio >= cutoff:
#                 result.append((ratio, p2))
#             
#     # Move the best scorers to head of list
#     result = heapq.nlargest(1, result)
#     # Strip scores for the best n matches
#     return result[0][1]

