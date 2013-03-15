# -*- coding: utf-8 -*-

# Copyright (C) 2010-2013 Trémouilles David

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

"""
Various utility functions
"""

import matplotlib
from weakref import WeakValueDictionary
from weakref import WeakKeyDictionary

import warnings


class UniversalCursors(object):

    def __init__(self):
        self.all_cursor_orient = WeakKeyDictionary()
        self.all_canvas = WeakValueDictionary()
        self.all_axes = WeakValueDictionary()
        self.backgrounds = {}
        self.visible = True
        self.needclear = False

    def _onmove(self, event):
        for canvas in self.all_canvas.values():
            if not canvas.widgetlock.available(self):
                return
        if event.inaxes is None or not self.visible:
            if self.needclear:
                self._update(event)
                for canvas in self.all_canvas.values():
                    canvas.draw()
                self.needclear = False
            return
        self._update(event)

    def _update(self, event):
        # 1/ Reset background
        for canvas in self.all_canvas.values():
            canvas.restore_region(self.backgrounds[id(canvas)])
        # 2/ update cursors
        for cursors in self.all_cursor_orient.keys():
            orient = self.all_cursor_orient[cursors]
            if (event.inaxes in [line.get_axes() for line in cursors]
                    and self.visible):
                visible = True
                self.needclear = True
            else:
                visible = False
            for line in cursors:
                if orient == 'vertical':
                    line.set_xdata((event.xdata, event.xdata))
                if orient == 'horizontal':
                    line.set_ydata((event.ydata, event.ydata))
                line.set_visible(visible)
                ax = line.get_axes()
                ax.draw_artist(line)
        # 3/ update canvas
        for canvas in self.all_canvas.values():
            canvas.blit(canvas.figure.bbox)

    def _clear(self, event):
        """clear the cursor"""
        self.backgrounds = {}
        for canvas in self.all_canvas.values():
            self.backgrounds[id(canvas)] = (
                canvas.copy_from_bbox(canvas.figure.bbox))
        for cursor in self.all_cursor_orient.keys():
            for line in cursor:
                line.set_visible(False)

    def add_cursor(self, axes=(), orient='vertical', **lineprops):
        class CursorList(list):
            def __hash__(self):
                return hash(tuple(self))
        cursors = CursorList()  # Required to keep weakref
        for ax in axes:
            self.all_axes[id(ax)] = ax
            ax_canvas = ax.get_figure().canvas
            if ax_canvas not in self.all_canvas.values():
                if not ax_canvas.supports_blit:
                    warnings.warn("Must use canvas that support blit")
                    return
                self.all_canvas[id(ax_canvas)] = ax_canvas
                ax_canvas.mpl_connect('motion_notify_event', self._onmove)
                ax_canvas.mpl_connect('draw_event', self._clear)
            if orient == 'vertical':
                line = ax.axvline(ax.get_xbound()[0], visible=False,
                                  animated=True, **lineprops)
            if orient == 'horizontal':
                line = ax.axhline(ax.get_ybound()[0], visible=False,
                                  animated=True, **lineprops)
            cursors.append(line)
        self.all_cursor_orient[cursors] = orient
        return cursors


def autoscale_visible_lines(axs):
    """
    Function to autoscale only on visible lines.
    """
    mplt_ver = [int(elem) for elem in matplotlib.__version__.split('.')[0:2]]
    ignore = True
    for line in (axs.lines):
        if not line.get_visible():
            continue  # jump to next line if this one is not visible
        if mplt_ver[0] == 0 and mplt_ver[1] < 98:
            axs.dataLim.update_numerix(line.get_xdata(),
                                       line.get_ydata(),
                                       ignore)
        else:
            axs.dataLim.update_from_data_xy(line.get_xydata(),
                                            ignore)
        ignore = False
    axs.autoscale_view()
    return None


def neg_bool_list(a_list):
    return [not elem for elem in a_list]
