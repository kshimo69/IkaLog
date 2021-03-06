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

import cv2
import os
import numpy as np

from ikalog.utils.character_recoginizer import *
from ikalog.utils import *


class UdemaeRecoginizer(CharacterRecoginizer):

    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, '__instance__'):
            cls.__instance__ = super(
                UdemaeRecoginizer, cls).__new__(cls, *args, **kwargs)

        return cls.__instance__

    def __init__(self):

        if hasattr(self, 'trained') and self.trained:
            return

        super(UdemaeRecoginizer, self).__init__()

        model_name = 'data/udemae.model'
        if os.path.isfile(model_name):
            self.load_model_from_file(model_name)
            self.train()
            return

        IkaUtils.dprint('Building udemae recoginization model.')
        data = [
            {'file': 'numbers2/a1.png', 'response': 'a'},
            {'file': 'numbers2/b1.png', 'response': 'b'},
            {'file': 'numbers2/c1.png', 'response': 'c'},
            {'file': 'numbers2/s1.png', 'response': 's'},
            {'file': 'numbers2/s2.png', 'response': 's'},
            {'file': 'numbers2/plus.png', 'response': '+'},
            {'file': 'numbers2/minus.png', 'response': '-'},
        ]

        for d in data:
            d['img'] = cv2.imread(d['file'])
            self.add_sample(d['response'], d['img'])
            self.add_sample(d['response'], d['img'])
            self.add_sample(d['response'], d['img'])
        self.save_model_to_file(model_name)

        self.train()

if __name__ == "__main__":
    UdemaeRecoginizer()
