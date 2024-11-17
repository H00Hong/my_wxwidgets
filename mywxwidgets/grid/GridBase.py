# -*- coding: utf-8 -*-
"""
自定义Grid基类

Grid
    鼠标右键菜单和键盘快捷键--复制、粘贴、剪切、插入、删除、清除

GridWithHeader
    带表头的 Grid  两个 Grid 的组合
"""
from typing import List, Tuple, Callable, Optional, Iterable

import wx
import wx.grid as gridlib


def build_empty(rows: int, cols: int) -> List[List[str]]:
    return [[''] * cols for _ in range(rows)]


FONT0 = (14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
         False, 'Microsoft Yahei')
FONT1 = (16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
         False, 'Microsoft Yahei')


class DataBase(gridlib.GridTableBase):  # 基类
    """
    
    """

    data: List[list]
    rowlabels: Optional[List[str]]
    collabels: Optional[List[str]]

    def __init__(self):
        gridlib.GridTableBase.__init__(self)

        _cls = type(self)
        for method in ('GetNumberRows', 'GetNumberCols', 'SetDataFunc',
                       'SetValueFunc', 'GetValueFunc', 'DeleteRowsFunc',
                       'InsertRowsFunc', 'AppendRowsFunc', 'DeleteColsFunc',
                       'InsertColsFunc', 'AppendColsFunc'):
            # The abc module cannot be used
            # check abstractmethod
            if not (hasattr(_cls, method) and callable(getattr(_cls, method))
                    and getattr(DataBase, method, None) != getattr(
                        _cls, method)):
                raise NotImplementedError(f'not implement {method}')

#region abstractmethod

    def GetNumberRows(self) -> int:
        """
        Override this method to return the number of rows in your data.
        
        Returns
        -----
        int
            The number of rows in your data.
        
        example
        -------
        >>> def GetNumberRows(self):
        >>>     return len(self.data)
        """
        ...

    def GetNumberCols(self) -> int:
        """
        Override this method to return the number of columns in your data.
        
        Returns
        -----
        int
            The number of columns in your data.
        
        example
        -------
        >>> def GetNumberCols(self):
        >>>     return len(self.data[0])
        """
        ...

    def SetDataFunc(self, data):
        """
        Override this method to set the entire data set.
        Typically, a data check will be performed here.

        Parameters
        ----------
        data : array-like
            self.data
        
        Returns
        ------
        array-like ndim == 2
            The outgoing array will be used to assign 
            values to `self.data`, which will be passed 
            to other methods, the array dimensions must be 2

        example
        -------
        >>> def SetDataFunc(self, data):
        >>>     if not isinstance(data, list):
        >>>         raise TypeError('data type must be list')
        >>>     if any([not isinstance(i, list) for i in data]):
        >>>         raise TypeError('data type must be list[list]')
        >>>     return data
        """
        ...

    def SetValueFunc(self, data, row: int, col: int, value):
        """
        Override this method to set the value of the cell at the given row and
        col. The value is expected to be a string.

        Parameters
        ----------
        data : array-like
            `self.data` will be passed here
        row : int
            The row index of the cell.
        col : int
            The column index of the cell.
        value : str or any
            The value of the cell. If called from the GUI, this will be a string.

        example
        -------
        >>> def SetValueFunc(self, data, row: int, col: int, value):
        >>>     data[row][col] = value
        """
        ...

    def GetValueFunc(self, data, row: int, col: int) -> str:
        """
        Override this method to get the value of the cell at the given row and
        col. The returned value is expected to be a string.

        Parameters
        ----------
        data : array-like
            `self.data` will be passed here
        row : int
            The row index of the cell.
        col : int
            The column index of the cell.

        Returns
        -------
        str
            The value of the cell as a string.

        example
        -------
        >>> def GetValueFunc(self, data, row: int, col: int) -> str:
        >>>     return str(data[row][col])
        """
        ...

    def DeleteRowsFunc(self, data, pos: int, numRows: int = 1):
        """
        Override this method to delete the rows at the given position.

        Parameters
        ----------
        data : array-like
            `self.data` will be passed here
        pos : int
            The starting row index to delete.
        numRows : int, optional
            The number of rows to delete. Default is 1.

        Returns
        -------
        The modified data.

        Notes
        -----
        The returned data must have the same structure as the input data.
        
        example
        -------
        >>> # if isinstance(data, list)
        >>> def DeleteRowsFunc(self, data, pos: int, numRows: int = 1):
        >>>     return data[:pos] + data[pos + numRows:]
        >>>
        >>> # if isinstance(data, ndarray)
        >>> def DeleteRowsFunc(self, data, pos: int, numRows: int = 1):
        >>>     return np.delete(data, list(range(pos, pos + numRows)), axis=0)
        """
        ...

    def InsertRowsFunc(self, data, pos: int, numRows: int = 1):
        """
        Override this method to insert the rows at the given position.

        Parameters
        ----------
        data : array-like
            `self.data` will be passed here
        pos : int
            The starting row index to insert.
        numRows : int, optional
            The number of rows to insert. Default is 1.

        Returns
        -------
        The modified data.

        Notes
        -----
        The returned data must have the same structure as the input data.
        
        example
        -------
        >>> # if isinstance(data, list)
        >>> def InsertRowsFunc(self, data, pos: int, numRows: int = 1):
        >>>     ncols = len(data[0])
        >>>     empty = [[''] * ncols for _ in range(numRows)]
        >>>     return data[:pos] + empty + data[pos:]
        >>>
        >>> # if isinstance(data, ndarray)
        >>> def InsertRowsFunc(self, data, pos: int, numRows: int = 1):
        >>>     empty = np.array([[''] * data.shape[1] for _ in range(numRows)]) 
        >>>     return np.insert(data, pos, empty, axis=0)
        """
        ...

    def AppendRowsFunc(self, data, numRows: int = 1):
        """
        Override this method to append the specified number of rows to the data.

        Parameters
        ----------
        data : array-like
            `self.data` will be passed here
        numRows : int, optional
            The number of rows to append. Default is 1.

        Returns
        -------
        The modified data.

        Notes
        -----
        The returned data must have the same structure as the input data.

        example
        -------
        >>> # if isinstance(data, list)
        >>> def AppendRowsFunc(self, data, numRows: int = 1):
        >>>     ncols = len(data[0])
        >>>     return data + [[''] * ncols for _ in range(numRows)]
        >>>
        >>> # if isinstance(data, ndarray)
        >>> def AppendRowsFunc(self, data, numRows: int = 1):
        >>>     empty = np.array([[''] * data.shape[1] for _ in range(numRows)])
        >>>     return np.append(data, empty, axis=0)
        """
        ...

    def DeleteColsFunc(self, data, pos: int, numCols: int = 1):
        """
        Override this method to delete the specified number of columns from the data.

        Parameters
        ----------
        data : array-like
            `self.data` will be passed here
        pos : int
            The starting column index to delete.
        numCols : int, optional
            The number of columns to delete. Default is 1.

        Returns
        -------
        The modified data.

        Notes
        -----
        The returned data must have the same structure as the input data.

        example
        -------
        >>> # if isinstance(data, list)
        >>> def DeleteColsFunc(self, data, pos: int, numCols: int = 1):
        >>>
        >>>     def list_transpose(data):
        >>>         return [list(i) for i in zip(*data)]
        >>>
        >>>     dat = list_transpose(data)
        >>>     dat_ = dat[:pos] + dat[pos + numCols:]
        >>>     return list_transpose(dat_)
        >>>
        >>> # if isinstance(data, ndarray)
        >>> def DeleteColsFunc(self, data, pos: int, numCols: int = 1):
        >>>     return np.delete(data, list(range(pos, pos + numCols)), axis=1)
        """
        ...
        ...

    def InsertColsFunc(self, data, pos: int, numCols: int = 1):
        """
        Override this method to insert the specified number of columns into the data at the given position.

        Parameters
        ----------
        data : array-like
            `self.data` will be passed here
        pos : int
            The starting column index to insert.
        numCols : int, optional
            The number of columns to insert. Default is 1.

        Returns
        -------
        The modified data.

        Notes
        -----
        The returned data must have the same structure as the input data.

        example
        -------
        >>> # if isinstance(data, list)
        >>> def InsertColsFunc(self, data, pos: int, numCols: int = 1):
        >>>
        >>>     def list_transpose(data):
        >>>         return [list(i) for i in zip(*data)]
        >>>
        >>>     nrows = len(data)
        >>>     empty = [[''] * nrows for _ in range(numCols)]
        >>>     dat = list_transpose(data)
        >>>     dat_ = dat[:pos] + empty + dat[pos:]
        >>>     return list_transpose(dat_)
        >>>
        >>> # if isinstance(data, ndarray)
        >>> def InsertColsFunc(self, data, pos: int, numCols: int = 1):
        >>>     empty = np.array([[''] * data.shape[0] for _ in range(numCols)])
        >>>     return np.insert(data, pos, empty, axis=1)
        """
        ...

    def AppendColsFunc(self, data, numCols: int = 1):
        """
        Override this method to append the specified number of columns to the data.

        Parameters
        ----------
        data : array-like
            `self.data` will be passed here
        numCols : int, optional
            The number of columns to append. Default is 1.

        Returns
        -------
        The modified data.

        Notes
        -----
        The returned data must have the same structure as the input data.

        example
        -------
        >>> # if isinstance(data, list)
        >>> def AppendColsFunc(self, data, numCols: int = 1):
        >>>
        >>>     def list_transpose(data):
        >>>         return [list(i) for i in zip(*data)]
        >>>
        >>>     nrows = len(data)
        >>>     empty = [[''] * nrows for _ in range(numCols)]
        >>>     dat = list_transpose(data)
        >>>     return list_transpose(dat + empty)
        >>>
        >>> # if isinstance(data, ndarray)
        >>> def AppendColsFunc(self, data, numCols: int = 1):
        >>>     empty = np.array([[''] * data.shape[1] for _ in range(numCols)])
        >>>     return np.append(data, empty, axis=0)
        """
        ...

#endregion

#region ProcessTableMessage

    def ValuesUpdated(self) -> None:  # 更新数据
        # print('GetValues')
        self.GetView().ProcessTableMessage(
            gridlib.GridTableMessage(
                self, gridlib.GRIDTABLE_REQUEST_VIEW_GET_VALUES))

    def RowsDeleted(self, pos: int, numRows: int) -> None:
        self.GetView().ProcessTableMessage(
            gridlib.GridTableMessage(self,
                                     gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED,
                                     pos, numRows))

    def RowsAppended(self, numRows: int) -> None:
        self.GetView().ProcessTableMessage(
            gridlib.GridTableMessage(self,
                                     gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED,
                                     numRows))

    def RowsInserted(self, pos: int, numRows: int) -> None:
        self.GetView().ProcessTableMessage(
            gridlib.GridTableMessage(self,
                                     gridlib.GRIDTABLE_NOTIFY_ROWS_INSERTED,
                                     pos, numRows))

    def ColsDeleted(self, pos: int, numCols: int) -> None:
        self.GetView().ProcessTableMessage(
            gridlib.GridTableMessage(self,
                                     gridlib.GRIDTABLE_NOTIFY_COLS_DELETED,
                                     pos, numCols))

    def ColsAppended(self, numCols: int) -> None:
        self.GetView().ProcessTableMessage(
            gridlib.GridTableMessage(self,
                                     gridlib.GRIDTABLE_NOTIFY_COLS_APPENDED,
                                     numCols))

    def ColsInserted(self, pos: int, numCols: int) -> None:
        self.GetView().ProcessTableMessage(
            gridlib.GridTableMessage(self,
                                     gridlib.GRIDTABLE_NOTIFY_COLS_INSERTED,
                                     pos, numCols))


#endregion

    def GetValue(self, row: int, col: int) -> str:
        """
        Returns the value of the cell at the given row and col.

        Parameters
        ----------
        row : int
            The row index of the cell.
        col : int
            The column index of the cell.

        Returns
        -------
        str
            The value of the cell as a string.

        Notes
        -----
        If the cell contains an error, the method returns an empty string.
        """
        try:
            return self.GetValueFunc(self.data, row, col)
        except:
            return ''

    def SetData(self, data) -> None:
        """
        Replaces the current dataset with the provided data and updates the grid accordingly.

        This function first retrieves the current number of rows and columns in the dataset.
        It then replaces the dataset by calling `SetDataFunc(data)` and updates the number
        of rows and columns. If the number of rows or columns has changed, the function
        sends the appropriate notifications to update the grid view.
        """
        old_rows, old_cols = self.GetNumberRows(), self.GetNumberCols()
        self.data = self.SetDataFunc(data)
        new_rows, new_cols = self.GetNumberRows(), self.GetNumberCols()
        if old_rows > new_rows:
            self.RowsDeleted(0, old_rows - new_rows)
        elif old_rows < new_rows:
            self.RowsAppended(new_rows - old_rows)
        if old_cols > new_cols:
            self.ColsDeleted(0, old_cols - new_cols)
        elif old_cols < new_cols:
            self.ColsAppended(new_cols - old_cols)
        self.ValuesUpdated()

    def SetDataValue(self, row: int, col: int, value) -> None:
        """
        Set the value of the cell at the given row and col.

        Parameters
        ----------
        row : int
            The row index of the cell.
        col : int
            The column index of the cell.
        value: any
            The value of the cell. This can be anything that can be
            converted to a string.
        
        raises
        ------
        IndexError
            If the row or col is out of range
        """
        self.SetValueFunc(self.data, row, col, value)
        self.ValuesUpdated()

    def SetValue(self, row: int, col: int, value) -> None:
        """
        Set the value of the cell at the given row and col.

        If the row or col is out of range, the grid will be resized to
        accommodate the new cell.

        Parameters
        ----------
        row : int
            The row index of the cell.
        col : int
            The column index of the cell.
        value : str or any
            The value of the cell. This can be anything that can be
            converted to a string. If called from the GUI, this will be a string.
        """
        nrows, ncols = self.GetNumberRows(), self.GetNumberCols()
        if col > ncols:
            self.AppendCols(col + 1 - ncols)
        if row > nrows:
            self.AppendRows(row + 1 - nrows)
        self.SetValueFunc(self.data, row, col, value)
        self.ValuesUpdated()

    def SetRowLabels(self, rowlables: Iterable) -> None:
        """
        Set the row labels of the grid. The row labels are the values that
        appear in the row header of the grid.

        Parameters
        ----------
        rowlables : Iterable
            The values of the row labels. This can be any iterable of objects
            that can be converted to a string.

        Raises
        ------
        TypeError
            If `rowlables` is not an iterable.
        """
        if isinstance(rowlables, Iterable):
            raise TypeError('rowlables must be Iterable')
        self.rowlabels = [str(i) for i in rowlables]

    def SetRowLabelValue(self, row: int, label: str) -> bool:
        """
        Set the value of the row label at the given row index.

        Parameters
        ----------
        row : int
            The row index of the row label.
        label : str
            The value of the row label.

        Returns
        -------
        bool
            True if successful, False otherwise. If `self.rowlabels` is None or
            `label` is not a string, returns False.
        """
        if self.rowlabels is None:
            print('rowlabels is None, cannot set row label')
            return False
        if isinstance(label, str):
            self.rowlabels[row] = label
            return True
        print('label is not a string')
        return False

    def GetRowLabelValue(self, row: int) -> str:
        """
        Get the value of the row label at the given row index.

        Parameters
        ----------
        row : int
            The row index of the row label.

        Returns
        -------
        str
            The value of the row label. If `self.rowlabels` is None, returns the
            result of calling the base class's GetRowLabelValue method.

        """
        if self.rowlabels:
            return self.rowlabels[row]
        return super().GetRowLabelValue(row)

    def SetColLabels(self, collabels: Iterable) -> None:
        """
        Set the column labels of the grid. The column labels are the values that
        appear in the column header of the grid.

        Parameters
        ----------
        collabels : Iterable
            The values of the column labels. This can be any iterable of objects
            that can be converted to a string.

        Raises
        ------
        TypeError
            If `collabels` is not an iterable.
        """
        if isinstance(collabels, Iterable):
            raise TypeError('collabels must be Iterable')
        self.collabels = [str(i) for i in collabels]

    def SetColLabelValue(self, col: int, label: str) -> bool:
        """
        Set the value of the column label at the given column index.

        Parameters
        ----------
        col : int
            The column index of the column label.
        label : str
            The value of the column label.

        Returns
        -------
        bool
            True if successful, False otherwise. If `self.collabels` is None or
            `label` is not a string, returns False.
        """
        if self.collabels is None:
            print('collabels is None, cannot set column label')
            return False
        if isinstance(label, str):
            self.collabels[col] = label
            return True
        print('label is not a string')
        return False

    def GetColLabelValue(self, col: int) -> str:
        """
        Get the value of the column label at the given column index.

        Parameters
        ----------
        col : int
            The column index of the column label.

        Returns
        -------
        str
            The value of the column label. If `self.collabels` is None, returns the
            result of calling the base class's GetColLabelValue method.
        """
        if self.collabels:
            return self.collabels[col]
        return super().GetColLabelValue(col)

    def IsEmptyCell(self, row: int, col: int) -> bool:
        """
        Check if the cell at the given row and column index is empty.

        Parameters
        ----------
        row : int
            The row index of the cell.
        col : int
            The column index of the cell.

        Returns
        -------
        bool
            True if the cell is empty, False otherwise. A cell is considered
            empty if it is either None or a string that is empty.
        """
        item = self.GetValue(row, col)
        return item == '' or item is None

    def DeleteRows(self, pos: int, numRows: int = 1) -> bool:
        """
        Delete the rows at the given position.

        Parameters
        ----------
        pos : int
            The starting row index to delete.
        numRows : int, optional
            The number of rows to delete. Default is 1.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        try:
            self.data = self.DeleteRowsFunc(self.data, pos, numRows)
            self.RowsDeleted(pos, numRows)
            return True
        except Exception as e:
            print(e)
            return False

    def DeleteCols(self, pos: int, numCols: int = 1) -> bool:
        """
        Delete the columns at the given position.

        Parameters
        ----------
        pos : int
            The starting column index to delete.
        numCols : int, optional
            The number of columns to delete. Default is 1.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        try:
            self.data = self.DeleteColsFunc(self.data, pos, numCols)
            self.ColsDeleted(pos, numCols)
            return True
        except Exception as e:
            print(e)
            return False

    def AppendRows(self, numRows: int = 1) -> bool:
        """
        Append the specified number of rows to the table.

        Parameters
        ----------
        numRows : int, optional
            The number of rows to append. Default is 1.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        try:
            self.data = self.AppendRowsFunc(self.data, numRows)
            self.RowsAppended(numRows)
            self.ValuesUpdated()
            return True
        except Exception as e:
            print(e)
            return False

    def AppendCols(self, numCols: int = 1) -> bool:
        """
        Append the specified number of columns to the table.

        Parameters
        ----------
        numCols : int, optional
            The number of columns to append. Default is 1.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        try:
            self.data = self.AppendColsFunc(self.data, numCols)
            self.ColsAppended(numCols)
            self.ValuesUpdated()
            return True
        except Exception as e:
            print(e)
            return False

    def InsertCols(self, pos: int, numCols: int = 1) -> bool:
        """
        Insert the specified number of columns at the given position.

        Parameters
        ----------
        pos : int
            The starting column index to insert.
        numCols : int, optional
            The number of columns to insert. Default is 1.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        try:
            self.data = self.InsertColsFunc(self.data, pos, numCols)
            self.ColsInserted(pos, numCols)
            self.ValuesUpdated()
            return True
        except Exception as e:
            print(e)
            return False

    def InsertRows(self, pos: int, numRows: int = 1) -> bool:
        """
        Insert the specified number of rows at the given position.

        Parameters
        ----------
        pos : int
            The starting row index to insert.
        numRows : int, optional
            The number of rows to insert. Default is 1.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        try:
            self.data = self.InsertRowsFunc(self.data, pos, numRows)
            self.RowsInserted(pos, numRows)
            self.ValuesUpdated()
            return True
        except Exception as e:
            print(e)
            return False

    def Clear(self) -> None:
        """
        Clear the data in the grid.

        This method sets the data to a fresh empty array of the same shape as the current data.
        It then calls ValuesUpdated to notify the grid that the data has changed.
        """
        self.data = self.SetDataFunc(build_empty(self.GetNumberRows(), self.GetNumberCols()))
        self.ValuesUpdated()


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

    def __init__(
            self,
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
        self._init_menu()

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

    def _init_menu(self):
        # 创建一个右键菜单
        self.popupmenu = wx.Menu()
        # 绑定左键选择事件 获取选中区域
        self._selected_range: Tuple[Tuple[int, int],
                                    Tuple[int, int]] = ((0, 0), (0, 0))
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
            self._selected_range = (event.GetTopLeftCoords(),
                                    event.GetBottomRightCoords())
        # else:
        #     self._selected_range = None

    def _OnLeftClick(self, event):
        # 获取被点击的行和列
        row: int = event.GetRow()
        col: int = event.GetCol()
        self._selected_range = ((row, col), (row, col))
        event.Skip()
        # print(self._selected_range)

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

        def set_selected():  # 将点击的单元格作为新的选定区域
            self.SelectBlock(row, col, row, col)
            self._selected_range = ((row, col), (row, col))

        if self._selected_range:
            top_left, bottom_right = self._selected_range
            if (row < top_left[0] or row > bottom_right[0] or col < top_left[1]
                    or col > bottom_right[1]):  # 如果点击的单元格不在 _selected_range 内
                set_selected()
            # print(f"之前选定的区域从第{top_left[0]}行，第{top_left[1]}列到第{bottom_right[0]}行，第{bottom_right[1]}列")
        else:
            # print("没有之前选定的区域")
            set_selected()

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
        lst_ = [map(str, it[top_left[1]:bottom_right[1] + 1]) for it in lst]
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
            self.dataBase.ValuesUpdated()  # 通知数据已经更新
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
        self.dataBase.ValuesUpdated()
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
        """
        Append the specified number of columns to the grid.

        Parameters
        ----------
        numCols : int, optional
            The number of columns to append. Default is 1.
        updateLabels : bool, optional
            If True, refreshes the grid labels after appending columns. Default is True.

        Returns
        -------
        bool
            True if the columns were successfully appended, False otherwise.
        """
        b = self.dataBase.AppendCols(numCols)
        # self.AutoSizeRows()
        if updateLabels:
            self.ForceRefresh()
        return b

    def AppendRows(self, numRows: int = 1, updateLabels: int = True):
        """
        Append the specified number of rows to the grid.

        Parameters
        ----------
        numRows : int, optional
            The number of rows to append. Default is 1.
        updateLabels : bool, optional
            If True, refreshes the grid labels after appending rows. Default is True.

        Returns
        -------
        bool
            True if the rows were successfully appended, False otherwise.
        """
        b = self.dataBase.AppendRows(numRows)
        # self.AutoSizeRows()
        if updateLabels:
            self.ForceRefresh()
        return b

    def InsertCols(self,
                   pos: int,
                   numCols: int = 1,
                   updateLabels: bool = True):
        """
        Insert the specified number of columns at the given position.

        Parameters
        ----------
        pos : int
            The starting column index to insert.
        numCols : int, optional
            The number of columns to insert. Default is 1.
        updateLabels : bool, optional
            If True, refreshes the grid labels after inserting columns. Default is True.

        Returns
        -------
        bool
            True if the columns were successfully inserted, False otherwise.
        """
        b = self.dataBase.InsertCols(pos, numCols)
        # self.AutoSizeRows()
        if updateLabels:
            self.ForceRefresh()
        return b

    def InsertRows(self,
                   pos: int,
                   numRows: int = 1,
                   updateLabels: bool = True):
        """
        Insert the specified number of rows at the given position.

        Parameters
        ----------
        pos : int
            The starting row index to insert.
        numRows : int, optional
            The number of rows to insert. Default is 1.
        updateLabels : bool, optional
            If True, refreshes the grid labels after inserting rows. Default is True.

        Returns
        -------
        bool
            True if the rows were successfully inserted, False otherwise.
        """
        b = self.dataBase.InsertRows(pos, numRows)
        # self.AutoSizeRows()
        if updateLabels:
            self.ForceRefresh()
        return b

    def DeleteCols(self,
                   pos: int,
                   numCols: int = 1,
                   updateLabels: bool = True):
        """
        Delete the columns at the given position.

        Parameters
        ----------
        pos : int
            The starting column index to delete.
        numCols : int, optional
            The number of columns to delete. Default is 1.
        updateLabels : bool, optional
            If True, refreshes the grid labels after deleting columns. Default is True.

        Returns
        -------
        bool
            True if the columns were successfully deleted, False otherwise.
        """

        b = self.dataBase.DeleteCols(pos, numCols)
        if updateLabels:
            self.ForceRefresh()
        return b

    def DeleteRows(self,
                   pos: int,
                   numRows: int = 1,
                   updateLabels: bool = True):
        """
        Delete the rows at the given position.

        Parameters
        ----------
        pos : int
            The starting row index to delete.
        numRows : int, optional
            The number of rows to delete. Default is 1.
        updateLabels : bool, optional
            If True, refreshes the grid labels after deleting rows. Default is True.

        Returns
        -------
        bool
            True if the rows were successfully deleted, False otherwise.
        """

        b = self.dataBase.DeleteRows(pos, numRows)
        if updateLabels:
            self.ForceRefresh()
        return b
