# -*- coding: utf-8 -*-
"""
自定义Grid

Grid
    基于 ndarray 的数据类型
    鼠标右键菜单和键盘快捷键--复制、粘贴、剪切、插入、删除、清除

GridWithHeader
    带表头的 Grid  两个 Grid 的组合
"""
from typing import Union, Sequence, List, Tuple, Literal
from numpy import array, asarray, ndarray, newaxis, insert, delete

import wx
import wx.grid as gridlib

from .GridBase import DataBase, GridBase, FONT0, FONT1, build_empty


def _empty(rows: int, cols: int):
    return asarray(build_empty(rows, cols))


def _check_array(arr: ndarray):
    if arr.ndim == 0:
        return arr.reshape(1, 1)
    elif arr.ndim == 1:
        return arr[:, newaxis]
    elif arr.ndim == 2:
        return arr
    else:
        raise ValueError('The `ndim` of the input array must <= 2')


class DataBaseNDArray(DataBase):  # 基类
    # ndarray
    data: ndarray

    def __init__(self,
                 data: Union[ndarray, Sequence, None] = None,
                 rowlabels: Union[List[str], None] = None,
                 collabels: Union[List[str], None] = None):
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
        return self.data.shape[0]

    def GetNumberCols(self) -> int:
        return self.data.shape[1]

    def SetDataFunc(self, obj):
        return _check_array(asarray(obj))

    def SetValueFunc(self, data: ndarray, row: int, col: int, value) -> None:
        data[row, col] = value

    def GetValueFunc(self, data: ndarray, row: int, col: int) -> str:
        return str(data[row, col])

    def DeleteRowsFunc(self, data: ndarray, pos: int, numRows: int):
        return delete(data, list(range(pos, pos + numRows)), axis=0)

    def InsertRowsFunc(self, data: ndarray, pos: int, numRows: int):
        return insert(data, pos, _empty(numRows, data.shape[1]), axis=0)

    def AppendRowsFunc(self, data: ndarray, numRows: int):
        return insert(data, data.shape[0], _empty(numRows, data.shape[1]), axis=0)

    def DeleteColsFunc(self, data: ndarray, pos: int, numCols: int):
        return delete(data, list(range(pos, pos + numCols)), axis=1)

    def InsertColsFunc(self, data: ndarray, pos: int, numCols: int):
        return insert(data, pos, _empty(numCols, data.shape[0]), axis=1)

    def AppendColsFunc(self,data: ndarray, numCols: int):
        return insert(data, data.shape[1], _empty(numCols, data.shape[0]), axis=1)


class DataBaseObj(DataBaseNDArray):

    def SetDataFunc(self, obj):
        arr = array(obj, object)
        return super().SetDataFunc(arr)


class DataBaseStr(DataBaseNDArray):

    def SetDataFunc(self, obj):
        arr = array(obj, str)
        return super().SetDataFunc(arr)


class Grid(GridBase):
    dataBase: DataBaseNDArray

    def __init__(self,
                 parent,
                 data: Union[List[list], tuple, None] = None,
                 data_type: Literal['object', 'str'] = 'object',
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.WANTS_CHARS,
                 name=gridlib.GridNameStr):
        if data_type == 'object':
            data_base = DataBaseObj(data)
        elif data_type == 'str':
            data_base = DataBaseStr(data)
        else:
            raise ValueError('data_type must be "object" or "str"')
        super().__init__(parent, data_base, id, pos, size, style, name)
        self.basetype = 'ndarray_' + data_type
        # self.HideRowLabels()
        # self.HideColLabels()

    def _OnCopy(self, event):
        # 实现复制功能的代码
        top_left, bottom_right = self._selected_range
        lst = self.dataBase.data[top_left[0]:bottom_right[0] + 1,
                                 top_left[1]:bottom_right[1] + 1].astype(str)
        text = '\n'.join('\t'.join(i) for i in lst)
        # 复制到剪切板
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()


class GridWithHeader(wx.Panel):

    def __init__(self,
                 parent,
                 subject: Union[List[list], Tuple[int, ...], None] = None,
                 header: Union[List[list], Tuple[int, ...], None] = None,
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
        self.header = Grid(self, header)
        self.subject = Grid(self, subject, 'str')
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

    def SetHeader(self, data: List[list]):
        self.header.SetData(data)

    def SetSubject(self, data: List[list]):
        self.subject.SetData(data)

    def SetHeaderLabels(self, labels: List[str]):
        self.header.dataBase.rowlabels = labels

    def SetSubjectLabels(self, labels: List[str]):
        self.subject.dataBase.collabels = labels


__all__ = ['DataBaseObj', 'DataBaseStr', 'Grid', 'GridWithHeader', 'gridlib']
