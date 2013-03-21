# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 10:12:56 2013

@author: dtremoui
"""
import os

from matplotlib.pyplot import figure
import h5py

from .storm import Storm
from .istorm_view import View
from ..thunder.importers.tools import plug_dict

from ..lightning.simple_plots import TLPOverlayWithLeakEvol


class InteractiveStorm(object):

    def __init__(self, storm=None):
        if storm is None:
            #TODO create a tmp file if None
            #self.storm = Storm()
            raise NotImplementedError
        elif type(storm) is str:
            if not os.path.exists(storm):
                h5py.File(storm, 'w')
            self.storm = Storm(storm)
        else:
            self.storm = storm

        for importer_name in plug_dict.keys():
            importer = plug_dict[importer_name]()
            setattr(self, 'import_' + importer_name,
                    self._gen_import_data(importer))

        self.overlay_tlp_fig = None

    def _gen_import_data(self, importer):
        def import_func(filename, comments=""):
            self.storm.append(View(importer.load(filename, comments,
                                                 h5file=self.storm._h5file)))
        return import_func

    @property
    def filename(self):
        return self.storm._h5file.filename

    def __repr__(self):
        if len(self.storm) == 0:
            return "Empty"
        showtxt = "Storm name: %s\n" % self.filename
        for idx, elem in enumerate(self.storm):
            showtxt += "%s : %s" % (idx, elem)
        return showtxt

    def overlay_raw_tlp(self, index_list, experiment_list=()):
        if self.overlay_tlp_fig is None:
            self.overlay_tlp_fig = TLPOverlayWithLeakEvol(figure())

        def handle_close(evt):
            self.overlay_tlp_fig = None
        self.overlay_tlp_fig.figure.canvas.mpl_connect('close_event',
                                                       handle_close)
        self.storm.overlay_raw_tlp(self.overlay_tlp_fig,
                                   index_list, experiment_list)
