#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import copy
import threading

import wx
import cv2


class PreviewPanel(wx.Panel):

    def SetEventHandlerEnable(self, obj, enable):
        orig_state = obj.GetEvtHandlerEnabled()
        obj.SetEvtHandlerEnabled(enable)
        return orig_state

    def on_frame_read(self, context):
        self.lock.acquire()
        self.latest_frame = cv2.resize(context['engine']['frame'], (640, 360))
        self.refresh_at_next = True
        self.lock.release()

    def OnResize(self, event):
        w, h = self.GetClientSizeTuple()
        new_height = int((w * 720) / 1280)

        orig_state = self.SetEventHandlerEnable(self, False)
        self.SetSize((w, new_height))
        self.SetEventHandlerEnable(self, orig_state)

    def OnPaint(self, event):
        self.lock.acquire()
        if self.latest_frame is None:
            self.lock.release()
            return

        width = 640
        height = 360

        frame_rgb = cv2.cvtColor(self.latest_frame, cv2.COLOR_BGR2RGB)
        self.lock.release()

        try:
            bmp = wx.Bitmap.FromBuffer(width, height, frame_rgb)
        except:
            bmp = wx.BitmapFromBuffer(width, height, frame_rgb)

        dc = wx.BufferedPaintDC(self)
        # dc.SetBackground(wx.Brush(wx.RED))

        dc.DrawBitmap(bmp, 0, 0)

    def OnTimer(self, event):
        self.lock.acquire()

        if self.latest_frame is None:
            self.lock.release()
            return

        self.lock.release()

        if not self.refresh_at_next:
            return

        self.Refresh()
        self.refresh_at_next = False

    def __init__(self, *args, **kwargs):
        self.refresh_at_next = False
        self.latest_frame = None
        self.lock = threading.Lock()

        wx.Panel.__init__(self, *args, **kwargs)
        self.timer = wx.Timer(self)
        self.timer.Start(100)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        # self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)


if __name__ == "__main__":
    import sys
    import wx

    application = wx.App()
    frame = wx.Frame(None, wx.ID_ANY, 'Preview', size=(640, 360))
    preview = PreviewPanel(frame, size=(640, 360))
    layout = wx.BoxSizer(wx.VERTICAL)
    layout.Add(preview)
    frame.SetSizer(layout)
    frame.Show()
    application.MainLoop()
