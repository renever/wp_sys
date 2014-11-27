#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os.path


def converts(string=""):
    result = []
    word_dict = {}
    data_file='word.data'

    if not os.path.exists(data_file):
        raise IOError("File Not Found")

    with file(data_file) as f_obj:
        for f_line in f_obj.readlines():
            try:
                line = f_line.split('    ')
                word_dict[line[0]] = line[1]
            except:
                line = f_line.split('   ')
                word_dict[line[0]] = line[1]

    if not isinstance(string, unicode):
        string = string.decode("utf-8")
    for char in string:
        if u'\u4e00' <= char <= u'\u9fff':
            key = '%X' % ord(char)
            result.append(word_dict.get(key, char).split()[0][:-1].lower())
        else:
            result.append(char)
        data = ''.join(result)
    return data






