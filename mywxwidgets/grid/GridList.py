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

from .GridBase import DataBase, HGridBase, build_empty, FONT0, FONT1


def listT(x: List[list]):
    return [list(i) for i in zip(*x)]

def _DeleteRows(data, pos, numRows):
    return data[:pos] + data[pos + numRows:]
def _DeleteCols(data, pos, numCols):
    dat = listT(data)
    dat_ = dat[:pos] + dat[pos + numCols:]
    return listT(dat_)
def _AppendRows(data, numRows):
    ncols = len(data[0])
    data += build_empty(numRows, ncols)
    return data
def _AppendCols(data, numCols):
    nrows = len(data)
    lst = build_empty(numCols, nrows)
    dat = listT(data)
    return listT(dat + lst)
def _InsertRows(data, pos, numRows=1):
    ncols = len(data[0])
    lst = build_empty(numRows, ncols)
    return data[:pos] + lst + data[pos:]
def _InsertCols(data, pos, numCols=1):
    nrows = len(data)
    lst = build_empty(numCols, nrows)
    dat = listT(data)
    dat_ = dat[:pos] + lst + dat[pos:]
    return listT(dat_)


class DataBaseList(DataBase):
    """
    
    """

    def __init__(self,
                 data: Union[List[list], list, Tuple[int,...], None] = None,
                 rowLables: Union[List[str], None] = None,
                 colLabels: Union[List[str], None] = None) -> None:
        gridlib.GridTableBase.__init__(self)
        if data is None:
            data = (3, 3)
        if isinstance(data, tuple):
            data = build_empty(*data)
        data = self._check_list(data)
        self.data = data
        self.rowlabels = rowLables
        self.collabels = colLabels
        
        self._func['DeleteRows'] = _DeleteRows
        self._func['DeleteCols'] = _DeleteCols
        self._func['AppendRows'] = _AppendRows
        self._func['AppendCols'] = _AppendCols
        self._func['InsertRows'] = _InsertRows
        self._func['InsertCols'] = _InsertCols
        self._func['SetData'] = self._check_list
        self._func['GetValue'] = lambda data, row, col: data[row][col]
        self._func['SetValue'] = self._set_datavalue

    def _check_list(self, lst):
        if not isinstance(lst[0], list):
            return [lst]
        return lst

    def _set_datavalue(self, data, row, col, value):
        data[row][col] = value

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.data[0])

    def IsEmptyCell(self, row, col):
        item = self.GetValue(row, col)
        return item == '' or item is None

    def Clear(self):
        self.data = build_empty(self.GetNumberRows(), self.GetNumberCols())
        self.ValuesGeted()


class Grid(HGridBase):

    def __init__(self, 
                 parent, 
                 data: Union[List[list], tuple, None] = None, 
                 id=wx.ID_ANY, 
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.WANTS_CHARS,
                 name=gridlib.GridNameStr) -> None:
        super().__init__(parent, DataBaseList(data), id, 
                         pos, size, style, name)
        self.basetype = 'list' # 数据类型标识
        # self.HideRowLabels()
        # self.HideColLabels()


    def SetData(self, data:list):
        if not isinstance(data, list):
            raise ValueError('HGrid_list.SetData: data 数据类型不支持')
        # if not isinstance(data[0], list):
        #     data = [data]
        super().SetData(data)


class GridWithHeader(wx.Panel):

    def __init__(self, parent,
                 subject: Union[List[list], Tuple[int,...], None] = None,
                 header: Union[List[list], Tuple[int,...], None] = None,
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
        self.header = Grid(self, -1, header)
        self.subject = Grid(self, -1, subject)
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

        self.header.Bind(wx.EVT_SCROLLWIN, self._on_grid_scroll) # 横向滚动条同步
        self.subject.Bind(wx.EVT_SCROLLWIN, self._on_grid_scroll) # 横向滚动条同步
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
        grid = event.GetEventObject() # 获取事件的发送者
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


if __name__ == '__main__':
    
    app = wx.App()
    frame = wx.Frame(None, -1, '测试', size=(400, 400))
    grid = GridWithHeader(frame,  (10, 10))
    grid.SetHeaderLabels(['a'])
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(grid, 1, wx.EXPAND| wx.ALL, 5)
    but = wx.Button(frame, -1, 'test')
    sizer.Add(but, 0, wx.EXPAND| wx.ALL, 5)
    frame.SetSizer(sizer)
    def on_click(event):
        grid.SetSubject([[1,2,3],[4,5,6]])
        grid.SetHeader(['a', 'b', 'c'])
    
    but.Bind(wx.EVT_BUTTON, on_click)
    
    frame.Show()
    app.MainLoop()
