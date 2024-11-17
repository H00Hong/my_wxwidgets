# -*- coding: utf-8 -*-
"""
自定义Grid

Grid
    基于 list[list] 的数据类型
    鼠标右键菜单和键盘快捷键--复制、粘贴、剪切、插入、删除、清除

GridWithHeader
    带表头的 Grid  两个 Grid 的组合
"""
from typing import Union, Sequence, List, Tuple

import wx
import wx.grid as gridlib

from .GridBase import DataBase, GridBase, build_empty, FONT0, FONT1


def list_transpose(x: List[list]):
    return [list(i) for i in zip(*x)]


class DataBaseList(DataBase):
    """
    
    """

    def __init__(self,
                 data: Union[List[list], list, Tuple[int, ...], None] = None,
                 rowlabels: Union[List[str], None] = None,
                 collabels: Union[List[str], None] = None) -> None:
        DataBase.__init__(self)
        if data is None:
            data = (3, 3)
        if isinstance(data, tuple):
            data = build_empty(*data)
        self.data = self.SetDataFunc(data)
        if rowlabels is None:
            self.rowlabels = None
        else:
            self.SetRowLabels(rowlabels)
        if collabels is None:
            self.collabels = None
        else:
            self.SetColLabels(collabels)

    def GetNumberRows(self) -> int:
        return len(self.data)

    def GetNumberCols(self) -> int:
        return len(self.data[0])

    def SetDataFunc(self, lst) -> List[list]:
        if not isinstance(lst, list):
            raise TypeError('DataBaseList\'s data type must be list')
        b = [isinstance(i, list) for i in lst]
        if all(b):
            if len(set([len(i) for i in lst])) != 1:
                raise ValueError('')
            return lst
        elif all([not i for i in b]):
            return [lst]
        else:
            raise TypeError('DataBaseList\'s data type must be list[list]')

    def GetValueFunc(self, data: List[list], row: int, col: int):
        return str(data[row][col])

    def SetValueFunc(self, data: List[list], row: int, col: int, value) -> None:
        data[row][col] = value

    def DeleteRowsFunc(self, data: List[list], pos: int, numRows: int = 1):
        return data[:pos] + data[pos + numRows:]

    def DeleteColsFunc(self, data: List[list], pos: int, numCols: int = 1):
        dat = list_transpose(data)
        dat_ = dat[:pos] + dat[pos + numCols:]
        return list_transpose(dat_)

    def AppendRowsFunc(self, data: List[list], numRows: int = 1):
        ncols = len(data[0])
        return data + build_empty(numRows, ncols)

    def AppendColsFunc(self, data: List[list], numCols: int = 1):
        nrows = len(data)
        lst = build_empty(numCols, nrows)
        dat = list_transpose(data)
        return list_transpose(dat + lst)

    def InsertRowsFunc(self, data: List[list], pos: int, numRows: int = 1):
        ncols = len(data[0])
        lst = build_empty(numRows, ncols)
        return data[:pos] + lst + data[pos:]

    def InsertColsFunc(self, data: List[list], pos: int, numCols: int = 1):
        nrows = len(data)
        lst = build_empty(numCols, nrows)
        dat = list_transpose(data)
        dat_ = dat[:pos] + lst + dat[pos:]
        return list_transpose(dat_)


class Grid(GridBase):

    def __init__(self,
                 parent,
                 data: Union[List[list], tuple, None] = None,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.WANTS_CHARS,
                 name=gridlib.GridNameStr) -> None:
        super().__init__(parent, DataBaseList(data), id, pos, size, style,
                         name)
        # self.HideRowLabels()
        # self.HideColLabels()

    def SetData(self, data: list):
        if not isinstance(data, list):
            raise ValueError('HGrid_list.SetData: data 数据类型不支持')
        # if not isinstance(data[0], list):
        #     data = [data]
        super().SetData(data)


class GridWithHeader(wx.Panel):

    def __init__(self,
                 parent,
                 subject: Union[List[List[str]], Tuple[int, ...], None] = None,
                 header: Union[List[List[str]], Tuple[int, ...], None] = None,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.TAB_TRAVERSAL,
                 name='GridWithHeader'):
        super().__init__(parent, id, pos, size, style, name)
        if header is None:
            if subject is None:
                header = (1, 3)
            elif isinstance(subject, tuple):
                header = (1, subject[1])
            elif isinstance(subject, list):
                header = (1, len(subject[0]))
            else:
                raise TypeError('GridWithHeader: subject 数据类型不支持')
        self.header = Grid(self, header)
        self.subject = Grid(self, subject)
        self.header.HideColLabels()
        self.subject.HideColLabels()
        self._isRowLabelsVisable = 1
        self.line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        self.line.SetMinSize((-1, 3))
        self.line.SetMaxSize((-1, 3))

        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.layout.Add(self.header, 0, wx.ALL | wx.EXPAND, 0)
        self.layout.Add(self.line, 0, wx.ALL | wx.EXPAND, 0)
        self.layout.Add(self.subject, 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(self.layout)

        self.header.Bind(wx.EVT_SCROLLWIN, self._on_grid_scroll)  # 横向滚动条同步
        self.subject.Bind(wx.EVT_SCROLLWIN, self._on_grid_scroll)  # 横向滚动条同步
        # 根据实际长度改变高度 防止滚动条遮盖内容
        self.header.Bind(gridlib.EVT_GRID_CELL_CHANGED, self._on_changed_size)
        self.subject.Bind(gridlib.EVT_GRID_CELL_CHANGED, self._on_changed_size)
        self.Bind(wx.EVT_SIZE, self._on_size)

    def _on_grid_scroll(self, event):
        # 同步Grid的横向滚动条
        # 获取事件的发送者
        sender = event.GetEventObject()
        # 获取当前Grid的滚动信息
        scroll_x, _ = sender.GetViewStart()
        # 设置另一个网格的滚动条位置
        if sender == self.header:
            _, scroll_y = self.subject.GetViewStart()
            self.subject.Scroll(scroll_x, scroll_y)
        elif sender == self.subject:
            _, scroll_y = self.header.GetViewStart()
            self.header.Scroll(scroll_x, scroll_y)
        event.Skip()

    def _on_changed_size_(self, grid: Grid):
        # 根据实际长度改变高度 防止滚动条遮盖内容
        w, _ = grid.GetSize()
        if grid.GetNumberCols() + self._isRowLabelsVisable > w / 80:
            self.header.SetMinSize((w, 49))
            self.header.SetMaxSize((w, 49))
        else:
            self.header.SetMinSize((w, 31))
            self.header.SetMaxSize((w, 31))

    def _on_changed_size(self, event):
        # 根据实际长度改变高度 防止滚动条遮盖内容
        grid = event.GetEventObject()  # 获取事件的发送者
        self._on_changed_size_(grid)
        self.layout.Layout()
        event.Skip()

    def _on_size(self, event):
        # 配合改变高度
        w, _ = event.GetSize()
        _, h1 = self.header.GetSize()
        self.header.SetMinSize((w, h1))
        self.header.SetMaxSize((w, h1))
        self.header.SetSize(w, h1)
        # self.subject.SetMinSize((w, -1))
        # self.subject.SetMaxSize((w, -1))
        self._on_changed_size_(self.header)
        event.Skip()

    def SetFont(self, font: wx.Font):
        super().SetFont(font)
        self.header.SetFont(font)
        self.subject.SetFont(font)
        self.header.SetDefaultCellFont(font)
        self.subject.SetDefaultCellFont(font)

    def SetLabelFont(self, font: wx.Font):
        self.header.SetLabelFont(font)
        self.subject.SetLabelFont(font)

    def HideRowLabels(self):
        self.header.HideRowLabels()
        self.subject.HideRowLabels()
        self._isRowLabelsVisable = 0

    def SetHeader(self, data: list):
        self.header.SetData(data)

    def SetSubject(self, data: List[list]):
        self.subject.SetData(data)

    def SetHeaderLabels(self, labels: List[str]):
        self.header.dataBase.SetColLabels(labels)

    def SetSubjectLabels(self, labels: List[str]):
        self.subject.dataBase.SetColLabels(labels)


__all__= ['DataBaseList', 'GridWithHeader', 'Grid', 'gridlib']
