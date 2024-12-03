# -*- coding: utf-8 -*-
import wx
import wx.richtext as rt
from wx.lib.embeddedimage import PyEmbeddedImage


class RichTextBase(wx.Frame):

    def __init__(self, parent, title='', size=(800, 600)) -> None:
        wx.Frame.__init__(self, parent, title=title, size=size)

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
        raise NotImplementedError

    def _func_style(self, f, method, *args):

        def ff(text):
            getattr(self.rtc, f'Begin{method}')(*args)
            f(text)
            getattr(self.rtc, f'End{method}')()

        return ff

    def write(self,
              text: str,
              colour=None,
              fontsize=None,
              bold=False,
              italic=False,
              underline=False,
              new: int = 1) -> None:

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
        self.rtc.WriteText('\t')
        self.rtc.WriteImage(PyEmbeddedImage(img_b64).GetBitmap())
        for _ in range(new):
            self.rtc.Newline()
