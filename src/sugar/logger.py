# Copyright (C) 2007 Red Hat, Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Logging service setup.

STABLE.
"""

import array
import collections
import errno
import logging
import sys
import os
import repr as repr_
import decorator

# Let's keep this module self contained so that it can be easily
# pasted in external sugar service like the datastore.

# traces function calls, use SUGAR_LOGGER_LEVEL=trace to enable
TRACE = 5
logging.addLevelName(TRACE, 'TRACE')

def get_logs_dir():
    profile = os.environ.get('SUGAR_PROFILE', 'default')
    logs_dir = os.environ.get('SUGAR_LOGS_DIR',
                              os.path.join(os.path.expanduser('~'),
                                           '.sugar', profile, 'logs'))
    return logs_dir

_LEVELS = { 'error'   : logging.ERROR,
            'warning' : logging.WARNING,
            'debug'   : logging.DEBUG,
            'info'    : logging.INFO,
            'trace'   : TRACE,
            'all'     : 0,
}
def set_level(level):
    if level in _LEVELS:
        logging.getLogger('').setLevel(_LEVELS[level])
        return

    try:
        logging.getLogger('').setLevel(int(level))
    except ValueError:
        logging.warning('Invalid log level: %r' % level)


# pylint: disable-msg=E1101,F0401
def _except_hook(exctype, value, traceback):
    # Attempt to provide verbose IPython tracebacks.
    # Importing IPython is slow, so we import it lazily.
    try:
        from IPython.ultraTB import AutoFormattedTB
        sys.excepthook = AutoFormattedTB(mode='Verbose', color_scheme='NoColor')
    except ImportError:
        sys.excepthook = sys.__excepthook__

    sys.excepthook(exctype, value, traceback)

def start(log_filename=None):
    # remove existing handlers, or logging.basicConfig() won't have no effect.
    root_logger = logging.getLogger('')
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    class SafeLogWrapper(object):
        """Small file-like wrapper to gracefully handle ENOSPC errors when
        logging."""

        def __init__(self, stream):
            self._stream = stream

        def write(self, s):
            try:
                self._stream.write(s)
            except IOError, e:
                # gracefully deal w/ disk full
                if e.errno != errno.ENOSPC:
                    raise e

        def flush(self):
            try:
                self._stream.flush()
            except IOError, e:
                # gracefully deal w/ disk full
                if e.errno != errno.ENOSPC:
                    raise e

    logging.basicConfig(level=logging.WARNING,
            format="%(created)f %(levelname)s %(name)s: %(message)s",
                        stream=SafeLogWrapper(sys.stderr))

    if os.environ.has_key('SUGAR_LOGGER_LEVEL'):
        set_level(os.environ['SUGAR_LOGGER_LEVEL'])

    if log_filename:
        try:
            log_path = os.path.join(get_logs_dir(), log_filename + '.log')

            log_fd = os.open(log_path, os.O_WRONLY | os.O_CREAT)
            os.dup2(log_fd, sys.stdout.fileno())
            os.dup2(log_fd, sys.stderr.fileno())
            os.close(log_fd)

            sys.stdout = SafeLogWrapper(sys.stdout)
            sys.stderr = SafeLogWrapper(sys.stderr)
        except OSError, e:
            # if we're out of space, just continue
            if e.errno != errno.ENOSPC:
                raise e

    sys.excepthook = _except_hook


class TraceRepr(repr_.Repr):

    # better handling of subclasses of basic types, e.g. for DBus
    _TYPES = [int, long, bool, tuple, list, array.array, set, frozenset,
        collections.deque, dict, str]
    def repr1(self, x, level):
        for t in self._TYPES:
            if isinstance(x, t):
                return getattr(self, 'repr_'+t.__name__)(x, level)

        return repr_.Repr.repr1(self, x, level)

    def repr_int(self, x, level):
        return repr(x)

    def repr_bool(self, x, level):
        return repr(x)


def trace(logger=None, logger_name=None, skip_args=None, skip_kwargs=None,
    maxsize_list=30, maxsize_dict=30, maxsize_string=300):

    if skip_args is None:
        skip_args = []

    if skip_kwargs is None:
        skip_kwargs = []

    # size-limit repr()
    trace_repr = TraceRepr()
    trace_repr.maxlist = maxsize_list
    trace_repr.maxdict = maxsize_dict
    trace_repr.maxstring = maxsize_string
    trace_repr.maxother = maxsize_string
    trace_logger = logger or logging.getLogger(logger_name)

    def _trace(f, *args, **kwargs):
        # don't do expensive formatting if loglevel TRACE is not enabled
        enabled = trace_logger.isEnabledFor(TRACE)
        if enabled:
            params_formatted = ", ".join(
                [trace_repr.repr(a)
                    for (idx, a) in enumerate(args) if idx not in skip_args] + \
                ['%s=%s' % (k,trace_repr.repr(v))
                    for (k,v) in kwargs.items() if k not in skip_kwargs])

            trace_logger.log(TRACE, "%s(%s) invoked", f.__name__,
                params_formatted)

        try:
            res = f(*args, **kwargs)
        except:
            trace_logger.exception("Exception occured in %s", f.__name__)
            raise

        if enabled:
            trace_logger.log(TRACE, "%s(%s) returned %s", f.__name__,
                params_formatted, trace_repr.repr(res))

        return res

    return decorator.decorator(_trace)


