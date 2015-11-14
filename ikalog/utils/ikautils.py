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
from __future__ import print_function

import os
import platform
import re
import sys

import cv2
import numpy as np
from PIL import Image


class IkaUtils(object):

    @staticmethod
    def isWindows():
        try:
            os.uname()
        except AttributeError:
            return True
        return False

    @staticmethod
    def isOSX():
        return platform.system() == 'Darwin'

    @staticmethod
    def dprint(text):
        print(text, file=sys.stderr)

    @staticmethod
    def baseDirectory():
        base_directory = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        base_directory = re.sub('[\\/]+$', '', base_directory)

        if os.path.isfile(base_directory):
            # In this case, this version of IkaLog is py2exe'd,
            # and base_directory is still pointing at the executable.
            base_directory = os.path.dirname(base_directory)

        return base_directory

    # Find the local player.
    #
    # @param context   IkaLog Context.
    # @return The player information (Directionary class) if found.
    @staticmethod
    def getMyEntryFromContext(context):
        for e in context['game']['players']:
            if e['me']:
                return e
        return None

    # Get player's title.
    #
    # @param playerEntry The player.
    # @return Title in string. Returns None if playerEntry doesn't have title data.
    @staticmethod
    def playerTitle(playerEntry):
        if playerEntry is None:
            return None

        if not (('gender' in playerEntry) and ('prefix' in playerEntry)):
            return None

        prefix = re.sub('の', '', playerEntry['prefix'])
        return "%s%s" % (prefix, playerEntry['gender'])

    @staticmethod
    def map2text(map, unknown=None, lang="ja"):
        if map is None:
            if unknown is None:
                unknown = "?"
            return unknown
        return map.id_

    @staticmethod
    def rule2text(rule, unknown=None, lang="ja"):
        if rule is None:
            if unknown is None:
                unknown = "?"
            return unknown
        return rule.id_

    @staticmethod
    def cropImageGray(img, left, top, width, height):
        if len(img.shape) > 2 and img.shape[2] != 1:
            return cv2.cvtColor(
                img[top:top + height, left:left + width],
                cv2.COLOR_BGR2GRAY
            )
        return img[top:top + height, left:left + width]

    @staticmethod
    def matchWithMask(img, mask, threshold=99.0, orig_threshold=70.0, debug=False):
        if len(img.shape) > 2 and img.shape[2] != 1:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Check false-positive
        orig_hist = cv2.calcHist([img], [0], None, [3], [0, 256])
        match2 = orig_hist[2] / np.sum(orig_hist)

        if match2 > orig_threshold:
            # False-Positive condition.
            #print("original %f > orig_threshold %f" % (match2, orig_threshold))
            return False

        ret, thresh1 = cv2.threshold(img, 230, 255, cv2.THRESH_BINARY)
        added = thresh1 + mask
        hist = cv2.calcHist([added], [0], None, [3], [0, 256])

        match = hist[2] / np.sum(hist)

        if debug and (match > threshold):
            print("match2 %f match %f > threshold %f" %
                  (match2, match, threshold))
            cv2.imshow('match_img', img)
            cv2.imshow('match_mask', mask)
            cv2.imshow('match_added', added)
            # cv2.waitKey()

        return match > threshold

    @staticmethod
    def loadMask(file, left, top, width, height):
        mask = cv2.imread(file)
        if mask is None:
            print("マスクデータ %s のロードに失敗しました")
            # raise a exception

        mask = mask[top:top + height, left:left + width]

        # BGR to GRAY
        if mask.shape[2] > 1:
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

        return mask

    @staticmethod
    def getWinLoseText(won, win_text="勝ち", lose_text="負け", unknown_text="不明"):
        if won is None:
            return unknown_text
        return win_text if won else lose_text

    @staticmethod
    def writeScreenshot(destfile, img):
        img_pil = Image.fromarray(img[:, :, ::-1])

        try:
            img_pil.save(destfile)
            assert os.path.isfile(destfile)
        except:
            self.dprint("Screenshot: failed")
            return False
        return True
