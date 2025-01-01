# -*- coding: utf-8 -*-
from typing import Union, Sequence

import wx
import wx.richtext as rt
from wx.lib.embeddedimage import PyEmbeddedImage


class RichTextBase(wx.Frame):
    """
    Rich Text Base Class

    Attributes
    ----------
    rtc : `wx.richtext.RichTextCtrl`
        The rich text control.

    Methods
    -------
    set_text()
        Set the text codes of `self.rtc`.
    write(text, colour=None, fontsize=None, bold=False, italic=False, underline=False, new=1)
        Write text to `self.rtc` with style options.
    write_img(img_b64, new=1)
        Write an image to `self.rtc`.

    Notes
    -----
    - The `set_text` method must be implemented in a subclass.
    - Default font family is 'Microsoft Yahei', default font size is 12px.
    """

    def __init__(self, parent, title='', size=(800, 600)) -> None:
        super(RichTextBase, self).__init__(parent, title=title, size=size)

        self.CreateStatusBar()  # 在底部创建状态栏
        self.SetStatusText(title)  # 设置状态栏文本并更新状态栏显示
        self.rtc = rt.RichTextCtrl(
            self, style=wx.TE_READONLY)  # wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|
        self.rtc.SetFont(
            wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                    wx.FONTWEIGHT_NORMAL, False, 'Microsoft Yahei'))
        # attr = self.rtc.GetDefaultStyleEx()
        # attr.SetParagraphSpacingAfter(1 * attr.GetParagraphSpacingAfter())
        # attr.SetParagraphSpacingBefore(2 * attr.GetParagraphSpacingBefore())
        # self.rtc.SetDefaultStyle(attr)

        self.rtc.Freeze()
        self.rtc.BeginSuppressUndo()  # 开始禁止命令的撤消历史记录
        self.rtc.BeginParagraphSpacing(0, 10)
        self.set_text()
        self.rtc.EndParagraphSpacing()  # 结束段落间距
        self.rtc.EndSuppressUndo()  # 结束禁止撤消命令历史记录
        self.rtc.Thaw()

    def set_text(self) -> None:
        """这里放置文本内容代码"""
        raise NotImplementedError

    def _func_style(self, f, method, *args):

        def ff(text):
            getattr(self.rtc, f'Begin{method}')(*args)
            f(text)
            getattr(self.rtc, f'End{method}')()

        return ff

    def write(self,
              text: str,
              colour: Union[wx.Colour, Sequence[int], str, None] = None,
              fontsize: Union[int, None] = None,
              bold: Union[bool, None] = False,
              italic: Union[bool, None] = False,
              underline: Union[bool, None] = False,
              new: int = 1) -> None:
        """
        Write text to the RichTextCtrl with style options.

        Parameters
        ----------
        text : str
            The text to write.
        colour : `wx.Colour` or array of RGB or str or None, default None
            The colour of the text. If None, the default colour is used.
        fontsize : int or None, default None
            The font size of the text. If None, the default font size is used.
        bold : bool, default False
            Whether to make the text bold.
        italic : bool, default False
            Whether to make the text italic.
        underline : bool, default False
            Whether to underline the text.
        new : int, default 1
            The number of newlines to add after the text.
        """

        def func(text):
            self.rtc.WriteText(text)

        if colour:
            func = self._func_style(func, 'TextColour', colour)
        if fontsize:
            func = self._func_style(func, 'FontSize', fontsize)
        if bold:
            func = self._func_style(func, 'Bold')
        if italic:
            func = self._func_style(func, 'Italic')
        if underline:
            func = self._func_style(func, 'Underline')

        func(text)
        for _ in range(new):
            self.rtc.Newline()

    def write_img(self, img_b64: str, new: int = 1) -> None:
        """
        Write an image to the RichTextCtrl.

        Parameters
        ----------
        img_b64 : str
            The image encoded as a base64 string.
        new : int, default 1
            The number of newlines to add after the image.
        """
        self.rtc.WriteText('\t')
        self.rtc.WriteImage(PyEmbeddedImage(img_b64).GetBitmap())
        for _ in range(new):
            self.rtc.Newline()
