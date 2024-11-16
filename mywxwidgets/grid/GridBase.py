# -*- coding: utf-8 -*-
"""
自定义Grid基类

Grid
    鼠标右键菜单和键盘快捷键--复制、粘贴、剪切、插入、删除、清除

GridWithHeader
    带表头的 Grid  两个 Grid 的组合
"""
from typing import List, Tuple, Callable, Optional, Iterable, TypedDict

import wx
import wx.grid as gridlib


def build_empty(rows: int, cols: int) -> List[List[str]]:
    return [[''] * cols for _ in range(rows)]


FONT0 = (14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
         False, 'Microsoft Yahei')
FONT1 = (16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
         False, 'Microsoft Yahei')


class _FuncDict(TypedDict):
    DeleteRows: Optional[Callable]  # Callable[[List[list], int, int], List[list]]
    InsertRows: Optional[Callable]  # Callable[[List[list], int, int], List[list]]
    AppendRows: Optional[Callable]  # Callable[[List[list], int, int], List[list]]
    DeleteCols: Optional[Callable]  # Callable[[List[list], int, int], List[list]]
    InsertCols: Optional[Callable]  # Callable[[List[list], int, int], List[list]]
    AppendCols: Optional[Callable]  # Callable[[List[list], int, int], List[list]]
    GetValue: Optional[Callable]  # Callable[[List[list], int, int], str]
    SetValue: Optional[Callable]  # Callable[[List[list], int, int, str], None]
    SetData: Optional[Callable]  # Callable[[List[list]], List[list]]


class DataBase(gridlib.GridTableBase):  # 基类

    data: List[list]
    rowlabels: Optional[List[str]]
    collabels: Optional[List[str]]

    _func: _FuncDict = {
        'DeleteRows': None,
        'InsertRows': None,
        'AppendRows': None,
        'DeleteCols': None,
        'InsertCols': None,
        'AppendCols': None,
        'GetValue': None,
        'SetValue': None,
        'SetData': None,
    }

    def GetNumberRows(self):  # return len(self.data)
        raise NotImplementedError('not implement GetNumberRows')

    def GetNumberCols(self):  # return len(self.data[0])
        raise NotImplementedError('not implement GetNumberCols')

    def GetValue(self, row: int, col: int):
        try:
            assert self._func['GetValue'] is not None
            return self._func['GetValue'](self.data, row, col)
        except:
            return ''

    def SetData(self, data):
        """替换整个数据集"""
        old_rows, old_cols = self.GetNumberRows(), self.GetNumberCols()
        assert self._func['SetData'] is not None, 'not implement SetData'
        self.data = self._func['SetData'](data)
        new_rows, new_cols = self.GetNumberRows(), self.GetNumberCols()
        if old_rows > new_rows:
            self.RowsDeleted(0, old_rows - new_rows)
        elif old_rows < new_rows:
            self.RowsAppended(new_rows - old_rows)
        if old_cols > new_cols:
            self.ColsDeleted(0, old_cols - new_cols)
        elif old_cols < new_cols:
            self.ColsAppended(new_cols - old_cols)
        self.ValuesGeted()

    def SetDataValue(self, row: int, col: int, value):
        """设置单个单元格的值"""
        assert self._func['SetValue'] is not None, 'not implement SetValue'
        self._func['SetValue'](self.data, row, col, value)
        self.ValuesGeted()

    def SetValue(self, row: int, col: int, value):
        # 从gui界面传入的value为str
        nrows, ncols = self.GetNumberRows(), self.GetNumberCols()
        if col > ncols:
            self.AppendCols(col + 1 - ncols)
        if row > nrows:
            self.AppendRows(row + 1 - nrows)
        assert self._func['SetValue'] is not None, 'not implement SetValue'
        self._func['SetValue'](self.data, row, col, value)
        self.ValuesGeted()

#region ProcessTableMessage

    def ValuesGeted(self):
        # print('GetValues')
        self.GetView().ProcessTableMessage(
            gridlib.GridTableMessage(
                self, gridlib.GRIDTABLE_REQUEST_VIEW_GET_VALUES))

    def RowsDeleted(self, pos: int, numRows: int):
        self.GetView().ProcessTableMessage(
            gridlib.GridTableMessage(self,
                                     gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED,
                                     pos, numRows))

    def RowsAppended(self, numRows: int):
        self.GetView().ProcessTableMessage(
            gridlib.GridTableMessage(self,
                                     gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED,
                                     numRows))

    def RowsInserted(self, pos: int, numRows: int):
        self.GetView().ProcessTableMessage(
            gridlib.GridTableMessage(self,
                                     gridlib.GRIDTABLE_NOTIFY_ROWS_INSERTED,
                                     pos, numRows))

    def ColsDeleted(self, pos: int, numCols: int):
        self.GetView().ProcessTableMessage(
            gridlib.GridTableMessage(self,
                                     gridlib.GRIDTABLE_NOTIFY_COLS_DELETED,
                                     pos, numCols))

    def ColsAppended(self, numCols: int):
        self.GetView().ProcessTableMessage(
            gridlib.GridTableMessage(self,
                                     gridlib.GRIDTABLE_NOTIFY_COLS_APPENDED,
                                     numCols))

    def ColsInserted(self, pos: int, numCols: int):
        self.GetView().ProcessTableMessage(
            gridlib.GridTableMessage(self,
                                     gridlib.GRIDTABLE_NOTIFY_COLS_INSERTED,
                                     pos, numCols))


#endregion

    def RowLabelRedrawed(self, row: int):
        pass

    def SetRowLabels(self, rowlables: Iterable):
        if isinstance(rowlables, Iterable):
            raise TypeError('rowlables must be Iterable')
        self.rowlabels = [str(i) for i in rowlables]

    def SetRowLabelValue(self, row: int, label: str):
        if self.rowlabels is None:
            return False
        self.rowlabels[row] = label
        return True

    def GetRowLabelValue(self, row: int):
        if self.rowlabels:
            return self.rowlabels[row]
        return super().GetRowLabelValue(row)

    def SetColLabels(self, collabels: Iterable):
        if isinstance(collabels, Iterable):
            raise TypeError('collabels must be Iterable')
        self.collabels = [str(i) for i in collabels]

    def SetColLabelValue(self, col: int, label: str):
        if self.collabels is None:
            return False
        self.collabels[col] = label
        return True

    def GetColLabelValue(self, col: int):
        if self.collabels:
            return self.collabels[col]
        return super().GetColLabelValue(col)

    def IsEmptyCell(self, row: int, col: int):
        item = self.GetValue(row, col)
        return item == '' or item is None

    def DeleteRows(self, pos: int, numRows: int = 1):
        func = self._func['DeleteRows']
        assert func is not None, 'not implement DeleteRows'
        try:
            self.data = func(self.data, pos, numRows)
            self.RowsDeleted(pos, numRows)
            return True
        except Exception as e:
            print(e)
            return False

    def DeleteCols(self, pos: int, numCols: int = 1):
        func = self._func['DeleteCols']
        assert func is not None, 'not implement DeleteCols'
        try:
            self.data = func(self.data, pos, numCols)
            self.ColsDeleted(pos, numCols)
            return True
        except Exception as e:
            print(e)
            return False

    def AppendRows(self, numRows: int = 1):
        func = self._func['AppendRows']
        assert func is not None, 'not implement AppendRows'
        try:
            self.data = func(self.data, numRows)
            self.RowsAppended(numRows)
            self.ValuesGeted()
            return True
        except Exception as e:
            print(e)
            return False

    def AppendCols(self, numCols: int = 1):
        func = self._func['AppendCols']
        assert func is not None, 'not implement AppendCols'
        try:
            self.data = func(self.data, numCols)
            self.ColsAppended(numCols)
            self.ValuesGeted()
            return True
        except Exception as e:
            print(e)
            return False

    def InsertRows(self, pos: int, numRows: int = 1):
        func = self._func['InsertRows']
        assert func is not None, 'not implement AppendCols'
        try:
            self.data = func(self.data, pos, numRows)
            self.RowsInserted(pos, numRows)
            self.ValuesGeted()
            return True
        except Exception as e:
            print(e)
            return False

    def InsertCols(self, pos: int, numCols: int = 1):
        func = self._func['InsertCols']
        assert func is not None, 'not implement AppendCols'
        try:
            self.data = func(self.data, pos, numCols)
            self.ColsInserted(pos, numCols)
            self.ValuesGeted()
            return True
        except Exception as e:
            print(e)
            return False

COPY = 'Copy'
PASTE = 'Paste'
CUT = 'Cut'
INSERT_UP = 'InsertUp'
INSERT_DOWN = 'InsertDown'
INSERT_LEFT = 'InsertLeft'
INSERT_RIGHT = 'InsertRight'
DELETE_VALUE = 'DeleteValue'
DELETE_ROWS = 'DeleteRows'
DELETE_COLS = 'DeleteCols'


class GridBase(gridlib.Grid):

    _MENU_ITEM: Tuple[Tuple[Optional[str], str], ...] = (
        (COPY, '复制  Ctrl+C'),
        (PASTE, '粘贴  Ctrl+V'),
        (CUT, '剪切  Ctrl+X'),
        (None, ''),
        (INSERT_UP, '向上插入空行'),
        (INSERT_DOWN, '向下插入空行'),
        (INSERT_LEFT, '向左插入空列'),
        (INSERT_RIGHT, '向右插入空列'),
        (None, ''),
        (DELETE_VALUE, '清除  Delete'),
        (DELETE_ROWS, '删除行'),
        (DELETE_COLS, '删除列')
    )

    def __init__(self,
                 parent,
                 dataBase: DataBase,  # 需要实现DataBase
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.WANTS_CHARS,
                 name='HGridBase') -> None:
        super().__init__(parent, id, pos, size, style, name)
        self.dataBase = dataBase
        self.SetTable(self.dataBase, True)
        self._selected_range: Tuple[Tuple[int, int], Tuple[int, int]] = ((0, 0), (0, 0))
        self._menu_event()

        font0 = wx.Font(*FONT0)

        self.SetFont(font0)
        self.SetLabelFont(font0)
        self.SetDefaultCellFont(font0)
        # self.AutoSizeRows()
        self.SetDefaultRowSize(31, True)

        # self.SetLabelBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.SetLabelBackgroundColour(wx.Colour(250, 250, 250))

    def SetData(self, data):
        self.dataBase.SetData(data)
        self.ForceRefresh()

    def _menu_event(self):
        # 创建一个右键菜单
        self.popupmenu = wx.Menu()
        # 绑定左键选择事件 获取选中区域
        self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self._OnRangeSelect)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self._OnLeftClick)
        # 绑定右键菜单事件
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self._OnRightClick)

        for i, (it0, it1) in enumerate(self._MENU_ITEM):
            if it0 is None:
                self.popupmenu.AppendSeparator()  # 插入分割线
            else:
                i += 10000  # 防止和一般ID冲突
                self.popupmenu.Append(i, it1)  # 添加菜单项
                self.Bind(wx.EVT_MENU,
                          handler=getattr(self, '_On' + it0),
                          id=i)  # 绑定菜单项事件
        # 绑定键盘事件
        self.Bind(wx.EVT_KEY_DOWN, self._OnKeyDown)

#region event_bind

    def _OnRangeSelect(self, event):
        # 当选择区域变化时，保存新的选定区域
        if event.Selecting():
            self._selected_range: Tuple[Tuple[int, int], Tuple[int, int]] = (
                event.GetTopLeftCoords(), event.GetBottomRightCoords())
        # else:
        #     self._selected_range = None

    def _OnLeftClick(self, event):
        # 获取被点击的行和列
        row: int = event.GetRow()
        col: int = event.GetCol()
        self._selected_range = ((row, col), (row, col))
        event.Skip()
        # print(row, col)

    def _OnKeyDown(self, event: wx.KeyEvent):
        key_code = event.GetKeyCode()  # 获取按键编码
        modifiers = event.GetModifiers()  # 获取按键修饰符
        # print('KeyCode:\t', key_code)
        # print('Modifiers:\t', modifiers)
        if modifiers == 2:  # 修饰符为ctrl
            if key_code == 67:  # ctrl+c
                self._OnCopy(event)
            elif key_code == 86:  # ctrl+v
                self._OnPaste(event)
            elif key_code == 88:  # ctrl+x
                self._OnCut(event)
        if modifiers == 0 and key_code == 127:  # 修饰符为空并且按下的是delete
            self._OnDeleteValue(event)
        # if modifiers == 0 and key_code == 8:  # 修饰符为空并且按下的是backspace
        #     pass
        # if modifiers == 0 and key_code == 88:
        #     print('')
        #     print(event.GetRow())

    def _OnRightClick(self, event):
        event.Skip(False)  # 阻止默认的右键点击行为
        # 获取被点击的行和列
        row: int = event.GetRow()
        col: int = event.GetCol()
        # print(f"右键点击了第{row}行，第{col}列")
        # 检查是否有选定的区域
        if self._selected_range:
            top_left, bottom_right = self._selected_range
            if row < top_left[0] or row > bottom_right[0] or col < top_left[
                    1] or col > bottom_right[1]:
                self.SelectBlock(row, col, row, col)
                self._selected_range = ((row, col), (row, col))
            # print(f"之前选定的区域从第{top_left[0]}行，第{top_left[1]}列到第{bottom_right[0]}行，第{bottom_right[1]}列")
            # self.SelectBlock(top_left[0], top_left[1], bottom_right[0], bottom_right[1])
        else:
            # print("没有之前选定的区域")
            self.SelectBlock(row, col, row, col)
            self._selected_range = ((row, col), (row, col))

        self.PopupMenu(self.popupmenu, event.GetPosition())

    def _OnCopy(self, event):
        # 实现复制功能
        # 获取选定区域
        # top_left = self.GetSelectionBlockTopLeft()[0]
        # bottom_right = self.GetSelectionBlockBottomRight()[0]
        top_left, bottom_right = self._selected_range
        # print(top_left)
        # print(bottom_right)
        lst = self.dataBase.data[top_left[0]:bottom_right[0] + 1]
        lst_ = (map(str, it[top_left[1]:bottom_right[1] + 1]) for it in lst)
        text = '\n'.join(['\t'.join(i) for i in lst_])
        # 复制到剪切板
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()

    def _OnPaste(self, event):
        # 实现粘贴功能
        # x, y = self.GetSelectionBlockTopLeft()[0]
        x, y = self._selected_range[0]
        text_data = wx.TextDataObject()
        if wx.TheClipboard.Open():  # 读取剪切板
            success = wx.TheClipboard.GetData(text_data)
            wx.TheClipboard.Close()
        if success:
            text: str = text_data.GetText()
            # print(text)
            ls = text.split('\n')
            if ls[-1] == '':
                ls.pop()
            ls1 = [row.split('\t') for row in ls]
            # 如果粘贴的行数和列数大于现有行数和列数，需要增加行和列
            dnrows = len(ls1) + x - self.GetNumberRows()
            dncols = len(ls1[0]) + y - self.GetNumberCols()
            if dncols > 0:
                # print("col")
                self.dataBase.AppendCols(dncols)
            if dnrows > 0:
                # print('row')
                self.dataBase.AppendRows(dnrows)

            for i in range(len(ls1)):
                for j in range(len(ls1[i])):
                    self.dataBase.data[i + x][j + y] = ls1[i][j]
            self.dataBase.ValuesGeted()  # 通知数据已经更新
            # self.AutoSizeRows()
            self.ForceRefresh()

    def _OnCut(self, event):
        self._OnCopy(event)
        self._OnDeleteValue(event)

    def _OnInsertUp(self, event):
        # 实现向上插入功能
        top_left, bottom_right = self._selected_range
        num = bottom_right[0] - top_left[0] + 1
        self.dataBase.InsertRows(top_left[0], num)
        # self.AutoSizeRows()
        self.ForceRefresh()

    def _OnInsertDown(self, event):
        # 实现向下插入功能
        top_left, bottom_right = self._selected_range
        num = bottom_right[0] - top_left[0] + 1
        self.dataBase.InsertRows(bottom_right[0] + 1, num)
        # self.AutoSizeRows()
        self.ForceRefresh()

    def _OnInsertLeft(self, event):
        # 实现向左插入功能
        top_left, bottom_right = self._selected_range
        num = bottom_right[1] - top_left[1] + 1
        self.dataBase.InsertCols(top_left[1], num)
        # self.AutoSizeRows()
        self.ForceRefresh()

    def _OnInsertRight(self, event):
        # 实现向右插入功能
        top_left, bottom_right = self._selected_range
        num = bottom_right[1] - top_left[1] + 1
        self.dataBase.InsertCols(bottom_right[1] + 1, num)
        # self.AutoSizeRows()
        self.ForceRefresh()

    def _OnDeleteValue(self, event):
        # 实现删除功能
        top_left, bottom_right = self._selected_range
        for i in range(top_left[0], bottom_right[0] + 1):
            for j in range(top_left[1], bottom_right[1] + 1):
                self.dataBase.data[i][j] = ''
        self.dataBase.ValuesGeted()
        self.ForceRefresh()

    def _OnDeleteRows(self, event):
        top_left, bottom_right = self._selected_range
        num = bottom_right[0] - top_left[0] + 1
        self.dataBase.DeleteRows(top_left[0], num)

    def _OnDeleteCols(self, event):
        top_left, bottom_right = self._selected_range
        num = bottom_right[1] - top_left[1] + 1
        self.dataBase.DeleteCols(top_left[1], num)

#endregion

#tag 实现并覆盖内部方法

    def AppendCols(self, numCols: int = 1, updateLabels: bool = True):
        b = self.dataBase.AppendCols(numCols)
        # self.AutoSizeRows()
        if updateLabels:
            self.ForceRefresh()
        return b

    def AppendRows(self, numRows: int = 1, updateLabels: int = True):
        b = self.dataBase.AppendRows(numRows)
        # self.AutoSizeRows()
        if updateLabels:
            self.ForceRefresh()
        return b

    def InsertCols(self,
                   pos: int,
                   numCols: int = 1,
                   updateLabels: bool = True):
        b = self.dataBase.InsertCols(pos, numCols)
        # self.AutoSizeRows()
        if updateLabels:
            self.ForceRefresh()
        return b

    def InsertRows(self,
                   pos: int,
                   numRows: int = 1,
                   updateLabels: bool = True):
        b = self.dataBase.InsertRows(pos, numRows)
        # self.AutoSizeRows()
        if updateLabels:
            self.ForceRefresh()
        return b

    def DeleteCols(self,
                   pos: int,
                   numCols: int = 1,
                   updateLabels: bool = True):
        b = self.dataBase.DeleteCols(pos, numCols)
        if updateLabels:
            self.ForceRefresh()
        return b

    def DeleteRows(self,
                   pos: int,
                   numRows: int = 1,
                   updateLabels: bool = True):
        b = self.dataBase.DeleteRows(pos, numRows)
        if updateLabels:
            self.ForceRefresh()
        return b
