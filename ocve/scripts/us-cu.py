 # -*- coding: utf-8 -*-
from ocve.models import *

import codecs

def run():
    src = SourceInformation.objects.filter(archive=1803)# 1803=US-Cu

    csv_string = 'source code\tshelf mark\tdisplayed copy information\tarchive\n'

    for s in src:
        csv_string += '%s\t%s\t%s\t%s\n' % (s.sourcecode, s.shelfmark, s.displayedcopy, s.archive)

    with codecs.open('ocve_us-cu.csv', 'w', encoding='utf-8') as csv_file:
        csv_file.write(csv_string)
        csv_file.close()
