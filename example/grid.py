# -*- coding: utf-8 -*-

import numpy as np
import wx
import wx.grid as gridlib
import os.path, sys

sys.path.append(os.path.split(os.path.dirname(__file__))[0])
from mywxwidgets.grid import gridnumpy, gridlist


class Main(wx.Frame):

    def __init__(self):
        super().__init__(None, title='测试', size=(600, 400))
        self.grid_l = gridnumpy.GridWithHeader(self, (10, 10))
        self.grid_l.SetHeaderLabels(['a'])
        self.grid_r = gridlist.GridWithHeader(self, (10, 10))
        self.grid_r.SetHeaderLabels(['b'])

        lab_l = wx.StaticText(self, label='left')
        self.btn1_l = wx.Button(self, label='set table')
        self.btn1_l.Bind(wx.EVT_BUTTON, self._on_set_l)
        self.btn2_l = wx.Button(self, label='print table')
        self.btn2_l.Bind(wx.EVT_BUTTON, self._on_print_l)

        lab_r = wx.StaticText(self, label='right')
        self.btn1_r = wx.Button(self, label='set table')
        self.btn1_r.Bind(wx.EVT_BUTTON, self._on_set_r)
        self.btn2_r = wx.Button(self, label='print table')
        self.btn2_r.Bind(wx.EVT_BUTTON, self._on_print_r)

        layout_l = wx.BoxSizer(wx.VERTICAL)
        layout_l.Add(lab_l, 0, wx.EXPAND | wx.ALL, 5)
        layout_l.Add(self.grid_l, 1, wx.EXPAND | wx.ALL, 5)
        layout_l.Add(self.btn1_l, 0, wx.EXPAND | wx.ALL, 5)
        layout_l.Add(self.btn2_l, 0, wx.EXPAND | wx.ALL, 5)
        layout_r = wx.BoxSizer(wx.VERTICAL)
        layout_r.Add(lab_r, 0, wx.EXPAND | wx.ALL, 5)
        layout_r.Add(self.grid_r, 1, wx.EXPAND | wx.ALL, 5)
        layout_r.Add(self.btn1_r, 0, wx.EXPAND | wx.ALL, 5)
        layout_r.Add(self.btn2_r, 0, wx.EXPAND | wx.ALL, 5)
        layout = wx.BoxSizer(wx.HORIZONTAL)
        layout.Add(layout_l, 1, wx.EXPAND | wx.ALL, 5)
        layout.Add(layout_r, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(layout)
        self.Center()

    def _on_set_l(self, event):
        self.grid_l.SetSubject(np.random.rand(10, 10).round(3))
        self.grid_l.SetHeader([[f'L{i}' for i in range(10)]])

    def _on_print_l(self, event):
        print('-' * 10)
        print('header:')
        print(self.grid_l.header.dataBase.data)
        print('subject:')
        print(self.grid_l.subject.dataBase.data)

    def _on_set_r(self, event):
        self.grid_r.SetSubject(np.random.rand(10, 10).round(3))
        self.grid_r.SetHeader([[f'R{i}' for i in range(10)]])

    def _on_print_r(self, event):
        print('-' * 10)
        print('header:')
        print(self.grid_r.header.dataBase.data)
        print('subject:')
        print(self.grid_r.subject.dataBase.data)


if __name__ == '__main__':
    app = wx.App()
    frame = Main()
    frame.Show()
    app.MainLoop()
