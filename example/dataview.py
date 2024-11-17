# -*- coding: utf-8 -*-

import wx
import os.path, sys
from typing import Sequence

sys.path.append(os.path.split(os.path.dirname(__file__))[0])
from mywxwidgets.dataview import DataRow, DataViewModel, dv


class Test(wx.Frame):

    def __init__(self, data: Sequence[DataRow]):
        wx.Frame.__init__(self, None, title='test')

        self.dvc = dv.DataViewCtrl(self,
                                   style=dv.DV_SINGLE | dv.DV_VERT_RULES
                                   | dv.DV_HORIZ_RULES | dv.DV_ROW_LINES)
        self.dvc.AppendTextColumn('value0', 0, dv.DATAVIEW_CELL_ACTIVATABLE)
        self.dvc.AppendTextColumn('value1', 1, dv.DATAVIEW_CELL_ACTIVATABLE)
        self.dvc.AppendTextColumn('value2', 2, dv.DATAVIEW_CELL_ACTIVATABLE)
        self.dvc.AppendTextColumn('value3', 3, dv.DATAVIEW_CELL_ACTIVATABLE)

        self.model = DataViewModel(data)
        self.dvc.AssociateModel(self.model)
        self.Centre()
        self.Show()


if __name__ == '__main__':

    def set_v(s):
        return [s + str(i) for i in range(5)]

    drs = [
        DataRow((0, ), set_v('a')),
        DataRow((1, ), set_v('b')),
        DataRow((0, 0), set_v('c')),
        DataRow((2, ), set_v('d')),
        DataRow((1, 0), set_v('e')),
        DataRow((0, 1), set_v('f')),
        DataRow((0, 2), set_v('g')),
        DataRow((0, 1, 0), set_v('h')),
    ]

    app = wx.App()
    Test(drs)
    app.MainLoop()
