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

# @package IkaOutput_Twitter

import os
from datetime import datetime
import json

import cv2

from ikalog.utils import *


# Needed in GUI mode
try:
    import wx
except:
    pass

# IkaOutput_Twitter: IkaLog Output Plugin for Twitter
#
# Tweet Splatton game events.


class Twitter(object):

    # TODO
    _preset_ck = None
    _preset_cs = None

    # API Endpoint for Tweets
    url = "https://api.twitter.com/1.1/statuses/update.json"
    # API Endpoint for Medias (screenshots)
    url_media = "https://upload.twitter.com/1.1/media/upload.json"

    last_me = None

    def apply_ui(self):
        if self.radioIkaLogKey.GetValue():
            self.consumer_key_type = 'ikalog'
        if self.radioOwnKey.GetValue():
            self.consumer_key_type = 'own'
        if self._preset_ck is None:
            self.consumer_key_type = 'own'

        self.enabled = self.checkEnable.GetValue()
        self.attach_image = self.checkAttachImage.GetValue()
        self.tweet_kd = self.checkTweetKd.GetValue()
        self.tweet_my_score = self.checkTweetMyScore.GetValue()
        self.tweet_udemae = self.checkTweetUdemae.GetValue()
        self.use_reply = self.checkUseReply.GetValue()
        self.consumer_key = self.editConsumerKey.GetValue()
        self.consumer_secret = self.editConsumerSecret.GetValue()
        self.access_token = self.editAccessToken.GetValue()
        self.access_token_secret = self.editAccessTokenSecret.GetValue()
        self.footer = self.editFooter.GetValue()

    def on_consumer_key_mode_switch(self, event=None):
        if self._preset_ck is None:
            self.radioIkaLogKey.Disable()
            self.radioOwnKey.SetValue(True)
        else:
            self.radioIkaLogKey.Enable()

        if self.radioOwnKey.GetValue():
            self.editConsumerKey.Enable()
            self.editConsumerSecret.Enable()
            self.buttonIkaLogAuth.Disable()
        else:
            self.editConsumerKey.Disable()
            self.editConsumerSecret.Disable()
            self.buttonIkaLogAuth.Enable()

    def refresh_ui(self):
        self._internal_update = True
        self.checkEnable.SetValue(self.enabled)
        self.checkAttachImage.SetValue(self.attach_image)
        self.checkTweetKd.SetValue(self.tweet_kd)
        self.checkTweetMyScore.SetValue(self.tweet_my_score)
        self.checkTweetUdemae.SetValue(self.tweet_udemae)
        self.checkUseReply.SetValue(self.use_reply)

        try:
            {
                'ikalog': self.radioIkaLogKey,
                'own': self.radioOwnKey,
            }[self.consumer_key_type].SetValue(True)
        except:
            pass

        if not self.consumer_key is None:
            self.editConsumerKey.SetValue(self.consumer_key)
        else:
            self.editConsumerKey.SetValue('')

        if not self.consumer_secret is None:
            self.editConsumerSecret.SetValue(self.consumer_secret)
        else:
            self.editConsumerSecret.SetValue('')

        if not self.access_token is None:
            self.editAccessToken.SetValue(self.access_token)
        else:
            self.editAccessToken.SetValue('')

        if not self.access_token_secret is None:
            self.editAccessTokenSecret.SetValue(self.access_token_secret)
        else:
            self.editAccessTokenSecret.SetValue('')

        if not self.footer is None:
            self.editFooter.SetValue(self.footer)
        else:
            self.editFooter.SetValue('')
        self.on_consumer_key_mode_switch()
        self._internal_update = False

    def on_config_reset(self, context=None):
        self.enabled = False
        self.attach_image = False
        self.tweet_kd = False
        self.tweet_my_score = False
        self.tweet_udemae = False
        self.use_reply = True
        self.consumer_key_type = 'ikalog'
        self.consumer_key = ''
        self.consumer_secret = ''
        self.access_token = ''
        self.access_token_secret = ''
        self.footer = ''

    def on_config_load_from_context(self, context):
        self.on_config_reset(context)

        try:
            conf = context['config']['twitter']
        except:
            conf = {}

        if 'Enable' in conf:
            self.enabled = conf['Enable']

        if 'AttachImage' in conf:
            self.attach_image = conf['AttachImage']

        if 'TweetMyScore' in conf:
            self.tweet_my_score = conf['TweetMyScore']

        if 'TweetKd' in conf:
            self.tweet_kd = conf['TweetKd']

        if 'TweetUdemae' in conf:
            self.tweet_udemae = conf['TweetUdemae']

        if 'UseReply' in conf:
            self.use_reply = conf['UseReply']

        if 'ConsumerKeyType' in conf:
            self.consumer_key_type = conf['ConsumerKeyType']

        if 'ConsumerKey' in conf:
            self.consumer_key = conf['ConsumerKey']

        if 'ConsumerSecret' in conf:
            self.consumer_secret = conf['ConsumerSecret']

        if 'AccessToken' in conf:
            self.access_token = conf['AccessToken']

        if 'AccessTokenSecret' in conf:
            self.access_token_secret = conf['AccessTokenSecret']

        if 'Footer' in conf:
            self.footer = conf['Footer']

        self.refresh_ui()
        return True

    def on_config_save_to_context(self, context):
        context['config']['twitter'] = {
            'Enable': self.enabled,
            'AttachImage': self.attach_image,
            'TweetMyScore': self.tweet_my_score,
            'TweetKd': self.tweet_kd,
            'TweetUdemae': self.tweet_udemae,
            'UseReply': self.use_reply,
            'ConsumerKeyType': self.consumer_key_type,
            'ConsumerKey': self.consumer_key,
            'ConsumerSecret': self.consumer_secret,
            'AccessToken': self.access_token,
            'AccessTokenSecret': self.access_token_secret,
            'Footer': self.footer,
        }

    def on_config_apply(self, context):
        self.apply_ui()

        if not self.consumer_key_type is None:
            try:
                {
                    'ikalog': self.radioIkaLogKey,
                    'own': self.radioOwnKey,
                }[self.consumer_key_type].SetValue(True)
            except:
                if self._preset_ck is None:
                    self.radioOwnKey.SetValue(True)
                else:
                    self.radioIkaLogKey.SetValue(True)
        else:
            self.editConsumerKey.SetValue('')

        if not self.consumer_key is None:
            self.editConsumerKey.SetValue(self.consumer_key)
        else:
            self.editConsumerKey.SetValue('')

        if not self.consumer_secret is None:
            self.editConsumerSecret.SetValue(self.consumer_secret)
        else:
            self.editConsumerSecret.SetValue('')

        if not self.access_token is None:
            self.editAccessToken.SetValue(self.access_token)
        else:
            self.editAccessToken.SetValue('')

        if not self.access_token_secret is None:
            self.editAccessTokenSecret.SetValue(self.access_token_secret)
        else:
            self.editAccessTokenSecret.SetValue('')

        if not self.footer is None:
            self.editFooter.SetValue(self.footer)
        else:
            self.editFooter.SetValue('')

        self._internal_update = False

    def on_test_button_click(self, event):
        dlg = wx.TextEntryDialog(
            None, '投稿内容を入力してください', caption='投稿テスト', value='マンメンミ')
        r = dlg.ShowModal()
        s = dlg.GetValue()
        dlg.Destroy()

        if r != wx.ID_OK:
            return

        failure = False
        try:
            # FixMe: tweet() doesn't return result code
            self.tweet(s)
        except:
            failure = True

        # FixMe

    def on_ika_log_auth_button_click(self, event):
        from requests_oauthlib import OAuth1Session

        request_token_url = 'https://api.twitter.com/oauth/request_token'
        authorization_url = 'https://api.twitter.com/oauth/authorize'
        access_token_url = 'https://api.twitter.com/oauth/access_token'

        oauth_session = OAuth1Session(
            self._preset_ck, client_secret=self._preset_cs, callback_uri='oob')
        step1 = oauth_session.fetch_request_token(request_token_url)
        auth_web_url = oauth_session.authorization_url(authorization_url)

        msg = "Twitter の利用認証を行います。\n下記のURLをブラウザにペーストし、Twitterサイトで認証ページを開いてください。"

        dlg = wx.TextEntryDialog(
            None, msg, caption='OAuth認証', value=auth_web_url)
        r = dlg.ShowModal()
        dlg.Destroy()

        if r != wx.ID_OK:
            return

        msg = "Twitter サイトにて認証に成功すると PIN コードが表示されます。\n表示された PIN コードを下記に入力してください。"

        dlg = wx.TextEntryDialog(None, msg, caption='OAuth認証', value='')
        dlg.ShowModal()
        pin = dlg.GetValue()
        dlg.Destroy()

        if r != wx.ID_OK:
            return

        oauth_session.params['oauth_verifier'] = pin
        r = oauth_session.get('%s?oauth_token=%s' %
                              (access_token_url, step1['oauth_token']))

        d = oauth_session.parse_authorization_response('?' + r.text)
        AT = d['oauth_token']
        ATS = d['oauth_token_secret']

        self.radioIkaLogKey.SetValue(True)
        self.consumer_key_type = 'ikalog'
        self.access_token = AT
        self.access_token_secret = ATS
        self.ScreenName = d['screen_name']

        self.refresh_ui()

    def on_option_tab_create(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.page = notebook.InsertPage(0, self.panel, 'Twitter')
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)
        self.checkEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, u'Twitter へ戦績を通知する')
        self.checkAttachImage = wx.CheckBox(
            self.panel, wx.ID_ANY, u'戦績画面を画像添付する')
        self.checkTweetMyScore = wx.CheckBox(
            self.panel, wx.ID_ANY, u'自スコアを投稿する')
        self.checkTweetKd = wx.CheckBox(self.panel, wx.ID_ANY, u'K/D を投稿する')
        self.checkTweetUdemae = wx.CheckBox(
            self.panel, wx.ID_ANY, u'ウデマエを投稿する')
        self.checkUseReply = wx.CheckBox(
            self.panel, wx.ID_ANY, u'@_ikalog_ へのリプライとして投稿する (タイムラインを汚しません)')
        self.editFooter = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

        self.radioIkaLogKey = wx.RadioButton(
            self.panel, wx.ID_ANY, u'IkaLog内部キー')
        self.radioOwnKey = wx.RadioButton(self.panel, wx.ID_ANY, u'自分のキー')

        self.buttonIkaLogAuth = wx.Button(
            self.panel, wx.ID_ANY, u'Twitter 連携認証')
        self.buttonTest = wx.Button(
            self.panel, wx.ID_ANY, u'投稿テスト(反映済みの設定を使用します)')
        self.editConsumerKey = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
        self.editConsumerSecret = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
        self.editAccessToken = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
        self.editAccessTokenSecret = wx.TextCtrl(
            self.panel, wx.ID_ANY, u'hoge')

        try:
            layout = wx.GridSizer(2, 2)
        except:
            layout = wx.GridSizer(2)

        layout.Add(self.radioIkaLogKey)
        layout.Add(self.buttonIkaLogAuth)
        layout.Add(self.radioOwnKey)

        self.layout.Add(self.checkEnable)
        self.layout.Add(self.checkUseReply)
        self.layout.Add(self.checkAttachImage)
        self.layout.Add(self.checkTweetMyScore)
        self.layout.Add(self.checkTweetKd)
        self.layout.Add(self.checkTweetUdemae)
        self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'フッタ'))

        self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'使用するAPIキー'))
        self.layout.Add(layout)

        self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'Consumer Key'))
        self.layout.Add(self.editConsumerKey, flag=wx.EXPAND)
        self.layout.Add(wx.StaticText(
            self.panel, wx.ID_ANY, u'Consumer Key Secret'))
        self.layout.Add(self.editConsumerSecret, flag=wx.EXPAND)
        self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'Access Token'))
        self.layout.Add(self.editAccessToken, flag=wx.EXPAND)
        self.layout.Add(wx.StaticText(
            self.panel, wx.ID_ANY, u'Access Token Secret'))
        self.layout.Add(self.editAccessTokenSecret, flag=wx.EXPAND)
        self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'フッタ'))
        self.layout.Add(self.editFooter, flag=wx.EXPAND)
        self.layout.Add(self.buttonTest)

        self.panel.SetSizer(self.layout)

        self.radioIkaLogKey.Bind(
            wx.EVT_RADIOBUTTON, self.on_consumer_key_mode_switch)
        self.radioOwnKey.Bind(wx.EVT_RADIOBUTTON,
                              self.on_consumer_key_mode_switch)
        self.buttonIkaLogAuth.Bind(
            wx.EVT_BUTTON, self.on_ika_log_auth_button_click)
        self.buttonTest.Bind(wx.EVT_BUTTON, self.on_test_button_click)

    ##
    # Post a tweet
    # @param self    The object pointer.
    # @param s       Text to tweet
    # @param media   Media ID
    #
    def tweet(self, s, media=None):
        if media is None:
            params = {"status": s}
        else:
            params = {"status": s, "media_ids": [media]}

        from requests_oauthlib import OAuth1Session

        CK = self._preset_ck if self.consumer_key_type == 'ikalog' else self.consumer_key
        CS = self._preset_cs if self.consumer_key_type == 'ikalog' else self.consumer_secret

        twitter = OAuth1Session(
            CK, CS, self.access_token, self.access_token_secret)
        twitter.post(self.url, params=params)

    ##
    # Post a screenshot to Twitter
    # @param  self    The object pointer.
    # @param  frame   The image to be posted.
    # @return media   The media ID
    #
    def post_media(self, frame):

        if IkaUtils.isWindows():
            temp_file = os.path.join(
                os.environ['TMP'], '_image_for_twitter.jpg')
        else:
            temp_file = '_image_for_twitter.jpg'

        IkaUtils.writeScreenshot(temp_file, cv2.resize(frame, (640, 360)))

        files = {"media": open(temp_file, "rb")}

        CK = self._preset_ck if self.consumer_key_type == 'ikalog' else self.consumer_key
        CS = self._preset_cs if self.consumer_key_type == 'ikalog' else self.consumer_secret

        from requests_oauthlib import OAuth1Session
        twitter = OAuth1Session(
            CK, CS, self.access_token, self.access_token_secret)
        req = twitter.post(self.url_media, files=files)

        if req.status_code == 200:
            return json.loads(req.text)['media_id']

        return None

    ##
    # get_text_game_individual_result
    # Generate a record for on_game_individual_result.
    # @param self      The Object Pointer.
    # @param context   IkaLog context
    #
    def get_text_game_individual_result(self, context):
        map = IkaUtils.map2text(context['game']['map'], unknown='スプラトゥーン')
        rule = IkaUtils.rule2text(context['game']['rule'], unknown='バトル')
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text='勝ち', lose_text='負け', unknown_text='参加し')
        t = datetime.now().strftime("%Y/%m/%d %H:%M")

        s = '%sで%sに%sました' % (map, rule, won)

        me = IkaUtils.getMyEntryFromContext(context)

        if ('score' in me) and self.tweet_my_score:
            s = '%s %sp' % (s, me['score'])

        if ('kills' in me) and ('deaths' in me) and self.tweet_kd:
            s = '%s %dk/%dd' % (s, me['kills'], me['deaths'])

        if ('udemae_pre' in me) and self.tweet_udemae:
            s = '%s ウデマエ %s' % (s, me['udemae_pre'])

        fes_title = IkaUtils.playerTitle(me)
        if fes_title:
            s = '%s %s' % (s, fes_title)

        s = '%s (%s) %s #IkaLogResult' % (s, t, self.footer)

        if self.use_reply:
            s = '@_ikalog_ %s' % s

        return s

    ##
    # on_game_individual_result Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def on_game_individual_result(self, context):
        self.img_result_detail = context['engine']['frame']

    def on_game_session_end(self, context):
        IkaUtils.dprint('%s (enabled = %s)' % (self, self.enabled))

        if not self.enabled:
            return False

        if self.img_result_detail is None:
            return False

        s = self.get_text_game_individual_result(context)
        IkaUtils.dprint('投稿内容 %s' % s)

        media = self.post_media(self.img_result_detail
                                ) if self.attach_image else None
        self.tweet(s, media=media)

        self.img_result_detail = None

    ##
    # check_import
    # Check availability of modules this plugin depends on.
    # @param self      The Object Pointer.
    #
    def check_import(self):
        try:
            from requests_oauthlib import OAuth1Session
        except:
            print("モジュール requests_oauthlib がロードできませんでした。 Twitter 投稿ができません。")
            print("インストールするには以下のコマンドを利用してください。\n    pip install requests_oauthlib\n")

    ##
    # Constructor
    # @param self              The Object Pointer.
    # @param consumer_key      Consumer key of the application.
    # @param consumer_secret   Comsumer secret.
    # @param auth_token        Authentication token of the user account.
    # @param auth_token_secret Authentication token secret.
    # @param attach_image      If true, post screenshots.
    # @param footer            Footer text.
    # @param tweet_my_score    If true, post score.
    # @param tweet_kd          If true, post killed/death.
    # @param tweet_udemae      If true, post udemae(rank).
    # @param use_reply         If true, post the tweet as a reply to @_ikalog_
    #
    def __init__(self, consumer_key=None, consumer_secret=None, access_token=None, access_token_secret=None, attach_image=False, footer='', tweet_my_score=False, tweet_kd=False, tweet_udemae=False, use_reply=True):
        self.enabled = not((consumer_key is None) or (consumer_secret is None) or (
            access_token is None) or (access_token_secret is None))
        self.consumer_key_type = 'own'
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.attach_image = attach_image
        self.tweet_my_score = tweet_my_score
        self.tweet_kd = tweet_kd
        self.tweet_udemae = tweet_udemae
        self.use_reply = use_reply
        self.footer = footer

        self.img_result_detail = None

        self.check_import()

if __name__ == "__main__":
    import sys
    obj = Twitter(
        consumer_key=sys.argv[1],
        consumer_secret=sys.argv[2],
        access_token=sys.argv[3],
        access_token_secret=sys.argv[4]
    )
    print(obj.get_text_game_individual_result({
        "game": {
            "map": {"name": "map_name"},
            "rule": {"name": "rule_name"},
            "won": True, }}))
    obj.tweet('＜8ヨ 〜〜')
