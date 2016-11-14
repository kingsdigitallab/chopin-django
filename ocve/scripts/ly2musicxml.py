__author__ = 'elliotthall'
#Quick script to test python ly musicxml conversion

import ly.musicxml


lilypondfilename='../templates/verovio/Op28 No9-1.ly'
xmlfilename = '../templates/verovio/Op28_No9-1.xml'

if __name__ == "__main__":
    lilypondfile = open(lilypondfilename,'r')
    lilypond_text = lilypondfile.read()
    lilypondfile.close()
    e = ly.musicxml.writer()
    e.parse_text(lilypond_text)
    xml = e.musicxml()
    xml.write(xmlfilename)         # or: xml.tostring()