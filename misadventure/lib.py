import inspect
import re

try:
    from shutil import get_terminal_size
except ImportError:
    try:
        from backports.shutil_get_terminal_size import get_terminal_size
    except ImportError:
        def get_terminal_size(fallback=(80, 24)):
            return fallback

try:
    import readline
except ImportError:
    pass

current_context = None

#: The separator that defines the context hierarchy
CONTEXT_SEP = '.'


class InvalidCommand(Exception):
    """A command is not defined correctly."""


class InvalidDirection(Exception):
    """The direction specified was not pre-declared."""


class InvalidEntry(Exception):
    """The entry specified could not be used in a Collection"""


class InvalidState(Exception):
    """The state name specified does not exist"""


class Collection:
    """Similar to a bag except it is strictly used to store non-duplicate string values"""

    def __init__(self):
        self._collection = []

    def add(self, *args):
        for arg in args:
            if not isinstance(arg, str):
                raise InvalidEntry('%r is not a string')
            if arg.lower() not in self._collection:
                self._collection.append(arg)
            else:
                raise InvalidEntry('%r already exists in the Collection, cannot add duplicates')

    def remove(self, *args):
        for arg in args:
            if arg.lower() in self._collection:
                try:
                    index = self._collection.index(arg)
                except ValueError:
                    raise InvalidEntry('%r was not found in the Collection')

    def __str__(self):
        return ', '.join(val for val in self._collection)

    def __int__(self):
        return len(self._collection)


def set_context(new_context):
    """Set current context.

    Set the context to `None` to clear the context.

    """
    global current_context
    _validate_context(new_context)
    current_context = new_context


def get_context():
    """Get the current command context."""
    return current_context


def _validate_context(context):
    """Raise an exception if the given context is invalid."""
    if context is None:
        return

    err = []
    if not context:
        err.append('be empty')
    if context.startswith(CONTEXT_SEP):
        err.append('start with {sep}')
    if context.endswith(CONTEXT_SEP):
        err.append('end with {sep}')
    if CONTEXT_SEP * 2 in context:
        err.append('contain {sep}{sep}')
    if err:
        if len(err) > 1:
            msg = ' or '.join([', '.join(err[:-1]), err[-1]])
        else:
            msg = err[0]
        msg = 'Context {ctx!r} may not ' + msg
        raise ValueError(msg.format(sep=CONTEXT_SEP, ctx=context))


def _match_context(context, active_context):
    """Return True if `context` is within `active_context`.

    adventurelib offers a hierarchical system of contexts defined with a
    dotted-string notation.

    A context matches if the active context is "within" the pattern's context.

    For example:

    * ``ham.spam`` is within ``ham.spam``
    * ``ham.spam`` is within ``ham``
    * ``ham.spam`` is within ``None``.
    * ``ham.spam`` is not within ``ham.spam.eggs``
    * ``ham.spam`` is not within ``spam`` or ``eggs``
    * ``None`` is within ``None`` and nothing else.

    """
    if context is None:
        # If command has no context, it always matches
        return True

    if active_context is None:
        # If the command has a context, and we don't, no match
        return False

    # The active_context matches if it starts with context and is followed by
    # the end of the string or the separator
    clen = len(context)
    return (
            active_context.startswith(context) and
            active_context[clen:clen + len(CONTEXT_SEP)] in ('', CONTEXT_SEP)
    )


class Placeholder:
    """Match a word in a command string."""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name.upper()


def _register(command, func, context=None, kwargs={}):
    """Register func as a handler for the given command."""
    pattern = Pattern(command, context)
    sig = inspect.signature(func)
    func_argnames = set(sig.parameters)
    when_argnames = set(pattern.argnames) | set(kwargs.keys())
    if func_argnames != when_argnames:
        raise InvalidCommand(
            'The function %s%s has the wrong signature for @when(%r)' % (
                func.__name__, sig, command
            ) + '\n\nThe function arguments should be (%s)' % (
                ', '.join(pattern.argnames + list(kwargs.keys()))
            )
        )

    commands.append((pattern, func, kwargs))


class Pattern:
    """A pattern for matching a command.

    Patterns are defined with a string like 'take ITEM' which corresponds to
    matching 'take' exactly followed by capturing one or more words as the
    group named 'item'.
    """

    def __init__(self, pattern, context=None):
        self.orig_pattern = pattern
        _validate_context(context)
        self.pattern_context = context
        words = pattern.split()
        match = []
        argnames = []
        self.placeholders = 0
        for w in words:
            if not w.isalpha():
                raise InvalidCommand(
                    'Invalid command %r' % pattern +
                    'Commands may consist of letters only.'
                )
            if w.isupper():
                arg = w.lower()
                if arg in argnames:
                    raise InvalidCommand(
                        'Invalid command %r' % pattern +
                        ' Identifiers may only be used once'
                    )
                argnames.append(arg)
                match.append(Placeholder(arg))
                self.placeholders += 1
            elif w.islower():
                match.append(w)
            else:
                raise InvalidCommand(
                    'Invalid command %r' % pattern +
                    '\n\nWords in commands must either be in lowercase or ' +
                    'capitals, not a mix.'
                )
        self.argnames = argnames
        self.prefix = []
        for w in match:
            if isinstance(w, Placeholder):
                break
            self.prefix.append(w)
        self.pattern = match[len(self.prefix):]
        self.fixed = len(self.pattern) - self.placeholders

    def __repr__(self):
        ctx = ''
        if self.pattern_context:
            ctx = ', context=%r' % self.pattern_context
        return '%s(%r%s)' % (
            type(self).__name__,
            self.orig_pattern,
            ctx
        )

    @staticmethod
    def word_combinations(have, placeholders):
        """Iterate over possible assignments of words in have to placeholders.

        `have` is the number of words to allocate and `placeholders` is the
        number of placeholders that those could be distributed to.

        Return an iterable of tuples of integers; the length of each tuple
        will match `placeholders`.

        """
        if have < placeholders:
            return
        if have == placeholders:
            yield (1,) * placeholders
            return
        if placeholders == 1:
            yield (have,)
            return

        # Greedy - start by taking everything
        other_groups = placeholders - 1
        take = have - other_groups
        while take > 0:
            remain = have - take
            if have >= placeholders - 1:
                combos = Pattern.word_combinations(remain, other_groups)
                for buckets in combos:
                    yield (take,) + tuple(buckets)
            take -= 1  # backtrack

    def is_active(self):
        """Return True if a command is active in the current context."""
        return _match_context(self.pattern_context, current_context)

    def ctx_order(self):
        """Return an integer indicating how nested the context is."""
        if not self.pattern_context:
            return 0
        return self.pattern_context.count(CONTEXT_SEP) + 1

    def match(self, input_words):
        """Match a given list of input words against this pattern.

        Return a dict of captured groups if the pattern matches, or None if
        the pattern does not match.

        """
        global current_context

        if len(input_words) < len(self.argnames):
            return None

        if input_words[:len(self.prefix)] != self.prefix:
            return None

        input_words = input_words[len(self.prefix):]

        if not input_words and not self.pattern:
            return {}
        if bool(input_words) != bool(self.pattern):
            return None

        have = len(input_words) - self.fixed

        for combo in self.word_combinations(have, self.placeholders):
            matches = {}
            take = iter(combo)
            inp = iter(input_words)
            try:
                for cword in self.pattern:
                    if isinstance(cword, Placeholder):
                        count = next(take)
                        ws = []
                        for _ in range(count):
                            ws.append(next(inp))
                        matches[cword.name] = ws
                    else:
                        word = next(inp)
                        if cword != word:
                            break
                else:
                    return {k: ' '.join(v) for k, v in matches.items()}
            except StopIteration:
                continue
        return None


def prompt():
    """Called to get the prompt text."""
    return '> '


def no_command_matches(command):
    """Called when a command is not understood."""
    print("I don't understand '%s'." % command)


def when(command, context=None, **kwargs):
    """Decorator for command functions."""

    def dec(func):
        _register(command, func, context, kwargs)
        return func

    return dec


def help():
    """Print a list of the commands you can give."""
    print('Here is a list of the commands you can give:')
    cmds = sorted(c.orig_pattern for c, _, _ in commands if c.is_active())
    for c in cmds:
        print(c)


def _available_commands():
    """Return the list of available commands in the current context.

    The order will be the order in which they should be considered, which
    corresponds to how deeply nested the context is.

    """
    available_commands = []
    for c in commands:
        pattern = c[0]
        if pattern.is_active():
            available_commands.append(c)
    available_commands.sort(
        key=lambda c: c[0].ctx_order(),
        reverse=True,
    )
    return available_commands


def _handle_command(cmd):
    """Handle a command typed by the user."""
    ws = cmd.lower().split()

    for pattern, func, kwargs in _available_commands():
        args = kwargs.copy()
        matches = pattern.match(ws)
        if matches is not None:
            args.update(matches)
            func(**args)
            break
    else:
        no_command_matches(cmd)
    print()


def start(help=True):
    """Run the game."""
    if help:
        # Ugly, but we want to keep the arguments consistent
        help = globals()['help']
        qmark = Pattern('help')
        qmark.prefix = ['?']
        qmark.orig_pattern = '?'
        commands.insert(0, (Pattern('help'), help, {}))
        commands.insert(0, (qmark, help, {}))
    while True:
        try:
            cmd = input(prompt()).strip()
        except EOFError:
            print()
            break

        if not cmd:
            continue

        _handle_command(cmd)


def say(msg):
    """Print a message.

    Unlike print(), this deals with de-denting and wrapping of text to fit
    within the width of the terminal.

    Paragraphs separated by blank lines in the input will be wrapped
    separately.

    """
    msg = str(msg)
    msg = re.sub(r'^[ \t]*(.*?)[ \t]*$', r'\1', msg, flags=re.M)
    width = get_terminal_size()[0]
    paragraphs = re.split(r'\n(?:[ \t]*\n)', msg)
    formatted = (textwrap.fill(p.strip(), width=width) for p in paragraphs)
    print('\n\n'.join(formatted))


commands = [
    (Pattern('quit'), sys.exit, {}),  # quit command is built-in
]
