#!/usr/bin/env python

""" OrderedBunch is a subclass of OrderedDict with attribute-style access.

    ordered_un/bunchify provide dictionary conversion; Bunches can also be
    converted via OrderedBunch.to/fromOrderedDict().

    original source:
    https://pypi.python.org/pypi/bunch
"""

import collections as _collections
import textwrap as _textwrap
#import inspect as _inspect


class OrderedBunch(_collections.OrderedDict):
    """ A dictionary that provides attribute-style access.
        A OrderedBunch is a subclass of dict; it supports all the methods a dict does...

        See ordered_unbunchify/OrderedBunch.toOrderedDict, ordered_bunchify/OrderedBunch.fromOrderedDict for notes about conversion.
    """

    _initialized = False

    def __init__(self,*args,**kwarg):
        """ initializes the ordered dict
        """
        # super(OrderedBunch,self).__init__(*args,**kwarg)
        super().__init__(*args,**kwarg)
        self._initialized = True

    def __contains__(self, k):
        try:
            return hasattr(self, k) or dict.__contains__(self, k)
        except:
            return False

    # only called if k not found in normal places
    def __getattr__(self, k):
        """ Gets key if it exists, otherwise throws AttributeError.
        """
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)

    def __setattr__(self, k, v):
        """ Sets attribute k if it exists, otherwise sets key k. A KeyError
            raised by set-item (only likely if you subclass OrderedBunch) will
            propagate as an AttributeError instead.
        """

        if not self._initialized:
            # for OrderedDict initialization
            return object.__setattr__(self, k, v)

        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
            except:
                raise AttributeError(k)
        else:
            object.__setattr__(self, k, v)

    def __delattr__(self, k):
        """ Deletes attribute k if it exists, otherwise deletes key k. A KeyError
            raised by deleting the key--such as when the key is missing--will
            propagate as an AttributeError instead.
        """
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)

    def _repr_pretty_(self,p,cycle):
        """ Pretty print for this class.  Will only trigger in ipython."""
        p.text(_print_recursive(self))

    def __dir__(self):
        """ Overload the tab-complete operation so that it is easier to dynamically explore the bunch.
        """
        return self.keys()


def ordered_bunchify(x,level=0):
    """ Recursively transforms a dictionary into a OrderedBunch via copy.
    """

    speak = False
    if speak: print('*'*(level+1)+' x is:  '+str(x))
    if isinstance(x, dict):
        return OrderedBunch((k,ordered_bunchify(v)) for k,v in x.items())
    elif isinstance(x, list):
        return [ordered_bunchify(y) for y in x]
    elif isinstance(x, tuple):
        return tuple(ordered_bunchify(y) for y in x)
    else:
        return x


def ordered_unbunchify(x):
    """ Recursively converts a OrderedBunch into OrderedDictionaries.
    """
    if isinstance(x,OrderedBunch):
        return _collections.OrderedDict( (k, ordered_unbunchify(v)) for k,v in x.items() )
    else:
        return x


def _print_recursive(xxx):
    """Return string to be used in the formatted printing of OrderedBunch
    objects.
    """
    sss = _print_recursive_main(xxx)
    return sss.strip()


def _print_recursive_main(xxx, depth=0, width=80, plen=0):

    # ToDo - width doesn't currently wrap the entry indentions - it only
    #        controls the printing of the dictionary values or list entries.

    sss = ''
    depmarks = '-' * depth

    if isinstance(xxx,dict):
        # Gen max length of labels to set prefix length
        prelen = max([len(x) for x in xxx.keys()])
        prefix_space = ' ' * plen
        for k,v in xxx.items():
            prefix = prefix_space + depmarks + k + ' ' * (prelen - len(k)) + ' : '
            sss += _print_recursive_work(v,prefix,depth=depth,width_set=width)
    elif isinstance(xxx,(list,tuple)):
        prefix_space = ' ' * plen
        for x in xxx:
            prefix = prefix_space + depmarks + ' '
            sss += _print_recursive_work(x,prefix,depth=depth,width_set=width)
    else:
        prefix_space = ' ' * (plen-depth-1)
        prefix = prefix_space + depmarks + ' '
        sss += _print_recursive_work(xxx,prefix,depth=depth,width_set=width)

    return sss


def _print_recursive_work(x,prefix,depth,width_set):

    wrapper = _textwrap.TextWrapper(initial_indent=prefix,
                                    width=width_set,
                                    replace_whitespace=False,
                                    subsequent_indent=' ' * len(prefix))

    if isinstance(x,dict):
        message = str(type(x)) + '\n'
        message += _print_recursive_main(x,depth=depth+1,plen=len(prefix))
    elif isinstance(x,list):
        message = '[\n'
        message += _print_recursive_main(x,depth=depth+1,plen=len(prefix))
        message += _print_recursive_main(']',depth=depth,plen=len(prefix))
    elif isinstance(x,tuple):
        message = '(\n'
        message += _print_recursive_main(x,depth=depth+1,plen=len(prefix))
        message += _print_recursive_main(')',depth=depth,plen=len(prefix))
    else:
        message = str(x)

    # Handle different message formats:
    # If message contains new lines, just pass those through to print.
    if message.find('\n') != -1:
        return prefix + message.replace('\n', '\n')
                                             # '\n' + ' ' * prelen) + '\n'
    # Else if message is not empty, pass to wrapper.fill
    elif message:
        return wrapper.fill(message) + '\n'
    # Else just pass the empty message along with prefix
    else:
        return prefix + '\n'
