#!python -u
# -*- coding: utf-8 -*-
#
"""Archivist storage classes."""
import mmap


class BlockMap:
    """Block."""

    __slots__ = ('_offset', '_size')

    def __init__(self, offset: int, size: int):
        """Initialize."""
        self._offset = offset
        self._size = size

    @property
    def offset(self) -> int:
        """Get offset."""
        return self._offset

    @offset.setter
    def offset(self, value: int):
        """Set offset."""
        self._offset = value

    @property
    def size(self) -> int:
        """Get size."""
        return self._size

    @size.setter
    def size(self, value: int):
        """Set size."""
        self._size = value


class TreeBranch:
    """Branch structure."""

    __slots__ = ('_count', '_left', '_right')

    def __init__(self):
        """Initialize."""
        self._count = 0
        self._left = None
        self._right = None

    @property
    def count(self):
        """Get count."""
        return self._count

    @count.setter
    def count(self, value: int):
        """Set count."""
        self._count = value

    @property
    def left(self):
        """Get left."""
        return self._left

    @left.setter
    def left(self, value):
        """Set left."""
        self._count = value

    @property
    def right(self):
        """Get right."""
        return self._right

    @right.setter
    def right(self, value):
        """Set right."""
        self._right = value


class FileMapRow(TreeBranch):
    """File allocation row record."""

    __slots__ = ('_extern', '_intern', '_id')

    def __init__(self):
        """Initialize."""
        TreeBranch.__init__(self)
        self._extern = BlockMap(0, 0)
        self._intern = BlockMap(0, 0)
        self._id = 0

    @property
    def extern(self):
        """Get extern."""
        return self._extern

    @extern.setter
    def extern(self, value):
        """Set extern."""
        self._extern = value

    @property
    def intern(self):
        """Get intern."""
        return self._intern

    @intern.setter
    def intern(self, value):
        """Set intern."""
        self._intern = value

    @property
    def file_id(self):
        """Get file id."""
        return self._id

    @file_id.setter
    def file_id(self, value):
        """Set file id."""
        self._id = value


class FileMap:
    """File allocation record."""

    __slots__ = ('_top',)

    def __init__(self):
        """Initialize."""

    def __len__(self):
        """Get len."""
        return 0

    def __getitem__(self, key):
        """Get item."""
        return None


class Archivist:
    """Archivist."""

    __slots__ = ('_map',)

    def __init__(self, filepath):
        """Initialize."""
        with open(filepath, 'w+b') as file_handler:
            if not Archivist._raw_size_(file_handler):
                Archivist._add_default_header(file_handler)
            # memory-map the file, size 0 means whole file
            fmap = mmap.mmap(file_handler.fileno(), 0)
            # read content via standard file methods
            print(fmap.readline())  # prints "Hello Python!"
            # read content via slice notation
            print(fmap[:5])  # prints "Hello"
            # update content using slice notation;
            # note that new content must have same size
            fmap[6:] = ' world!\n'
            # ... and read again using standard file methods
            fmap.seek(0)
            print(fmap.readline())  # prints "Hello  world!"
            # close the map
            fmap.close()

    def files(self):
        """Files."""

    @staticmethod
    def _add_default_header(f_h):
        """Adding defaul header to file."""
        f_m = FileMap()
        f_h.write(f_m)

    @staticmethod
    def _raw_size_(f_h):
        pos = f_h.tell()
        f_h.seek(0, 2)
        ret = f_h.tell()
        f_h.seek(pos, 0)
        return ret

    def __len__(self):
        """Get len."""
        return 0

    def __getitem__(self, key):
        """Get item."""
        return None


if __name__ == '__main__':
    import doctest
    from os import unlink
    doctest.testmod()

    ARCHI = Archivist('tmp.tmp')
    unlink('tmp.tmp')
