# -*- coding: utf-8 -*-

"""
    echarts
    ~~~~~~~

    An unofficial Echarts options generator with Python.

    :copyright: (c) 2014 by Hsiaoming Yang <me@lepture.com>.
    :license: MIT, see `MIT <https://opensource.org/licenses/MIT>`_ for more details.
"""

import os
import sys
import json
import logging
import tempfile
import webbrowser
from .option import Base
from .option import Axis, Legend, Series, Tooltip, Toolbox, VisualMap
from .datastructure import *

__version__ = '0.1'
__release__ = '0.1.3'
__author__ = 'Hsiaoming Yang <me@lepture.com>'


class Echart(Base):
    validOptions = ['title', 'legend', 'grid', 'xAxis', 'yAxis', 'polar',
        'radiusAxis', 'angleAxis', 'radar', 'dataZoom', 'visualMap', 'tooltip',
        'axisPointer', 'toolbox', 'brush', 'geo', 'parallel', 'parallelAxis',
        'singleAxis', 'timeline', 'graphic', 'calendar', 'series', 'color',
        'backgroundColor', 'textStyle', 'animation', 'animationThreshold',
        'animationDuration', 'animationEasing', 'animationDelay',
        'animationDurationUpdate', 'animationEasingUpdate',
        'animationDelayUpdate', 'progressive', 'progressiveThreshold',
        'blendMode', 'hoverLayerThreshold', 'useUTC']

    def __init__(self, title, js_path=None, description=None, axis=True,
            **kwargs):
        self.js_path = js_path
        self.title = {
            'text': title,
            'subtext': description,
        }

        self.axis = axis
        if self.axis:
            self.x_axis = []
            self.y_axis = []

        self.series = []
        self.kwargs = kwargs

        self.logger = logging.getLogger(__name__)

    def use(self, obj):
        if isinstance(obj, Axis):
            if obj.position in ('bottom', 'top'):
                self.x_axis.append(obj)
            else:
                self.y_axis.append(obj)
            return self

        if isinstance(obj, Legend):
            self.legend = obj
        elif isinstance(obj, Tooltip):
            self.tooltip = obj
        elif isinstance(obj, Series):
            self.series.append(obj)
        elif isinstance(obj, Toolbox):
            self.toolbox = obj
        elif isinstance(obj, VisualMap):
            self.visualMap = obj
        elif isinstance(obj, dict):
            self.others = obj

        return self

    @property
    def data(self):
        return self.series

    @property
    def json(self):
        """JSON format data."""
        json = {
            'title': self.title,
            'series': list(map(dict, self.series)),
        }

        if self.axis:
            json['xAxis'] = list(map(dict, self.x_axis)) or [{}]
            json['yAxis'] = list(map(dict, self.y_axis)) or [{}]

        if hasattr(self, 'legend'):
            json['legend'] = self.legend.json
        if hasattr(self, 'tooltip'):
            json['tooltip'] = self.tooltip.json
        if hasattr(self, 'toolbox'):
            json['toolbox'] = self.toolbox.json
        if hasattr(self, 'visualMap'):
            json['visualMap'] = self.visualMap.json
        if hasattr(self, 'others'):
            for key in self.others.keys():
                if key in self.validOptions:
                    json[key] = self.others[key]
                else:
                    sys.stderr('Invalid Option: %s' % key)
                    exit(-1)

        json.update(self.kwargs)
        return json

    def _html(self):
        echarts_js_path = 'https://cdnjs.cloudflare.com/ajax/libs/echarts/3.5.4/echarts.min.js'
        if self.js_path:
            echarts_js_path = self.js_path
        with open(os.path.join(os.path.dirname(__file__), 'plot.j2')) as f:
            template = f.read()
            return template.replace('{{ opt }}', json.dumps(self.json, indent=4)
            ).replace('{{echarts_js_path}}', echarts_js_path)

    def plot(self, persist=True):
        """
        Plot into html file

        :param persist: persist output html to disk
        """
        with tempfile.NamedTemporaryFile(suffix='.html',
                delete=not persist) as fobj:
            fobj.write(self._html())
            fobj.flush()
            webbrowser.open('file://' + os.path.realpath(fobj.name))
            persist or raw_input('Press enter for continue')

    def save(self, path, name):
        """
        Save html file into project dir
        :param path: project dir
        :param name: html file name
        """
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + str(name) + ".html", "w") as html_file:
            html_file.write(self._html())