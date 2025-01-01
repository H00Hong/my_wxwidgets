# -*- coding: utf-8 -*-
"""
自定义 DataViewModel

- DataRow (class)
    自定义 DataRow 数据类型
    使用 Tuple[int,...] 为数据的 ID 表示在view中的位置
    使用 List[str] 为数据的内容

- DataViewModel (class)
    自定义 DataViewModel 数据类型
    使用 Sequence[DataRow] 为数据源

- get_itemid (function)
    获取指定的 DataViewItem 的 ID

"""
import sys
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import wx.dataview as dv


class DataRow:
    """
    用于存储 DataViewModel 中的数据
    以行为单位

    Attributes
    ----------
    ids: Tuple[int, ...]
        数据行的 id , 可接受一个整数序列
    data: List[str]
        数据行的值, 应为一个字符串列表

    Methods
    -------
    lid -- property
        id 的级别 即 length
    __len__()
        data 的长度
    __getitem__(index)
        data 的索引
    __setitem__(index, value)
        data 的索引赋值
    """

    def __init__(self, ids: Tuple[int, ...], data: List[str]) -> None:
        self._ids = tuple(ids)
        if not all([isinstance(x, str) for x in data]):
            raise TypeError('data must be a list of strings')
        self.data = data
        # data [name, type, size, value]

    __slots__ = ['_ids', 'data']

    @property
    def ids(self) -> Tuple[int, ...]:
        return self._ids

    @ids.setter
    def ids(self, ids: Sequence[int]) -> None:
        self._ids = tuple(ids)

    @property
    def lid(self) -> int:
        """id 的级别 即 length"""
        return len(self._ids)

    def __len__(self) -> int:
        return len(self.data)

    def __hash__(self):
        return hash((self._ids, self.data))

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index: int, value: str) -> None:
        self.data[index] = value

    def __repr__(self) -> str:
        return f'DataRow(ids={self._ids},\n\tdata={self.data})'

    __str__ = __repr__

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DataRow):
            return False
        return self.ids == other.ids

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, DataRow):
            return True
        return self.ids != other.ids

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, DataRow):
            raise TypeError
        return self.ids < other.ids

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, DataRow):
            raise TypeError
        return self.ids > other.ids

    def __le__(self, other: object) -> bool:
        if not isinstance(other, DataRow):
            raise TypeError
        return self.ids <= other.ids

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, DataRow):
            raise TypeError
        return self.ids >= other.ids


def compare_dr(dr1: DataRow, dr2: DataRow) -> None:
    dr1ids = dr1.ids
    dr2ids = dr2.ids
    dr1lid = dr1.lid
    dr2lid = dr2.lid
    if dr1lid == dr2lid:
        if dr1ids[:-1] != dr2ids[:-1] or dr1ids[-1] + 1 != dr2ids[-1]:
            index = dr1ids[:dr1lid - 1] + (dr1ids[-1] + 1, )
            dr2.ids = index

    elif dr1lid < dr2lid:
        if dr1ids[:dr1lid] != dr2ids[:dr1lid] or dr2ids[-1] != 0:
            index = dr1ids + (0, )
            dr2.ids = index

    else:  # dr1.lid > dr2.lid:
        dr2lid_ = dr2lid - 1
        if dr1ids[:dr2lid_] != dr2ids[:dr2lid_] or dr1ids[
                dr2lid_] != dr2ids[-1] + 1:
            index = dr1ids[:dr2lid_] + (dr1ids[dr2lid_] + 1, )
            dr2.ids = index


def sort_drs(_drs: Sequence[DataRow]):
    """对 dataRow 列表 进行排序并重新编号"""
    if not _drs:
        print('sort_datarow: null set')
        return []
    drs = sorted(_drs)
    if drs[0].ids != (0, ):
        drs[0].ids = (0, )
    for i in range(1, len(drs)):
        compare_dr(drs[i - 1], drs[i])

    return drs


def get_itemid(item: dv.DataViewItem) -> int:
    """获取指定的 DataViewItem 的 ID"""
    return int(item.GetID())


class DataViewModel(dv.DataViewModel):

    data: Dict[int, DataRow]
    mapper: Dict[int, dv.DataViewItem]
    container: Dict[int, bool]
    index_oid: Dict[Tuple[int, ...], int]
    _ncol: int
    _lid_max: int

    def __init__(self, data: Sequence[DataRow], resort: bool = False) -> None:
        dv.DataViewModel.__init__(self)

        self.SetDataRows(data, resort)

    def SetDataRows(self, data: Sequence[DataRow], resort: bool = False):
        """使用 Sequence[DataRow] 为数据源重新设置数据"""
        if not isinstance(data, Sequence):
            raise TypeError('DataViewModel.SetDataRows: data must be Sequence')
        if not all(isinstance(dr, DataRow) for dr in data):
            raise TypeError('DataViewModel.SetDataRows: data must be DataRow')
        self.data = {}
        self.mapper = {}
        self.container = {}
        self.index_oid = {}
        self._lid_max = 0
        if resort:
            _dat = sort_drs(data)
        else:
            _dat = sorted(data)
        ncol = []
        for v in _dat:
            self._append_datarow(v)
            if v.lid > self._lid_max:
                self._lid_max = v.lid
            ncol.append(len(v))

        if len(set(ncol)) == 1:
            self._ncol = ncol[0]
        elif len(set(ncol)) > 1:
            raise ValueError(
                'DataViewModel: data ColumnCount length must be equal')

        self.check_all_container(True)

    def _append_datarow(self, datarow: DataRow) -> int:
        oid = id(datarow)
        while oid > sys.maxsize:
            oid -= sys.maxsize
        self.data[oid] = datarow
        self.mapper[oid] = dv.DataViewItem(oid)
        self.index_oid[datarow.ids] = oid
        return oid

    def _check_datarow(self, datarow: DataRow) -> None:
        if not isinstance(datarow, DataRow):
            raise TypeError(
                'DataViewModel.AppendDataRow: data must be dataRow')
        if datarow.lid > self._lid_max:
            raise ValueError(
                'DataViewModel.AppendDataRow: data length must be \
greater than lid_max')
        if len(datarow) != self._ncol:
            raise ValueError(
                'DataViewModel.AppendDataRow: data ColumnCount length \
must be equal')

    def AppendDataRow(self, datarow: DataRow) -> None:
        """添加单个 DataRow 到数据模型"""
        self._check_datarow(datarow)
        oid = self._append_datarow(datarow)
        self.check_all_container()
        self.ItemAdded(self.GetParent(self.mapper[oid]), self.mapper[oid])

    def AppendDataRows(self, datarows: Iterable[DataRow]) -> None:
        """添加多个 DataRow 到数据模型"""
        parents, items = [], []
        for dr in datarows:
            self._check_datarow(dr)
            oid = self._append_datarow(dr)
            item = self.mapper[oid]
            parents.append(self.GetParent(item))
            items.append(item)

        self.check_all_container()
        parent = list(set(parents))
        assert len(parent) != 0, 'No parent found'
        if len(parent) == 1:
            self.ItemsAdded(parent[0], items)
        else:
            for p in parent:
                _items = dv.DataViewItemArray()  # type: ignore
                for pp in parents:
                    if pp == p:
                        _items.append(items[parents.index(pp)])
                self.ItemsAdded(p, _items)

    def check_all_container(self, isSorted: bool = False) -> None:
        if isSorted:
            dat = list(self.data.values())
        else:
            dat = sorted(list(self.data.values()))
        if not self.data:
            return
        for oid, dr in self.data.items():
            if dr.lid == self._lid_max:
                self.container[oid] = False
                continue

            id = dr.ids
            for it in dat:
                id_ = it.ids
                if id_[:dr.lid] == id:
                    if id_ > id:
                        self.container[oid] = True
                        break
                    elif id == id_:  # 针对最后一个节点没有子节点的情况
                        self.container[oid] = False
                elif id_[:dr.lid] > id:
                    self.container[oid] = False
                    break

    def SortDataRows(self) -> None:
        """对现有的 DataRow 进行排序"""
        idx, drs = zip(
            *sorted(enumerate(self.data.values()), key=lambda x: x[1]))
        self._set_SortDataRows(idx, drs)

    def _set_SortDataRows(self, idx: List[int], drs) -> None:
        oids = list(self.data.keys())
        z = zip([oids[i] for i in idx], drs)
        self.data = dict(z)
        self.index_oid = {dr.ids: oid for oid, dr in z}

    def ResortDataRows(self) -> None:
        """对现有的 DataRow 进行检查序号的重新排序"""
        idx, drs = zip(
            *sorted(enumerate(self.data.values()), key=lambda x: x[1]))
        self._set_SortDataRows(idx, sort_drs(drs))

    def RemoveItem(self, item: dv.DataViewItem) -> None:
        """删除指定的 DataViewItem"""
        oid = self.GetItemId(item)
        self.ItemDeleted(self.GetParent(item), item)
        del self.index_oid[self.data[oid].ids]
        del self.data[oid]
        del self.mapper[oid]
        del self.container[oid]

    def GetItemId(self, item: dv.DataViewItem) -> int:
        """获取指定的 DataViewItem 的 ID"""
        return get_itemid(item)

    def GetItemWithIndex(self, index: Tuple[int, ...]) -> dv.DataViewItem:
        """获取索引Tuple[int,...]对应的 DataViewItem"""
        return self.mapper[self.index_oid[index]]

    def GetDataRowWithIndex(self, index: Tuple[int, ...]) -> DataRow:
        """获取索引Tuple[int,...]对应的 DataRow"""
        return self.data[self.index_oid[index]]

    def GetDataRows(self) -> List[DataRow]:
        """获取所有的 DataRow 的列表"""
        return list(self.data.values())

    def GetDataRow(self, item: dv.DataViewItem) -> DataRow:
        """获取 DataViewItem 对应的 DataRow"""
        return self.data[self.GetItemId(item)]

    def GetValues(self, item: dv.DataViewItem) -> Optional[List[str]]:
        """获取 DataViewItem 对应的 DataRow 的值, 如果没有对应则返回 None"""
        if not item:
            return None
        return self.GetDataRow(item).data

    def GetColumnCount(self) -> int:
        return self._ncol

    def GetColumnType(self, col):
        return 'str'

    def GetChildren(self, parent: dv.DataViewItem, children) -> int:
        """查找 parent(DataViewItem) 节点的子节点, 并放入 children 中

        Parameters
        ----------
        parent: DataViewItem
            所要查找的节点
        children: array-like(带`append`方法)
            子节点列表
            使用`children`的`append`方法添加`DataViewItem`

            给`DataViewCtrl`调用时传入`DataViewItemArray`

        Returns
        -------
        int
            子节点数量
        """
        # print('GetChildren')
        n = 0
        if not parent:
            for k, v in self.data.items():
                if v.lid == 1:
                    children.append(self.mapper[k])
                    n += 1
            return n

        oid = self.GetItemId(parent)
        node = self.data[oid]
        n_ind = node.lid
        if n_ind < self._lid_max:
            for k, item in self.data.items():
                if item.lid == n_ind + 1 and item.ids[:n_ind] == node.ids:
                    children.append(self.mapper[k])
                    n += 1
        return n

    def IsContainer(self, item: dv.DataViewItem) -> bool:
        """判断 item(DataViewItem) 是否有子节点"""
        # print('IsContainer')
        if not item:
            return True
        try:
            return self.container[self.GetItemId(item)]
        except Exception as e:
            print(e)
            return False

    def GetParent(self, item: dv.DataViewItem) -> dv.DataViewItem:
        """返回 item(DataViewItem) 的父项(DataViewItem)"""
        # print('GetParent')
        if not item:
            return dv.NullDataViewItem
        node = self.GetDataRow(item)
        if node.lid != 1:
            idx = node.ids[:-1]
            if isinstance(idx, int):
                idx = (idx, )
            for k, v in self.data.items():
                if v.ids == idx:
                    return self.mapper[k]
            print('GetParent: item not found')
        return dv.NullDataViewItem

    def HasContainerColumns(self, item):
        return True

    def HasValue(self, item, col):
        if get_itemid(item) in self.data and col < self._ncol:
            return True
        return False

    def GetValue(self, item: dv.DataViewItem, col: int):
        """返回 item(DataViewItem) 的 col 列的值, 如果不存在返回 None.
        DataViewCtrl 调用此方法显示值"""
        # print('GetValue')
        if not item:
            return None
        node = self.GetDataRow(item)
        return node[col]

    def SetValue(self, value, item: dv.DataViewItem, col: int) -> bool:
        """设置 item(DataViewItem) 的 col 列的值为 value, 返回是否更改成功"""
        # print('SetValue')
        if not item:
            return False
        try:
            oid = self.GetItemId(item)
            self.data[oid][col] = value
            self.ValueChanged(item, col)  # 通知视图值已更改
            self.ItemChanged(item)  # 通知视图值已更改
            return True
        except Exception as e:
            print(e)
            return False

    def ChangeValue(self, value, item: dv.DataViewItem, col: int) -> bool:
        """改变 item(DataViewItem) 的 col 列的值为 value, 等价于 SetValue"""
        return self.SetValue(value, item, col)


__all__ = ['DataViewModel', 'DataRow', 'dv', 'get_itemid']
