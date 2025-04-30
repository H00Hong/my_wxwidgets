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
from collections import defaultdict
from itertools import count, takewhile
from typing import (Dict, Iterable, List, Literal, Optional, Sequence, Tuple,
                    overload)

import wx.dataview as dv

__updated__ = '2025-4-30'


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
    __slots__ = ['_ids', 'data']

    def __init__(self, ids: Tuple[int, ...], data: List[str]) -> None:
        self._ids = self._validate_ids(ids)
        self.data = data
        # data [name, type, size, value]

    def _validate_ids(self, ids):
        if not all([isinstance(x, int) for x in ids]):
            raise TypeError('DataRow: All ids must be integers')
        return tuple(ids)

    @property
    def ids(self) -> Tuple[int, ...]:
        return self._ids

    @ids.setter
    def ids(self, ids: Sequence[int]) -> None:
        self._ids = self._validate_ids(ids)

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
    node_children: Dict[Optional[int], List[int]]
    _ncol: int
    _lid_max: int
    _oid_counter: count

    def __init__(self, data: Sequence[DataRow], resort: bool = False) -> None:
        super(DataViewModel, self).__init__()

        self.SetDataRows(data, resort)

    def _init_args(self) -> None:
        self.data = {}
        self.mapper = {}
        self.index_oid = {}
        self._lid_max = 0
        self._ncol = 0
        self._oid_counter = count(1)  # 0 id 的 DataViewItem 会被判定为根节点

    def _gen_oid(self):
        count = next(self._oid_counter)
        if count <= sys.maxsize:
            return count
        if count < sys.maxsize*2:
            return - count % sys.maxsize
        raise ValueError('DataViewModel: oid is too large')

    def SetDataRows(self, data: Sequence[DataRow], resort: bool = False):
        """使用 `Sequence[DataRow]` 为数据源重新设置数据."""
        if not isinstance(data, Sequence):
            raise TypeError('DataViewModel.SetDataRows: data must be `Sequence`')
        if not all(isinstance(dr, DataRow) for dr in data):
            raise TypeError('DataViewModel.SetDataRows: data must be `DataRow`')
        self._init_args()
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
        oid = self._gen_oid()
        self.data[oid] = datarow
        self.mapper[oid] = dv.DataViewItem(oid)
        self.index_oid[datarow.ids] = oid
        return oid

    def _check_datarow(self, datarow: DataRow) -> None:
        if not isinstance(datarow, DataRow):
            raise TypeError(
                'DataViewModel.AppendDataRow: data must be `DataRow`')
        if datarow.lid > self._lid_max:
            raise ValueError(
                'DataViewModel.AppendDataRow: data length must be \
greater than `lid_max`'                       )
        if len(datarow) != self._ncol:
            raise ValueError(
                'DataViewModel.AppendDataRow: data ColumnCount length \
must be equal'              )

    def _init_children(self) -> None:
        # SetDataRows 之后运行
        self.node_children = {}
        if not self.data:
            return
        drs = sorted(self.data.values(), key=lambda dr: (dr.lid, dr.ids))
        get_oid_with_index = lambda a: [self.index_oid[dr.ids] for dr in a]
        child_dr: List[list[DataRow]] = []
        processed_len = 0
        for i in range(1, self._lid_max + 1):
            lv_child_dr = list(takewhile(lambda dr: dr.lid == i, drs[processed_len:]))
            processed_len += len(lv_child_dr)
            child_dr.append(lv_child_dr)
        # 将所有 lid==1 的 item 做为根节点的子节点
        self.node_children[None] = get_oid_with_index(child_dr[0])
        if len(child_dr) == 1:
            return
        # 将所有末节点的子节点设置为[]
        for dr in child_dr[-1]:
            self.node_children.setdefault(self.index_oid[dr.ids], [])
        # 添加所有中间层的子节点
        for i in range(len(child_dr)-1):
            lv_root_dr = child_dr[i]
            lv_chil_dr = child_dr[i+1]
            processed_len = 0
            for dr in lv_root_dr:
                arr = get_oid_with_index(takewhile(
                    lambda x: x.ids[:dr.lid] == dr.ids, lv_chil_dr[processed_len:]))
                self.node_children[self.index_oid[dr.ids]] = arr
                processed_len += len(arr)

    def AppendDataRow(self, datarow: DataRow) -> None:
        """添加单个 `DataRow` 到数据模型."""
        self._check_datarow(datarow)
        oid = self._append_datarow(datarow)
        self.node_children[oid] = []
        parent_id = self.GetParentId(oid)
        self.node_children[parent_id].append(oid)
        if parent_id is None:
            parent = dv.NullDataViewItem
        else:
            parent = self.mapper[parent_id]
        self.ItemAdded(parent, self.mapper[oid])

    def AppendDataRows(self, datarows: Iterable[DataRow]) -> None:
        """添加多个 `DataRow` 到数据模型."""
        if not datarows:  # 空输入保护
            return
        parent_map: defaultdict[dv.DataViewItem, List[dv.DataViewItem]] = defaultdict(list)
        child_map: defaultdict[dv.DataViewItem, List[int]] = defaultdict(list)
        for dr in datarows:
            self._check_datarow(dr)
            oid = self._append_datarow(dr)
            item = self.mapper[oid]
            parent = self.GetParent(item)
            parent_map[parent].append(item)
            child_map[parent].append(oid)

        # 添加子节点
        for parent, items in child_map.items():
            for item in items:
                self.node_children.setdefault(item, [])
            self.node_children[self.GetItemId(parent)].extend(items)

        assert parent_map, 'No parent found'
        # 通知数据模型  添加子节点
        if len(parent_map) == 1:
            parent, items = parent_map.popitem()
            self.ItemsAdded(parent, items)
        else:
            for parent, items in parent_map.items():
                dv_arr = dv.DataViewItemArray()  # type: ignore
                for item in items:
                    # 没有 extend
                    dv_arr.append(item)  # type: ignore
                self.ItemsAdded(parent, dv_arr)

    def SortDataRows(self) -> None:
        """对现有的 `DataRow` 进行排序."""
        idx, drs = zip(*sorted(enumerate(self.data.values()),
                               key=lambda x: x[1]))
        self._set_SortDataRows(idx, drs)

    def _set_SortDataRows(self, idx: List[int], drs) -> None:
        oids = list(self.data.keys())
        self.data = {oids[i]: dr for i, dr in zip(idx, drs)}
        self.index_oid = {dr.ids: oid for oid, dr in self.data.items()}

    def ResortDataRows(self) -> None:
        """对现有的 `DataRow` 进行检查序号的重新排序."""
        idx, drs = zip(*sorted(enumerate(self.data.values()),
                               key=lambda x: x[1]))
        self._set_SortDataRows(idx, sort_drs(drs))

    def RemoveItem(self, item: dv.DataViewItem) -> None:
        """删除指定的 DataViewItem"""
        oid = self.GetItemId(item)
        self.ItemDeleted(self.GetParent(item), item)
        del self.index_oid[self.data[oid].ids]
        del self.data[oid]
        del self.mapper[oid]
        self.node_children[oid].clear()

    def GetNodeInfo(self, oid: Optional[int] = None, item: Optional[dv.DataViewItem] = None,
                    index: Optional[Tuple[int, ...]] = None):
        """
        获取指定节点的详细信息.

        Parameters
        ----------
        oid : int, optional
            节点唯一标识符。若提供则直接查询该节点信息
        item : dv.DataViewItem, optional
            DataView组件项对象。若提供则转换为oid后查询
        index : Tuple[int,...], optional
            树形结构索引路径。若提供则转换为oid后查询

        Returns
        -------
        dict
            包含节点完整信息的字典，包含以下键：
            - oid: 节点唯一标识符
            - item: 对应的DataViewItem对象
            - index: 节点的层级索引路径
            - datarow: 节点关联的数据对象
            - parent: 父节点oid（通过_get_parent方法获取）
            - children: 子节点oid列表
            - container: 是否包含多个子节点的容器标记

        Notes
        -----
        三个参数互斥，优先级顺序为 oid > item > index
        """
        if oid is not None:
            return {
                'oid': oid,
                'item': self.mapper[oid],
                'index': self.data[oid].ids,
                'datarow': self.data[oid],
                'parent': self.GetParentId(oid),
                'children': self.node_children[oid],
                'container': len(self.node_children[oid]) != 1
            }
        if item is not None:
            oid = self.GetItemId(item)
            return self.GetNodeInfo(oid=oid)
        if index is not None:
            oid = self.index_oid[index]
            return self.GetNodeInfo(oid=oid)

    def GetItemId(self, item: dv.DataViewItem) -> int:
        """获取指定的 `DataViewItem` 的 ID."""
        return get_itemid(item)

    def GetItemWithIndex(self, index: Tuple[int, ...]) -> dv.DataViewItem:
        """获取索引`Tuple[int,...]`对应的 `DataViewItem`.
        若索引为空 则返回 `NullDataViewItem`."""
        if not index:
            return dv.NullDataViewItem
        return self.mapper[self.index_oid[index]]

    def GetItemIdWithIndex(self, index: Optional[Tuple[int, ...]]) -> Optional[int]:
        """获取索引`Tuple[int,...]`对应的 `DataViewItem` 的 ID.
        若索引为空 则返回 `None`."""
        if not index:
            return
        return self.index_oid[index]

    def GetDataRowWithIndex(self, index: Tuple[int, ...]) -> DataRow:
        """获取索引`Tuple[int,...]`对应的 `DataRow`."""
        return self.data[self.index_oid[index]]

    def GetDataRows(self) -> List[DataRow]:
        """获取所有的 `DataRow` 的列表."""
        return list(self.data.values())

    def GetDataRow(self, item: dv.DataViewItem) -> DataRow:
        """获取 `DataViewItem` 对应的 `DataRow`."""
        return self.data[self.GetItemId(item)]

    def GetValues(self, item: dv.DataViewItem) -> Optional[List[str]]:
        """获取 `DataViewItem` 对应的 `DataRow` 的值. 如果没有对应则返回 `None`."""
        if not item:
            return None
        return self.GetDataRow(item).data

    def GetColumnCount(self) -> int:
        return self._ncol

    def GetColumnType(self, col):
        return 'str'

    @overload
    def GetChildArr(self, oid: Optional[int] = None, item: Optional[dv.DataViewItem] = None,
                    index: Optional[Tuple[int, ...]] = None, reteurn_item: Literal[False]=False) -> List[int]:        ...
    @overload
    def GetChildArr(self, oid: Optional[int] = None, item: Optional[dv.DataViewItem] = None,
                    index: Optional[Tuple[int, ...]] = None, reteurn_item: Literal[True]=True) -> List[dv.DataViewItem]:        ...
    def GetChildArr(self, oid: int = None, item: dv.DataViewItem = None,
                    index: Tuple[int, ...] = None, reteurn_item: bool = False):
        """
        获取子节点列表.

        Parameters
        ----------
        oid : int, optional
            节点唯一标识符。若提供则直接查询该节点信息
        item : dv.DataViewItem, optional
            DataView 组件项对象。若提供则转换为oid后查询
        index : Tuple[int,...], optional
            树形结构索引路径。若提供则转换为oid后查询
        return_item : bool, optional
            是否返回 `DataViewItem` 对象，默认为 `False`。
            若为 `True`，则返回 `DataViewItem` 对象列表，否则返回 `int` 对应的 `oid` 列表。

        Returns
        -------
        list
            对应的子节点列表.
            默认返回根节点的子节点列表.

        Notes
        -----
        三个参数互斥，优先级顺序为 oid > item > index
        """
        if oid is not None:
            pass
        elif item is not None:
            if not item:
                oid = None
            else:
                oid = self.GetItemId(item)
        elif index is not None:
            oid = self.index_oid[index]
        res = self.node_children[oid]
        if reteurn_item:
            res = [self.mapper[i] for i in res]
        return res

    def GetChildren(self, parent: dv.DataViewItem, children) -> int:
        """查找 `parent`(`DataViewItem`) 节点的子节点, 并放入 `children` 中.

        Parameters
        ----------
        parent : DataViewItem
            所要查找的节点
        children : array-like(带`append`方法)
            子节点列表
            使用`children`的`append`方法添加`DataViewItem`

            给`DataViewCtrl`调用时传入`DataViewItemArray`

        Returns
        -------
        int
            子节点数量
        """
        # print('GetChildren')
        if not parent:
            oid = None
        else:
            oid = self.GetItemId(parent)
        child_oid = self.node_children[oid]
        for i in child_oid:
            children.append(self.mapper[i])
        return len(child_oid)

    def IsContainer(self, item: dv.DataViewItem) -> bool:
        """判断 `item`(`DataViewItem`) 是否有子节点."""
        # print('IsContainer')
        if not item:
            return True
        return len(self.node_children[self.GetItemId(item)]) != 0

    def _get_parent_idx(self, dr_idx: Tuple[int, ...]) -> Optional[Tuple[int, ...]]:
        idx = dr_idx[:-1]
        # if len(idx) == 0:
        #     return
        if isinstance(idx, int):
            idx = (idx, )
        return idx

    def GetParentId(self, oid: int) -> Optional[int]:
        """返回项目(`oid`) 的父项 ID. 若父项不存在则返回 `None`."""
        if oid not in self.data:
            return
        return self.GetItemIdWithIndex(self._get_parent_idx(self.data[oid].ids))

    def GetParent(self, item: dv.DataViewItem) -> dv.DataViewItem:
        """返回 `item`(`DataViewItem`) 的父项(`DataViewItem`)."""
        # print('GetParent')
        if not item:
            return dv.NullDataViewItem
        dr = self.GetDataRow(item)
        return self.GetItemWithIndex(self._get_parent_idx(dr.ids))

    def HasContainerColumns(self, item):
        return True

    def HasValue(self, item, col):
        if get_itemid(item) in self.data and col < self._ncol:
            return True
        return False

    def GetValue(self, item: dv.DataViewItem, col: int):
        """返回 `item`(`DataViewItem`) 的 `col` 列的值, 如果不存在返回 `None`.
        `DataViewCtrl` 调用此方法显示值."""
        # print('GetValue')
        if not item:
            return None
        return self.GetDataRow(item).data[col]

    def SetValue(self, value, item: dv.DataViewItem, col: int) -> bool:
        """设置 `item`(`DataViewItem`) 的 `col` 列的值为 `value`, 返回是否更改成功."""
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
        """改变 `item`(`DataViewItem`) 的 `col` 列的值为 `value`, 等价于 `SetValue`."""
        return self.SetValue(value, item, col)


__all__ = ['DataViewModel', 'DataRow', 'dv', 'get_itemid']
