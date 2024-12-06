# -*- coding: utf-8 -*-
"""
自定义Grid

Grid
    基于 ndarray 的数据类型
    鼠标右键菜单和键盘快捷键--复制、粘贴、剪切、插入、删除、清除

GridWithHeader
    带表头的 Grid  两个 Grid 的组合
"""
from typing import List, Tuple, Union

import wx
from numpy import asarray, char, delete, insert, ndarray, newaxis

from . import gridbase


class DataBaseNP(gridbase.DataBase):

    data: char.chararray
    _slen: int

    def __init__(self,
                 data: Union[ndarray, char.chararray, list, tuple, None] = None,
                 str_len: int = 10,
                 rowlabels: Union[List[str], None] = None,
                 collabels: Union[List[str], None] = None):
        super(DataBaseNP, self).__init__()
        if data is None:
            data = (3, 3)
        if isinstance(data, tuple):
            if len(data) != 2:
                raise ValueError(f'{self.__class__}.data: The length of the tuple must be 2')
            data = gridbase.build_empty(*data)
        if not isinstance(str_len, int):
            raise TypeError(f'{self.__class__}: str_len must be int')
        if str_len < 1:
            raise ValueError(f'{self.__class__}: str_len must > 0')
        data = asarray(data, str)
        dtype = data.dtype
        slen = dtype.itemsize // dtype.alignment
        self._slen = slen if slen > str_len else str_len
        self.data = self.SetDataFunc(data)
        if rowlabels is not None:
            self.SetRowLabels(rowlabels)
        if collabels is not None:
            self.SetColLabels(collabels)

    def _set_array(self, obj):
        return char.asarray(obj, self._slen, unicode=True)

    def SetDataFunc(self, obj) -> char.chararray:
        arr = self._set_array(obj)
        if arr.ndim == 0:
            return arr.reshape(1, 1)
        elif arr.ndim == 1:
            return arr[:, newaxis]
        elif arr.ndim == 2:
            return arr
        else:
            raise ValueError(f'{self.__class__}: The `ndim` of the input array must <= 2')

    def GetNumberRows(self) -> int:
        return self.data.shape[0]

    def GetNumberCols(self) -> int:
        return self.data.shape[1]

    def SetValueFunc(self, data: char.chararray, row: int, col: int, value) -> None:
        if len(str(value)) > self._slen:
            self._slen = len(str(value))
            data = self.SetDataFunc(data)
        data[row, col] = value

    def GetValueFunc(self, data: char.chararray, row: int, col: int) -> str:
        return str(data[row, col])

    def DeleteRowsFunc(self, data: char.chararray, pos: int, numRows: int) -> char.chararray:
        return delete(data, list(range(pos, pos + numRows)), axis=0)

    def InsertRowsFunc(self, data: char.chararray, pos: int, numRows: int) -> char.chararray:
        empty = self._set_array(gridbase.build_empty(numRows, data.shape[1]))
        return insert(data, pos, empty, axis=0)

    def AppendRowsFunc(self, data: char.chararray, numRows: int) -> char.chararray:
        empty = self._set_array(gridbase.build_empty(numRows, data.shape[1]))
        return insert(data, data.shape[0], empty, axis=0)

    def DeleteColsFunc(self, data: char.chararray, pos: int, numCols: int) -> char.chararray:
        return delete(data, list(range(pos, pos + numCols)), axis=1)

    def InsertColsFunc(self, data: char.chararray, pos: int, numCols: int) -> char.chararray:
        empty = self._set_array(gridbase.build_empty(numCols, data.shape[0]))
        return insert(data, pos, empty, axis=1)

    def AppendColsFunc(self,data: char.chararray, numCols: int) -> char.chararray:
        empty = self._set_array(gridbase.build_empty(numCols, data.shape[0]))
        return insert(data, data.shape[1], empty, axis=1)


class Grid(gridbase.GridBase):

    dataBase: DataBaseNP

    def __init__(self,
                 parent,
                 dat: Union[gridbase.DataBase, ndarray, char.chararray, List[list],
                            Tuple[int, ...], None] = None,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.WANTS_CHARS,
                 name='Grid') -> None:
        if not isinstance(dat, gridbase.DataBase):
            dat = DataBaseNP(dat)
        super().__init__(parent, dat, id, pos, size, style, name)
        # self.HideRowLabels()
        # self.HideColLabels()

    def _OnCopy(self, event) -> None:
        # 实现复制功能的代码
        top_left, bottom_right = self._selected_range
        lst = self.dataBase.data[top_left[0]:bottom_right[0] + 1,
                                 top_left[1]:bottom_right[1] + 1]
        text = '\n'.join('\t'.join(i) for i in lst)
        # 复制到剪切板
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()


class GridWithHeader(wx.Panel):

    def __init__(self,
                 parent,
                 subject: Union[ndarray, char.chararray, List[list],
                                Tuple[int, ...], None] = None,
                 header: Union[ndarray, char.chararray, List[list],
                               Tuple[int, ...], None] = None,
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
        self.subject = Grid(self, subject)
        self.header.HideColLabels()
        self.subject.HideColLabels()
        self.SetHeaderLabels([f'header{i+1}' for i in range(100)])

        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.layout.Add(self.header, 0, wx.ALL | wx.EXPAND, 0)
        self.layout.Add(self._line(), 0, wx.ALL | wx.EXPAND, 0)
        self.layout.Add(self.subject, 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(self.layout)

        self._connect_grid()
        # 根据实际长度改变高度 防止滚动条遮盖内容
        self.header.Bind(gridbase.EVT_GRID_CELL_CHANGED, self._on_changed_size)
        self.subject.Bind(gridbase.EVT_GRID_CELL_CHANGED, self._on_changed_size)
        self.Bind(wx.EVT_SIZE, self._on_size)

    def _line(self):
        line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        line.SetMinSize((-1, 3))
        line.SetMaxSize((-1, 3))
        return line

    def _connect_grid(self):
        # 同步横向滚动条
        self.header.Bind(wx.EVT_SCROLLWIN, self._on_grid_scroll)
        self.subject.Bind(wx.EVT_SCROLLWIN, self._on_grid_scroll)
        # 同步插入列 同步删除列
        self.header.Bind(gridbase.EVT_GRID_COLS_APPENDED, self._on_grid_cols)
        self.subject.Bind(gridbase.EVT_GRID_COLS_APPENDED, self._on_grid_cols)
        self.header.Bind(gridbase.EVT_GRID_COLS_INSERTED, self._on_grid_cols)
        self.subject.Bind(gridbase.EVT_GRID_COLS_INSERTED, self._on_grid_cols)
        self.header.Bind(gridbase.EVT_GRID_COLS_DELETED, self._on_grid_cols)
        self.subject.Bind(gridbase.EVT_GRID_COLS_DELETED, self._on_grid_cols)
        # 同步改变列宽
        self.header.Bind(gridbase.EVT_GRID_COL_SIZE, self._on_grid_colsize)
        self.subject.Bind(gridbase.EVT_GRID_COL_SIZE, self._on_grid_colsize)

    def _on_grid_scroll(self, event):
        # 同步Grid的横向滚动条
        # 获取事件的发送者
        sender = event.GetEventObject()
        # 获取当前Grid的滚动信息
        scroll_x, _ = sender.GetViewStart()
        # 设置另一个网格的滚动条位置
        if sender is self.header:
            _, scroll_y = self.subject.GetViewStart()
            self.subject.Scroll(scroll_x, scroll_y)
        elif sender is self.subject:
            _, scroll_y = self.header.GetViewStart()
            self.header.Scroll(scroll_x, scroll_y)
        event.Skip()

    def _on_grid_cols(self, event: gridbase.GridRowColEvent):
        # 同步列增减
        grid: Grid = event.GetEventObject().GetView()
        if grid is self.header:
            obj = self.subject.dataBase
        elif grid is self.subject:
            obj = self.header.dataBase
        if event.GetCommandType() == 'insert':
            if event.GetPosition() == -1:
                obj.AppendCols(event.GetNum(), False)
            else:
                obj.InsertCols(event.GetPosition(), event.GetNum(), False)
        else:
            obj.DeleteCols(event.GetPosition(), event.GetNum(), False)
        self._on_changed_size_()
        event.Skip()
    
    def _on_grid_colsize(self, event):
        # 同步列宽改变
        grid: Grid = event.GetEventObject()
        ncol = event.GetRowOrCol()
        w = grid.GetColSize(ncol)
        if grid is self.header:
            self.subject.SetColSize(ncol, w)
        elif grid is self.subject:
            self.header.SetColSize(ncol, w)
        self._on_changed_size_()
        event.Skip()

    def _on_changed_size_(self):
        # 根据实际长度改变高度 防止滚动条遮盖内容
        w, _ = self.header.GetSize()
        colwidths = [
            self.header.GetColSize(i)
            for i in range(self.header.GetNumberCols())
        ]
        labelwidth = self.header.GetRowLabelSize()
        h = self.header.GetRowSize(0)
        if self.header.GetNumberRows() > 1:
            h += h // 2
        if sum(colwidths) + labelwidth > w:
            _, sh = self.subject.GetSize()
            _, sh0 = self.subject.GetVirtualSize()
            h += sh - sh0
        size = wx.Size(w, h)
        self.header.SetSize(size)
        self.header.SetMinSize(size)
        self.header.SetMaxSize(size)
        self.Layout()

    def _on_changed_size(self, event):
        # 根据实际长度改变高度 防止滚动条遮盖内容
        # grid = event.GetEventObject()  # 获取事件的发送者
        self._on_changed_size_()
        event.Skip()

    def _on_size(self, event):
        # 配合改变高度
        w, _ = event.GetSize()
        _, h = self.header.GetSize()
        self.header.SetSize(w, h)
        self._on_changed_size_()
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

    def SetHeader(self, data: List[list]):
        self.header.SetData(data)

    def SetSubject(self, data: List[list]):
        self.subject.SetData(data)

    def SetHeaderLabels(self, labels: List[str]):
        self.header.dataBase.SetRowLabels(labels)

    def SetSubjectLabels(self, labels: List[str]):
        self.subject.dataBase.SetRowLabels(labels)


__all__ = ['DataBaseNP', 'Grid', 'GridWithHeader']
