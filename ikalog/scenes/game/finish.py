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

import sys
import cv2

from ikalog.utils import *
from ikalog.scenes.scene import Scene


class GameFinish(Scene):

    def reset(self):
        super(GameFinish, self).reset()

        self._last_event_msec = - 100 * 1000

    def match_no_cache(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine']['frame']

        matched = self.mask_finish.match(frame)

        if not matched:
            return False

        if not self.matched_in(context, 60 * 1000, attr='_last_event_msec'):
            self._call_plugins('on_game_finish')
            self._last_event_msec = context['engine']['msec']

        return matched

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self.mask_finish = IkaMatcher(
            0, 0, 1280, 720,
            img_file='masks/ui_finish.png',
            threshold=0.950,
            orig_threshold=0.05,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_WHITE(sat=(0, 255), visibility=(16, 255)),
            label='Finish',
            debug=debug,
        )

if __name__ == "__main__":
    GameFinish.main_func()
