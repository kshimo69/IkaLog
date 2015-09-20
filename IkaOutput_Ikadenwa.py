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

from IkaUtils import *
from datetime import datetime
import time

## IkaLog Output Plugin: Show message on Console
#
class IkaOutput_Ikadenwa:

	def onLobbyMatched(self, context):
		# ToDo: もし使えるのなら全プレイヤーの情報(ランク、名前のハッシュ的なもの)をイカデンワに送信
		# イカデンワ側でのユーザマッチングに利用してもらう 

	def onGameStart(self, context):
		# ゲーム開始でステージ名、ルール名が表示されたタイミング

		# ToDo: いったん全員ミュート

        def onTeamColor(self, context):
                # チームカラーが判明したらイカデンワに報告する
		my_color = context['game']['color'][0]

		# ToDo: イカデンワに色を通知(してミュートを解除してほしい)
		#       色情報は整数値(HSV) の Hue 、整数値で送信する
		#       ±20度ぐらいでおなじ色を持っているプレイヤーとマッチングして
		#       自動的にミュートを解除してもらえると OK

	def onGameFinished(self, context):
		# まだないコールバック
		# ゲーム終了が検出できたらできるだけ早くこのコールバックが呼ばれるようにする

		# ToDo: イカデンワの Mute 解除

	def onGameIndividualResult(self, context):
		# いまでもあるコールバック
		# このタイミングでミュートだとちょっと遅い
