#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 11:14:44 2018

@author: zero
"""

import hashlib

def get_md5(url):
    '''
    将urlmd5化,计算一个字符串的MD5值
    '''
    if isinstance(url,str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


if __name__ == "__main__":
    print(get_md5("http://jobbole.com"))