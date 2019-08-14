# -*- coding: utf-8 -*-
# @Time  : 6/19/19 3:36 PM
# @Author : jlinka
# @Project : ESG
# @Desc : 时间正则表达式, 同ner抽取的时间正则还是具备一定差距, 故有意愿可以当成辅助使用

import re
import time

# 主要时间正则表达式
time_regex = re.compile(r'(20\d{2}([\.\-/|年月\s]{1,3}\d{1,2}){2}日?(\s?\d{2}:\d{2}(:\d{2})?)?)|(\d{1,2}\s?(分钟|小时|天)前)')

while True:
    time_text = input("input time:\n")
    post_time = re.search(time_regex, time_text)
    if post_time:
        print("\tfind time: {}\t".format(post_time.group()))
    else:
        print("not find time input: {}".format(time_text))
    print()
