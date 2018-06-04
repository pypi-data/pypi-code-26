from __future__ import absolute_import, division, print_function

import abc
import torch.nn as nn
import torch.utils.hooks as hooks
from collections import OrderedDict


class Attack(object):
    r"""Base class for all attack classes.
    Your models should also subclass this class.
    ``Attack`` allows pre and post hooks to provide a room for additional
    processes.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        self._pre_hooks = OrderedDict()
        self._hooks = OrderedDict()
        self.targeted = True
        self._cuda = False

    def __call__(self, *input, **kwargs):
        for hook in self._pre_hooks.values():
            hook(self, input)
        result = self.generate(*input, **kwargs)
        for hook in self._hooks.values():
            hook_result = hook(self, input, result)
            if hook_result is not None:
                raise RuntimeError("a post hook should always return None")
        return result

    def register_pre_hook(self, hook):
        r"""Registers a pre-hook on the module.
        The hook will be called every time before :func:`generate` is invoked.
        It should have the following signature::
            hook(module, input) -> None
        The hook should not modify the input.
        Returns:
            :class:`torch.utils.hooks.RemovableHandle`:
                a handle that can be used to remove the added hook by calling
                ``handle.remove()``
        """
        handle = hooks.RemovableHandle(self._pre_hooks)
        self._pre_hooks[handle.id] = hook
        return handle

    def register_hook(self, hook):
        r"""Registers a hook on the module.
        The hook will be called every time after :func:`generate` has
        computed an output.
        It should have the following signature::
            hook(module, input, output) -> None
        The hook should not modify the input or output.
        Returns:
            :class:`torch.utils.hooks.RemovableHandle`:
                a handle that can be used to remove the added hook by calling
                ``handle.remove()``
        """
        handle = hooks.RemovableHandle(self._hooks)
        self._hooks[handle.id] = hook
        return handle

    @abc.abstractmethod
    def generate(self, *input):
        r"""Defines the generative computation performed at every call.
        Should be overriden by all subclasses.
        .. note::
            Although the recipe for adversarial example generation needs to be
            defined within this function, one should call the :class:`Attack`
            instance afterwards instead of this since the former takes care of
            running the registered hooks while the latter silently ignores
            them.
        """
        raise NotImplementedError

    def cuda(self):
        r""" Allow the use of CUDA in training. """
        self._cuda = True
        return self

    def __repr__(self):
        tmpstr = self.__class__.__name__ + '\n'
        return tmpstr
