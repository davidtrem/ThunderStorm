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

"""istorm is an ipython shell for thunderstorm tools
"""

import os, sys
import IPython

def main():
    # hook thunderstorm tree in path
    istrom_dir = os.path.dirname(os.path.realpath(__file__))
    thunderstorm_dir  = os.path.join(istrom_dir, 'thunderstorm')
    sys.path.insert(0, thunderstorm_dir)

    # Change the current directory to the one specified as argument
    # This allow drag and drop start on windows
    if len(sys.argv) == 2:
        os.chdir(sys.argv[1])

    from istormlib.thunder_interface import Load
    from istormlib.istorm_view import View

    init_message = "Welcome in Istorm\n"
    init_message += "Copyright (C) 2010  David Trémouilles\n"
    init_message +="This program comes with ABSOLUTELY NO WARRANTY\n"
    init_message +="This is free software, and you are welcome to redistribute"
    init_message +="it under certain\n"
    init_message +="conditions; read the COPYING* files for details.\n"

    init_message += "Available tester import plugins are:\n"
    for plug_name in Load.plug_list:
        init_message += "\t- " + plug_name + "\n"
    init_message += "Use Load.'tester_plugin_name'(\"datafile\")"
    init_message += "to load a measurement\n"
    init_message += "Enjoy!"
    ipshell = IPython.Shell.IPShellEmbed(banner = init_message,
                                         exit_msg = 'Thanks for using istrom')
    ipshell()


if __name__ == "__main__":
    main()
