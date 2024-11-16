# -*- coding: utf-8 -*-

import numpy as np
import wx
import wx.grid as gridlib
import os.path
import sys

sys.path.append(os.path.split(os.path.dirname(__file__))[0])
import grid


class Main(wx.Frame):

    def __init__(self):
        super().__init__(None, title='测试', size=(400, 400))
        self.grid = GridWithHeader(self, -1, (10, 10))
        self.grid.SetHeaderLabels(['a'])
        self.but = wx.Button(self, label='测试')
        self.but.Bind(wx.EVT_BUTTON, self._on_button)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.but, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

    def _on_button(self, event):
        print('-' * 10)
        print('header:')
        print(self.grid.header.dataBase.data)
        print('subject:')
        print(self.grid.subject.dataBase.data)
