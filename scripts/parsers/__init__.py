from .bca import BCAParser
from .dbs import DBSParser
from .mandiri import MandiriParser
from .cimb import CIMBParser
from .bni import BNIParser
from .bsi import BSIParser
from .mega import MegaParser

PARSER_MAP = {
    "bca":          BCAParser(),
    "dbs_3099":     DBSParser(),
    "mandiri_3517": MandiriParser(),
    "cimb_0407":    CIMBParser("cimb_0407", "CIMB Niaga", "0407"),
    "cimb_5614":    CIMBParser("cimb_5614", "CIMB Niaga", "5614"),
    "cimb_6174":    CIMBParser("cimb_6174", "CIMB Syariah", "6174"),
    "bni_0493":     BNIParser("bni_0493", "0493", "MC Titanium"),
    "bni_2256":     BNIParser("bni_2256", "2256", "Lotte Mart"),
    "bsi_6634":     BSIParser(),
    "mega_6566":    MegaParser("mega_6566", "6566"),
}
