#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2010 Trémouilles David

#This file is part of Thunderstorm.
#
#ThunderStrom is free software: you can redistribute it and/or modify
#it under the terms of the GNU Lesser General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#ThunderStorm is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Lesser General Public License for more details.
#
#You should have received a copy of the GNU Lesser General Public License
#along with ThunderStorm.  If not, see <http://www.gnu.org/licenses/>.

"""istorm is a shell for thunderstorm tools
"""

from thunderstorm.istormlib.thunder_interface import Load
from thunderstorm.istormlib.istorm_view import View

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.interactive(True)
from thunderstorm.interact import my_storm

def console(variables):
    import os, sys
    # hook thunderstorm tree in path
    thunderstorm_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, thunderstorm_dir)

    # Change the current directory to the one specified as argument
    # This allow drag and drop start on windows
    if len(sys.argv) == 2:
        os.chdir(sys.argv[1])

    init_message = """Welcome in Istorm
Copyright (C) 2010  David Trémouilles
This program comes with ABSOLUTELY NO WARRANTY
This is free software, and you are welcome to redistribute
it under certain
conditions; read the COPYING* files for details.
Available tester import plugins are:"""
    for plug_name in Load.plug_list:
        init_message += "\t- " + plug_name + "\n"
    init_message += """Use Load.'tester_plugin_name'("datafile")
to load a measurement
Enjoy!
"""
    plt_info = "Using -%s- matplotlib backend" % matplotlib.get_backend()
    try:
        from IPython.Shell import IPShellEmbed
        ipshell = IPShellEmbed(exit_msg='Thanks for using istrom')
        return  (ipshell,
                 init_message + plt_info + " and -IPython shell-")
    except ImportError:
        import code
        import rlcompleter
        import readline
        readline.parse_and_bind("tab: complete")
        print init_message
        shell = code.InteractiveConsole(variables)
        return (shell.interact,
                init_message + plt_info +" and -Interactive Console-")

 
if __name__ == "__main__":
    prompt, message = console(locals())
    prompt(message)
