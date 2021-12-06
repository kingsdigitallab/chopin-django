# -*- coding: utf-8 -*-

from collections import OrderedDict


# The documents are referenced by page content, via the database IDs,
# so these must be ordered.
document_data = {
    1: {
        'file': 'Table 1.pdf',
        'title': "Table 1 'First editions' with revised music text"
    },
    2: {
        'file': 'Table 2.pdf',
        'title': 'Table 2 Later editions'
    },
    3: {
        'file': 'Table 3.pdf',
        'title': 'Table 3 Chopin’s French publishers'
    },
    4: {
        'file': 'Table 4.pdf',
        'title': 'Table 4 Changes in ownership and acquisitions: Chopin’s French publishers'
    },
    5: {
        'file': 'Table 5.entire.pdf',
        'title': 'Table 5 Works published in France with opus number'
    },
    6: {
        'file': 'Table 6.pdf',
        'title': 'Table 6 Works published in France without opus number'
    },
    7: {
        'file': 'Table 7.pdf',
        'title': 'Table 7 Works published posthumously in France'
    },
    8: {
        'file': 'Table 8.pdf',
        'title': 'Table 8 Chopin’s German/Austrian publishers'
    },
    9: {
        'file': 'Table 9.pdf',
        'title': 'Table 9 Changes in ownership and acquisitions: Chopin’s German/Austrian publishers'
    },
    10: {
        'file': 'Table 10.entire.pdf',
        'title': 'Table 10 Works published in the German states with opus number'
    },
    11: {
        'file': 'Table 11.pdf',
        'title': 'Table 11 Works published in the German states without opus number or posthumously'
    },
    12: {
        'file': 'Table 12.pdf',
        'title': 'Table 12 Chopin’s English publishers'
    },
    13: {
        'file': 'Table 13.pdf',
        'title': 'Table 13 Changes in ownership, acquisitions and reprints: Chopin’s English publishers'
    },
    14: {
        'file': 'Table 14.entire.pdf',
        'title': 'Table 14 Works published in England with opus number'
    },
    15: {
        'file': 'Table 15.pdf',
        'title': 'Table 15 Works published in England without opus number or posthumously'
    },
    16: {
        'file': 'Table 16.pdf',
        'title': 'Table 16 Possible TPs and publication dates of defective English Chopin editions as inferred from advertisements'
    },
    17: {
        'file': 'Table 17.pdf',
        'title': 'Table 17 Chopin’s Polish publishers'
    },
    18: {
        'file': 'Table 18.pdf',
        'title': 'Table 18 Changes in ownership: Chopin’s Polish publishers'
    },
    19: {
        'file': 'Table 19.pdf',
        'title': 'Table 19 Italian publisher'
    }
}

document_data = OrderedDict(sorted(list(document_data.items()), key=lambda t: t[0]))

abbreviation_data = {
    'AA': 'acquisition advertisement',
    'ADF': 'Additional Distinguishing Feature(s)',
    'advt(s)': 'advertisement(s)',
    'AFE': 'Austrian first edition',
    'AmZ': '<i>Allgemeine musikalische Zeitung</i>',
    'ATP': 'album title page',
    'b.': 'bar',
    'BnF': 'Bibliotheque nationale de France',
    'bs': 'bars',
    'c.': 'circa',
    'CFC': '<i>Correspondance de Frédéric Chopin</i> (see <a id="20" linktype="page">Bibliography</a>)',
    'Ch&T': 'Chomiński and Turło, <i>Katalog dzieł Fryderyka Chopina</i> (see <a id="20" linktype="page">Bibliography</a>)',
    'col.': 'column',
    'cols.': 'columns',
    'CP': 'cover page',
    'CT': 'caption title',
    'CTP': 'common title page',
    'DF': 'Distinguishing Feature(s)',
    'DMF': 'Distinguishing Musical Feature(s)',
    'edn': 'edition',
    'EFE': 'English first edition',
    'engr': 'engraved',
    'EO': "STP of u'ÉDITION ORIGINALE| OEUVRES COMPLÈTES POUR LE PIANO|DE|FRÉDÉRIC CHOPIN (...)' published by G. Brandus et S. Dufour→G. Brandus et Cie→Brandus et Cie→Ph. Maquet",
    'FFE': 'French first edition',
    'Fl.': 'Florin(s)',
    'FL': 'footline',
    'Florp.': 'floren polski (i.e. Polish florin(s))',
    'FPA': 'first publication announcement',
    'GFE': 'German first edition',
    'gGr.': 'gute Groschen',
    'GMP': '<i>Gazette musicale de Paris</i>',
    'Gr.': 'Groschen',
    'GW': '<i>Gazeta Warszawska</i>',
    'HL': 'headline',
    'HT': 'half-title',
    'IB': '<i>Intelligenz-Blatt</i> (in AmZ)',
    'IFE': 'Italian first edition',
    'ITP': 'individual title page',
    'KA': '<i>Kurze Anzeige</i> (in AmZ)',
    'KFC': '<i>Korespondencja Fryderyka Chopina</i> (see <a id="20" linktype="page">Bibliography</a>)',
    'Kop.': 'kopeck(s)',
    'Kr.': 'Kreutzer(s)',
    'KW': '<i>Kurjer Warszawski</i>',
    'LH': 'left hand',
    'lith': 'lithographed',
    'MIM': '<i>Musikalisch-literarischer Monatsbericht</i>',
    'Mk.': 'Mark(s)',
    'mm': 'millimetre(s)',
    'mvt(s)': 'movement(s)',
    'MW': '<i>Musical World</i>',
    'Ngr.': 'Neugroschen',
    'p.': 'page',
    'PA': 'publication advertisement',
    'PD': 'publication date',
    'Pf.': 'Pfennig(s)',
    'PFE': 'Polish first edition',
    'pp.': 'pages',
    'R': '<i>Rezensionen</i> (in AmZ)',
    'RD': 'registration date',
    'RGMP': '<i>Revue et Gazette musicale de Paris</i>',
    'RH': 'right hand',
    'RH/LH': 'right and left hands (used to describe a musical feature in both parts)',
    'Rs.': 'srebrny rubel (i.e. silver rouble(s))',
    'SC': 'sub-caption',
    'sep.': 'separate',
    'Sgr.': 'Silbergroschen',
    'STP': 'series title page',
    'Thlr.': 'Thaler(s)',
    'TP': 'title page',
    'vol.': 'volume',
    'vols.': 'volumes',
    'WP': 'wrapper page',
    'WZ': '<i>Wiener Zeitung</i>',
    'złp., Złtp.': 'złoty polski',
}

bad_library_codes = [
    'Buch-u',
    'EDITEURS-COMMISSIORES',
    'Fantaisie-Transcription',
    'Fantasy-Impromptu',
    'Half-title',
    'I-A',
    'Instrumenten-u',
    'MUSIKALIEN-LEIHANSTALT',
    'PIANOFORTE-WERKE',
    'PUITS-GAILLOT',
    'quasi-oval',
    'reddish-brown',
    'Saint-Honoré',
    'Sub-caption',
    'Zaleska-Rosengardt',
]
