# -*- coding: utf-8 -*-
import wx
import wx.richtext as rt
from wx.lib.embeddedimage import PyEmbeddedImage


class RichTextBase(wx.Frame):

    def __init__(self, parent, title='', size=(800, 600)) -> None:
        wx.Frame.__init__(self, parent, title=title, size=size)

        self.CreateStatusBar() # 在底部创建状态栏
        self.SetStatusText(title) # 设置状态栏文本并更新状态栏显示
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

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.rtc, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

    def set_text(self) -> None:
        raise NotImplementedError

    def _func_style(self, f, method, *args):
        def ff(text):
            getattr(self.rtc, f'Begin{method}')(*args)
            f(text)
            getattr(self.rtc, f'End{method}')()
        return ff

    def _write(self,
               text: str,
               colour=None,
               font=None,
               bold=False,
               italic=False,
               underline=False,
               new: int = 1) -> None:

        def func(text):
            self.rtc.WriteText(text)

        if colour:
            func = self._func_style(func, 'TextColour', colour)
        if font:
            func = self._func_style(func, 'FontSize', font)
        if bold:
            func = self._func_style(func, 'Bold')
        if italic:
            func = self._func_style(func, 'Italic')
        if underline:
            func = self._func_style(func, 'Underline')

        func(text)
        for _ in range(new):
            self.rtc.Newline()

    def _write_img(self, img: str, new: int = 1) -> None:
        self.rtc.WriteText('\t')
        self.rtc.WriteImage(PyEmbeddedImage(img).GetBitmap())
        for _ in range(new):
            self.rtc.Newline()


if __name__ == '__main__':

    polynomial = "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"

    class Example(RichTextBase):

        def set_text(self):
            w = self._write
            red = (255, 0, 0)
            blue = (0, 0, 255)
            purple = (170, 85, 255)

            w('默认字体')
            w('加粗', bold=True, new=0)
            w('18号', font=18, new=0)
            w('蓝色', colour=blue, new=0)
            w('下划线', underline=True, new=0)
            w('斜体', italic=True)
            w('蓝色18号加粗下划线斜体', bold=True, font=18, colour=blue, underline=True, italic=True)
            w('center'.center(30, '-'), blue)
            w('\t制表符')
            self.rtc.Newline()
            self._write_img(polynomial)

    app = wx.App()
    Example(None, '色度计算和转换操作说明').Show()
    app.MainLoop()
