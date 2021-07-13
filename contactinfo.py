# -*- coding: utf-8 -*-
import json
import os
import tablib


def _json2xml():
    with open(os.path.join('./Results/results.json'), 'r', encoding='utf-8') as f:
        rows = json.load(f)
        xsldata = rows
        lenlist = len(xsldata)
        if lenlist != 0:
            header = tuple([i for i in xsldata[1].keys()])
            data = []
            for row in xsldata:
                body = []
                for v in row.values():
                    body.append(v)
                data.append(tuple(body))
                print('data', data)
            data = tablib.Dataset(*data, headers=header)
            print('data', data)
            open(os.path.join('./Results/results.xls'), 'wb').write(data)
            print('data.xls',data.xls)
            print('Results.xls文件写入完成')

if __name__ == '__main__':
    _json2xml()