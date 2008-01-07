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

import sys
import os
import logging
import time

# Let's keep this self contained so that it can be easily
# pasted in external sugar service like the datastore.

def get_logs_dir():
    profile = os.environ.get('SUGAR_PROFILE', 'default')
    logs_dir = os.path.join(os.path.expanduser('~'),
                            '.sugar', profile, 'logs')
    return logs_dir

def set_level(level):
    levels = { 'error'   : logging.ERROR,
               'warning' : logging.WARNING,
               'debug'   : logging.DEBUG,
               'info'    : logging.INFO }
    if levels.has_key(level):
        logging.getLogger('').setLevel(levels[level])

def _except_hook(type, value, traceback):
    # Attempt to provide verbose IPython tracebacks.
    # Importing IPython is slow, so we import it lazily.
    try:
        from IPython.ultraTB import AutoFormattedTB
        sys.excepthook = AutoFormattedTB(mode='Verbose', color_scheme='NoColor')
    except ImportError:
        sys.excepthook = sys.__excepthook__

    sys.excepthook(type, value, traceback)
        
def start(log_filename=None):
    logging.basicConfig(level=logging.WARNING,
            format="%(created)f %(levelname)s %(name)s: %(message)s")

    if os.environ.has_key('SUGAR_LOGGER_LEVEL'):
        set_level(os.environ['SUGAR_LOGGER_LEVEL'])

    if log_filename and not sys.stdin.isatty():
        log_path = os.path.join(get_logs_dir(), log_filename + '.log')
        log_file = open(log_path, 'w')

        os.dup2(log_file.fileno(), sys.stdout.fileno())
        os.dup2(log_file.fileno(), sys.stderr.fileno())

    sys.excepthook = _except_hook

