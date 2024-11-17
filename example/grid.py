# -*- coding: utf-8 -*-

import numpy as np
import wx
import wx.grid as gridlib
import os.path, sys

sys.path.append(os.path.split(os.path.dirname(__file__))[0])
from mywxwidgets.grid import gridnumpy, gridlist


class Main(wx.Frame):

    def __init__(self):
        super().__init__(None, title='测试', size=(400, 400))
        self.grid = gridnumpy.GridWithHeader(self, (10, 10))
        self.grid.SetHeaderLabels(['a'])

        self.btn1 = wx.Button(self, label='set table')
        self.btn1.Bind(wx.EVT_BUTTON, self._on_set)
        self.btn2 = wx.Button(self, label='print table')
        self.btn2.Bind(wx.EVT_BUTTON, self._on_print)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.btn1, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.btn2, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

    def _on_set(self, event):
        self.grid.SetSubject(np.random.rand(10, 10).round(3))
        self.grid.SetHeader([[f'L{i}' for i in range(10)]])

    def _on_print(self, event):
        print('-' * 10)
        print('header:')
        print(self.grid.header.dataBase.data)
        print('subject:')
        print(self.grid.subject.dataBase.data)


if __name__ == '__main__':
    app = wx.App()
    frame = Main()
    frame.Show()
    app.MainLoop()
