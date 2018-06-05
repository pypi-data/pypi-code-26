#-- powertools.click

''' extension for Click

    add support for command groups written in the style of a generator context manager
    use @subcommand_manager decorator to mark a generator function
    yield an object to be passed to subcommands as ctx.obj
    receive from yield the (args, kwargs) passed to the group's result callback

    add support for multiple names for a command -- automatic aliasing.

    add support for concise ANSI color tokens in help files,
        and colorize default output
'''


from .logging import AutoLogger
log = AutoLogger()

from . import term
from .print import pprint

import click
from click import *

import inspect
from types import GeneratorType

#----------------------------------------------------------------------------------------------#

class Context(click.Context):
    '''  '''

    def invoke(*args, cmd=None, **kwargs):
        """Invokes a command callback in exactly the way it expects.  There
        are two ways to invoke this method:

        1.  the first argument can be a callback and all other arguments and
            keyword arguments are forwarded directly to the function.
        2.  the first argument is a click command object.  In that case all
            arguments are forwarded as well but proper click parameters
            (options and click arguments) must be keyword arguments and Click
            will fill in defaults.

        Note that before Click 3.2 keyword arguments were not properly filled
        in against the intention of this code and no context was created.  For
        more information about this change and why it was done in a bugfix
        release see :ref:`upgrade-to-3.2`.
        """
        self, callback = args[:2]
        ctx = self

        # It's also possible to invoke another command which might or
        # might not have a callback.  In that case we also fill
        # in defaults and make a new context for this command.
        if isinstance(callback, Command):
            # log.info('is Command')
            other_cmd = callback
            callback = other_cmd.callback
            ctx = Context(other_cmd, info_name=other_cmd.name, parent=self)
            if callback is None:
                raise TypeError('The given command does not have a '
                                'callback that can be invoked.')

            for param in other_cmd.params:
                if param.name not in kwargs and param.expose_value:
                    kwargs[param.name] = param.get_default(ctx)

        args = args[2:]
        with click.core.augment_usage_errors(self):
            with ctx:
                # log.info('running callback ', term.cyan(callback), ' cmd=', cmd)
                if hasattr(cmd, '__is_subcommand_manager__'):
                    # log.info(term.cyan('IS SUBCOMMAND MANAGER '))
                    real_callback   = cmd.callback(*args, **kwargs)
                    result          = next(real_callback)
                    # log.info(self.obj)
                    if result is not None:
                        self.obj = result
                    def process_teardown(*a, **kw):
                        try:
                            real_callback.send(a)
                        except StopIteration as e:
                            return e.value
                    cmd.result_callback = process_teardown
                    return result

                return callback(*args, **kwargs)


#----------------------------------------------------------------------------------------------#

class Command(click.Command):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.real_callback = None

    def __call__(self, *args, **kwargs):
        """Alias for :meth:`main`."""
        # log.info(term.pink('CALL'))
        return self.main(*args, **kwargs)

    def make_context(self, info_name, args, parent=None, **extra):
        """This function when given an info name and arguments will kick
        off the parsing and create a new :class:`Context`.  It does not
        invoke the actual command callback though.

        :param info_name: the info name for this invokation.  Generally this
                          is the most descriptive name for the script or
                          command.  For the toplevel script it's usually
                          the name of the script, for commands below it it's
                          the name of the script.
        :param args: the arguments to parse as list of strings.
        :param parent: the parent context if available.
        :param extra: extra keyword arguments forwarded to the context
                      constructor.
        """
        # log.info(term.blue('MAKE CONTEXT'))
        for key, value in click._compat.iteritems(self.context_settings):
            if key not in extra:
                extra[key] = value
        ctx = Context(self, info_name=info_name, parent=parent, **extra)
        with ctx.scope(cleanup=False):
            self.parse_args(ctx, args)
        return ctx


    def invoke(self, ctx):
        """Given a context, this invokes the attached callback (if it exists)
        in the right way.
        """
        if self.callback is not None:
            # log.info('Command ', type(self.callback), ' ', self.callback)
            # pprint(dir(self.callback))
            return ctx.invoke(self.callback, cmd=self, **ctx.params)


#----------------------------------------------------------------------------------------------#

class Group(click.Group, Command):
    ''' group with subcommand order relying on python 3.6 dicts '''

    def list_commands(self, ctx):   return self.commands

    def group(self, *args, **kwargs):
        """A shortcut decorator for declaring and attaching a group to
        the group.  This takes the same arguments as :func:`group` but
        immediately registers the created command with this instance by
        calling into :meth:`add_command`.
        """
        def decorator(f):
            cmd = group( *args, **kwargs )( f )
            self.add_command(cmd)
            return cmd
        return decorator

    def invoke(self, ctx):
        # log.info('begin ', self.callback)
        # assert False

        def _process_result(value):
            # log.info('process_result')
            if self.result_callback is not None:
                # log.info('result_callback not None ', self.result_callback)
                value = ctx.invoke(self.result_callback, value,
                                   **ctx.params)
            return value

        if not ctx.protected_args:
            # If we are invoked without command the chain flag controls
            # how this happens.  If we are not in chain mode, the return
            # value here is the return value of the command.
            # If however we are in chain mode, the return value is the
            # return value of the result processor invoked with an empty
            # list (which means that no subcommand actually was executed).
            if self.invoke_without_command:
                if not self.chain:
                    # log.info('not chain')
                    return Command.invoke(self, ctx)
                with ctx:
                    # log.info('chain')
                    Command.invoke(self, ctx)
                    return _process_result([])
            ctx.fail('Missing command.')


        # Fetch args back out
        # log.info('fetch args')
        args = ctx.protected_args + ctx.args
        ctx.args = []
        ctx.protected_args = []

        # If we're not in chain mode, we only allow the invocation of a
        # single command but we also inform the current context about the
        # name of the command to invoke.
        if not self.chain:
            # Make sure the context is entered so we do not clean up
            # resources until the result processor has worked.
            with ctx:
                # log.info('protected not chain')
                cmd_name, cmd, args = self.resolve_command(ctx, args)
                ctx.invoked_subcommand = cmd_name
                Command.invoke(self, ctx)
                sub_ctx = cmd.make_context(cmd_name, args, parent=ctx)
                # log.info(term.green('make context '), sub_ctx)
                with sub_ctx:
                    return _process_result(sub_ctx.command.invoke(sub_ctx))

        # In chain mode we create the contexts step by step, but after the
        # base command has been invoked.  Because at that point we do not
        # know the subcommands yet, the invoked subcommand attribute is
        # set to ``*`` to inform the command that subcommands are executed
        # but nothing else.
        with ctx:
            # log.info('protected chain')
            ctx.invoked_subcommand = args and '*' or None
            click.Command.invoke(self, ctx)

            # Otherwise we make every single context and invoke them in a
            # chain.  In that case the return value to the result processor
            # is the list of all invoked subcommand's results.
            contexts = []
            while args:
                cmd_name, cmd, args = self.resolve_command(ctx, args)
                sub_ctx = cmd.make_context(cmd_name, args, parent=ctx,
                                           allow_extra_args=True,
                                           allow_interspersed_args=False)
                contexts.append(sub_ctx)
                args, sub_ctx.args = sub_ctx.args, []

            rv = []
            for sub_ctx in contexts:
                with sub_ctx:
                    rv.append(sub_ctx.command.invoke(sub_ctx))
            return _process_result(rv)



#----------------------------------------------------------------------------------------------#

# todo: color codes in doc strings need to be parsed by click. how shall I hook into that?

def _make_command(f, name, attrs, cls):
    if isinstance(f, click.Command):
        raise TypeError('Attempted to convert a callback into a '
                        'command twice.')
    try:
        params = f.__click_params__
        params.reverse()
        del f.__click_params__
    except AttributeError:
        params = []
    help = attrs.get('help')
    if help is None:
        help = inspect.getdoc(f)
        if isinstance(help, bytes):
            help = help.decode('utf-8')
    else:
        help = inspect.cleandoc(help)
    attrs['help'] = help
    click._unicodefun._check_for_unicode_literals()
    return cls(name=name or f.__name__.lower(),
               callback=f, params=params, **attrs)


def command( name=None, cls=None, **kwargs ):
    if cls is None:
        cls = click.Command
    def decorator(f):
        cmd = _make_command(f, name, kwargs, cls)
        cmd.__doc__ = f.__doc__
        if hasattr(f, '__is_subcommand_manager__'):
            cmd.__is_subcommand_manager__ = True
        return cmd
    return decorator


def group( *args, **kwargs ):
    kwargs.setdefault('cls', Group)
    return command( *args, **kwargs )


def contextmanager( f ):
    if not inspect.isgeneratorfunction(f):
        raise TypeError(
            f'{f} must be a generator function.\n'
            f'Hint: Make sure another decorator is not wrapping your generator.'
        )
    f.__is_subcommand_manager__ = True
    return f


#----------------------------------------------------------------------------------------------#
