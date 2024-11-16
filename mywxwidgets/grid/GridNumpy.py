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


def _set_value(data: ndarray, row: int, col: int, value) -> None:
    data[row, col] = value


def _delete_rows(data: ndarray, pos: int, numRows: int):
    return delete(data, list(range(pos, pos + numRows)), axis=0)


def _delete_cols(data: ndarray, pos: int, numCols: int):
    return delete(data, list(range(pos, pos + numCols)), axis=1)


def _empty(rows: int, cols: int):
    return asarray(build_empty(rows, cols))


def _append_rows(data: ndarray, numRows: int):
    return insert(data, data.shape[0], _empty(numRows, data.shape[1]), axis=0)


def _append_cols(data: ndarray, numCols: int):
    return insert(data, data.shape[1], _empty(numCols, data.shape[0]), axis=1)


def _insert_rows(data: ndarray, pos: int, numRows: int):
    return insert(data, pos, _empty(numRows, data.shape[1]), axis=0)


def _insert_cols(data: ndarray, pos: int, numCols: int):
    return insert(data, pos, _empty(numCols, data.shape[0]), axis=1)


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
                 rowLabels: Union[List[str], None] = None,
                 colLabels: Union[List[str], None] = None):
        gridlib.GridTableBase.__init__(self)
        if data is None:
            data = (3, 3)
        if isinstance(data, tuple):
            data = build_empty(*data)
        self.data = self._check_array(data)
        self.rowlabels = rowLabels
        self.collabels = colLabels

        self._func['DeleteRows'] = _delete_rows
        self._func['DeleteCols'] = _delete_cols
        self._func['AppendRows'] = _append_rows
        self._func['AppendCols'] = _append_cols
        self._func['InsertRows'] = _insert_rows
        self._func['InsertCols'] = _insert_cols
        self._func['SetData'] = self._check_array
        self._func['GetValue'] = lambda data, row, col: data[row, col]
        self._func['SetValue'] = _set_value

    def _check_array(self, obj):
        return _check_array(asarray(obj))

    def GetNumberRows(self):
        return self.data.shape[0]

    def GetNumberCols(self):
        return self.data.shape[1]

    def IsEmptyCell(self, row, col):
        item = self.GetValue(row, col)
        return item == '' or item is None

    def Clear(self):
        self.data = _empty(self.GetNumberRows(), self.GetNumberCols())
        self.ValuesGeted()


class DataBaseObj(DataBaseNDArray):

    def _check_array(self, obj):
        arr = array(obj, object)
        super()._check_array(arr)


class DataBaseStr(DataBaseNDArray):

    def _check_array(self, obj):
        arr = array(obj, str)
        super()._check_array(arr)


class Grid(GridBase):
    dataBase: DataBaseNDArray

    def __init__(self,
                 parent,
                 id=wx.ID_ANY,
                 data: Union[List[list], tuple, None] = None,
                 data_type: Literal['object', 'str'] = 'object'):
        if data_type == 'object':
            data_base = DataBaseObj(data)
        elif data_type == 'str':
            data_base = DataBaseStr(data)
        else:
            raise ValueError('data_type must be "object" or "number"')
        super().__init__(parent, id, data_base)
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
                 id=wx.ID_ANY,
                 subject: Union[List[list], Tuple[int, ...], None] = None,
                 header: Union[List[list], Tuple[int, ...], None] = None):
        super().__init__(parent, id)
        if header is None:
            if subject is None:
                header = (1, 3)
            elif isinstance(subject, tuple):
                header = (1, subject[1])
            elif isinstance(subject, list):
                header = (1, len(subject[0]))
        self.header = Grid(self, -1, header)
        self.subject = Grid(self, -1, subject, 'str')
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


if __name__ == '__main__':

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

    app = wx.App()
    frame = Main()
    frame.Show()
    app.MainLoop()
