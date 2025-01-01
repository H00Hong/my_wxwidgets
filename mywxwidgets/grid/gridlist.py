# -*- coding: utf-8 -*-
"""
自定义Grid

DataBaseList
    基于 list[list] 的表格数据基

Grid
    基于 DataBaseList 的表格
    鼠标右键菜单和键盘快捷键--复制、粘贴、剪切、插入、删除、清除

GridWithHeader
    带表头的 Grid, 两个 Grid 的组合
"""
from typing import List, Tuple, Union

import wx

from . import gridbase


def list_transpose(x: List[list]):
    return list(map(list, zip(*x)))


class DataBaseList(gridbase.DataBase):
    """
    基于 list[list] 的表格数据基

    Parameters
    ----------
    data: List[list]
        数据
    rowlabels: List[str]
        行标签
    collabels: List[str]
        列标签
    show_format: str
        显示格式

    Attributes
    ----------
    data: List[list]
        数据
    rowlabels: List[str]
        行标签
    collabels: List[str]
        列标签
    show_format: str
        显示格式

    Methods
    -------
    GetNumberRows()
        获取行数
    GetNumberCols()
        获取列数
    GetValue(row: int, col: int)
        获取单元格值
    SetValue(row: int, col: int, value)
        设置单元格值
    SetData(data)
        设置数据
    
    SetRowLabels(rowlabels)
        设置行标签
    SetColLabels(collabels)
        设置列标签
    SetShowFormat(show_format)
        设置显示格式

    """

    def __init__(self,
                 data: Union[List[list], list, Tuple[int, ...], None] = None,
                 rowlabels: Union[List[str], None] = None,
                 collabels: Union[List[str], None] = None,
                 show_format: Union[str, None] = None) -> None:
        super(DataBaseList, self).__init__()
        if data is None:
            data = (3, 3)
        if isinstance(data, tuple):
            data = gridbase.build_empty(*data)
        self.data = self.SetDataFunc(data)
        if rowlabels is not None:
            self.SetRowLabels(rowlabels)
        if collabels is not None:
            self.SetColLabels(collabels)
        self.SetShowFormat(show_format)

    def GetNumberRows(self) -> int:
        return len(self.data)

    def GetNumberCols(self) -> int:
        return len(self.data[0])

    def SetDataFunc(self, lst) -> List[list]:
        if not isinstance(lst, list):
            raise TypeError(f'{self.__class__}: data type must be list')
        b = [isinstance(i, list) for i in lst]
        if all(b):
            if len(set([len(i) for i in lst])) != 1:
                raise ValueError(f'{self.__class__}: data type must be list[list]')
            return lst
        elif all([not i for i in b]):
            return [lst]
        else:
            raise TypeError(f'{self.__class__}: data type must be list[list]')

    def GetValueFunc(self, data: List[list], row: int, col: int) -> Union[float, complex, str]:
        val = data[row][col]
        try:
            val = complex(val)
            if -5e-16 < val.imag < 5e-16:
                val = val.real
            return val
        except:
            return str(val)

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
        return data + gridbase.build_empty(numRows, ncols)

    def AppendColsFunc(self, data: List[list], numCols: int = 1):
        nrows = len(data)
        lst = gridbase.build_empty(numCols, nrows)
        dat = list_transpose(data)
        return list_transpose(dat + lst)

    def InsertRowsFunc(self, data: List[list], pos: int, numRows: int = 1):
        ncols = len(data[0])
        lst = gridbase.build_empty(numRows, ncols)
        return data[:pos] + lst + data[pos:]

    def InsertColsFunc(self, data: List[list], pos: int, numCols: int = 1):
        nrows = len(data)
        lst = gridbase.build_empty(numCols, nrows)
        dat = list_transpose(data)
        dat_ = dat[:pos] + lst + dat[pos:]
        return list_transpose(dat_)


class Grid(gridbase.GridBase):

    def __init__(self,
                 parent,
                 dat: Union[gridbase.DataBase, List[list], Tuple[int, ...], None] = None,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.WANTS_CHARS,
                 name='Grid',
                 read_only: bool = False) -> None:
        if not isinstance(dat, gridbase.DataBase):
            dat = DataBaseList(dat)
        super().__init__(parent, dat, id, pos, size, style, name, read_only)
        # self.HideRowLabels()
        # self.HideColLabels()


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
                raise TypeError(f'{self.__class__}: subject 数据类型不支持')
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
        # 同步插入列 删除列
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
        grid: Grid = event.GetEventObject()
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
        # print('_on_changed_size_')
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
        self.layout.Layout()

    def _on_changed_size(self, event):
        # 根据实际长度改变高度 防止滚动条遮盖内容
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

    def SetHeader(self, data: list):
        self.header.SetData(data)

    def SetSubject(self, data: List[list]):
        self.subject.SetData(data)

    def SetHeaderLabels(self, labels: List[str]):
        self.header.dataBase.SetRowLabels(labels)

    def SetSubjectLabels(self, labels: List[str]):
        self.subject.dataBase.SetRowLabels(labels)


__all__= ['DataBaseList', 'Grid', 'GridWithHeader']
