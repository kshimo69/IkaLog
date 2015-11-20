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

from ikalog import inputs
from ikalog.utils import *
import wx

class VideoCapture(object):

    # アマレコTV のキャプチャデバイス名
    DEV_AMAREC = "AmaRec Video Capture"

    source = 'amarec'
    source_device = None
    deinterlace = False
    File = ''


    def read(self):
        if self.capture is None:
            return None, None

        r =  self.capture.read()
        return r

    def start_recorded_file(self, file):
        IkaUtils.dprint(
            '%s: initalizing pre-recorded video file %s' % (self, file))
        self.realtime = False
        self.from_file = True
        self.capture.init_capture(file)
        self.fps = self.capture.cap.get(5)


    def enumerate_devices(self):
        return inputs.CVCapture().enumerate_input_sources()

    def initialize_input(self):
        if self.source == 'camera':
            if 0: #IkaUtils.isOSX():
                self.capture = inputs.AVFoundationCapture()
            else:
                self.capture = inputs.CVCapture()
                self.capture.start_camera(self.source_device)

        elif self.source == 'screen':
            self.capture = inputs.ScreenCapture()
            self.capture.calibrate()

        elif self.source == 'amarec':
            self.capture = inputs.CVCapture()
            self.capture.start_camera(self.DEV_AMAREC)

        elif self.source == 'file':
            self.capture = inputs.CVFile()
            self.start_recorded_file(self.File)

        # ToDo reset context['engine']['msec']
        success = True

        return success

    def apply_ui(self):
        self.source = ''
        for control in [self.radioAmarecTV, self.radioCamera, self.radioScreen, self.radioFile]:
            if control.GetValue():
                self.source = {
                    self.radioAmarecTV: 'amarec',
                    self.radioCamera: 'camera',
                    self.radioFile: 'file',
                    self.radioScreen: 'screen',
                }[control]

        self.source_device = self.listCameras.GetItems(
        )[self.listCameras.GetSelection()]
        self.File = self.editFile.GetValue()
        self.deinterlace = self.checkDeinterlace.GetValue()

        # この関数は GUI 動作時にしか呼ばれない。カメラが開けなかった
        # 場合にメッセージを出す
        if not self.initialize_input():
            r = wx.MessageDialog(None, u'キャプチャデバイスの初期化に失敗しました。設定を見直してください', 'Error',
                                 wx.OK | wx.ICON_ERROR).ShowModal()
            IkaUtils.dprint(
                "%s: failed to activate input source >>>>" % (self))
        else:
            IkaUtils.dprint("%s: activated new input source" % self)

    def refresh_ui(self):
        if self.source == 'amarec':
            self.radioAmarecTV.SetValue(True)

        if self.source == 'camera':
            self.radioCamera.SetValue(True)

        if self.source == 'screen':
            self.radioScreen.SetValue(True)

        if self.source == 'file':
            self.radioFile.SetValue(True)

        try:
            dev = self.source_device
            index = self.listCameras.GetItems().index(dev)
            self.listCameras.SetSelection(index)
        except:
            IkaUtils.dprint('Current configured device is not in list')

        if not self.File is None:
            self.editFile.SetValue('')
        else:
            self.editFile.SetValue(self.File)

        self.checkDeinterlace.SetValue(self.deinterlace)

    def on_config_reset(self, context=None):
        # さすがにカメラはリセットしたくないな
        pass

    def on_config_load_from_context(self, context):
        self.on_config_reset(context)
        try:
            conf = context['config']['cvcapture']
        except:
            conf = {}

        self.source = ''
        try:
            if conf['Source'] in ['camera', 'file', 'amarec', 'screen']:
                self.source = conf['Source']
        except:
            pass

        if 'SourceDevice' in conf:
            try:
                self.source_device = conf['SourceDevice']
            except:
                # FIXME
                self.source_device = 0

        if 'File' in conf:
            self.File = conf['File']

        if 'Deinterlace' in conf:
            self.deinterlace = conf['Deinterlace']

        self.refresh_ui()
        return self.initialize_input()

    def on_config_save_to_context(self, context):
        context['config']['cvcapture'] = {
            'Source': self.source,
            'File': self.File,
            'SourceDevice': self.source_device,
            'Deinterlace': self.deinterlace,
        }

    def on_config_apply(self, context):
        self.apply_ui()

    def on_reload_devices_button_click(self, event=None):
        pass

    def on_calibrate_screen_button_click(self, event=None):
        if (self.capture is not None) and self.capture.__class__.__name__ == 'ScreenCapture':
            img = self.capture.read_raw()
            if img is not None:
                self.capture.auto_calibrate(img)

    def on_screen_reset_button_click(self, event=None):
        if (self.capture is not None) and self.capture.__class__.__name__ == 'ScreenCapture':
            self.capture.reset()

    def on_option_tab_create(self, notebook):
        is_windows = IkaUtils.isWindows()

        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.page = notebook.InsertPage(0, self.panel, 'Input')

        cameras = self.enumerate_devices()

        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)
        self.radioAmarecTV = wx.RadioButton(
            self.panel, wx.ID_ANY, u'Capture through AmarecTV')

        self.radioCamera = wx.RadioButton(
            self.panel, wx.ID_ANY, u'Realtime Capture from HDMI grabber')

        self.radioScreen = wx.RadioButton(
            self.panel, wx.ID_ANY, u'Realtime Capture from desktop')
        self.buttonCalibrateDesktop = wx.Button(
            self.panel, wx.ID_ANY, u'Calibrate')
        self.buttonEntireDesktop = wx.Button(
            self.panel, wx.ID_ANY, u'Reset')

        self.radioFile = wx.RadioButton(
            self.panel, wx.ID_ANY, u'Read from pre-recorded video file (for testing)')
        self.editFile = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
        self.listCameras = wx.ListBox(self.panel, wx.ID_ANY, choices=cameras)
        self.listCameras.SetSelection(0)
        self.buttonReloadDevices = wx.Button(
            self.panel, wx.ID_ANY, u'Reload Devices')
        self.checkDeinterlace = wx.CheckBox(
            self.panel, wx.ID_ANY, u'Enable Deinterlacing (experimental)')

        self.layout.Add(wx.StaticText(
            self.panel, wx.ID_ANY, u'Select Input source:'))
        self.layout.Add(self.radioAmarecTV)
        self.layout.Add(self.radioCamera)
        self.layout.Add(self.listCameras, flag=wx.EXPAND)
        self.layout.Add(self.buttonReloadDevices)
        self.layout.Add(self.radioScreen)
        buttons_layout = wx.BoxSizer(wx.HORIZONTAL)
        buttons_layout.Add(self.buttonCalibrateDesktop)
        buttons_layout.Add(self.buttonEntireDesktop)
        self.layout.Add(buttons_layout)
        self.layout.Add(self.radioFile)
        self.layout.Add(self.editFile, flag=wx.EXPAND)
        self.layout.Add(self.checkDeinterlace)
        self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'Video Offset'))

        if is_windows:
            self.radioAmarecTV.SetValue(True)

        else:
            self.radioCamera.SetValue(True)
            self.radioAmarecTV.Disable()
            self.radioScreen.Disable()
            self.buttonCalibrateDesktop.Disable()

        self.buttonReloadDevices.Bind(
            wx.EVT_BUTTON, self.on_reload_devices_button_click)
        self.buttonCalibrateDesktop.Bind(
            wx.EVT_BUTTON, self.on_calibrate_screen_button_click)
        self.buttonEntireDesktop.Bind(
            wx.EVT_BUTTON, self.on_screen_reset_button_click)

    def __init__(self):
        self.from_file = False
        self.capture = None

if __name__ == "__main__":
    pass
