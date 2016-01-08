#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Abhi Gupta
# @Date:   2015-06-09 15:08:47
# @Last Modified by:   Abhi
# @Last Modified time: 2015-06-12 03:19:49
# Text to Speech

import os
import platform 

os_info = platform.system()

def text2speech(text):
    """Different voices used for text to speech"""
    if os_info == 'Darwin':
        os.system('say ' + text)
    elif os_info == 'Linux':
        os.system('espeak -v en ' + text)   # must install python espeak module for ubuntu 
    else:
        import win32com.client
        speech = win32com.client.Dispatch('Sapi.SpVoice')   # must install python for Windows module
        speech.Speak(text)

#Example Usuage of TTS
if __name__ == '__main__':
    text2speech('Hello World')