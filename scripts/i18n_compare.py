# -*- coding: utf-8 -*-

import unicodecsv
import gettext
import json
import os

from path import path

LANG = 'fr'
# this work in my dev environement (it may differs in yours)
BASE_DIR = path(os.path.abspath(__file__)).dirname().parent.parent
EDX_LOCALE = BASE_DIR / 'edx-platform/conf/locale'
FUN_LOCALE = BASE_DIR / 'fun-apps/locale'


edx_translations = gettext.translation('django', EDX_LOCALE, [LANG])
fun_translations = gettext.translation('django', FUN_LOCALE, [LANG])


def write_csv(filename, rows):
    with open(filename, 'wb') as f:
        writer = unicodecsv.writer(f, encoding='utf-8', delimiter=';', quotechar='"', quoting=unicodecsv.QUOTE_NONNUMERIC)
        for row in rows:
            writer.writerow(row)


def untranslated_edx_strings():
    # get edx's strings not translated in french:
    # (this do not work as empty strings are not compiled, we'll have to find an other way)
    keys = []
    for key, trans in edx_translations._catalog.items():
        print "%s  --   %s" % (key, trans)
        if trans == "":
            print key
            keys.append(key)
    return keys


def obsolete_fun_strings():
    # get obsoletes fun strings (keys do not exists anymore in edx)
    obsolete = {}
    for key, trans in fun_translations._catalog.items():
        if key not in edx_translations._catalog.keys():
            obsolete[key] = trans
    return obsolete


def unnecessary_fun_strings():
    # get unnecessary fun strings (translation is the same in both edx and fun)
    unnecessary = {}
    for key, trans in edx_translations._catalog.items():
        if key in fun_translations._catalog.keys():
            if fun_translations._catalog[key] == trans:
                unnecessary[key] = trans
    return unnecessary


def fun_edx_diff():
    # get diff (fun strings which differ from edx's)
    diff = {}
    for key, trans in edx_translations._catalog.items():
        if key in fun_translations._catalog.keys():
            if fun_translations._catalog[key] != trans:
                diff[key] = (trans, fun_translations._catalog[key])
    return diff




if __name__ == '__main__':

    write_csv('untranslated_edx_strings.csv', untranslated_edx_strings())
    #write_csv('obsolete_fun_strings.csv', obsolete_fun_strings().items())
    #write_csv('unnecessary_fun_strings.csv', unnecessary_fun_strings().items())
    #data = [(key, value[0], value[1]) for key, value in fun_edx_diff().items()]
    #write_csv('fun_edx_diff.csv', data)
