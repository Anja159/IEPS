import sys
from A import extractRegex
from A2 import extractRegex
from B import extractXpath
from C import autoExtract

overstock1 = '../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html'
overstock2 = '../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljs╠îe v razredu - RTVSLO.si.html'
rtvslo1 = '../input-extraction/overstock.com/jewelry01.html'
rtvslo2 = '../input-extraction/overstock.com/jewelry02.html'

kitara1 = '../input-extraction/thomann.de/Squier Affinity Strat Laurel SG – Thomann International.html'
kitara2 = '../input-extraction/thomann.de/Harley Benton Electric Guitar Kit ST-Style – Thomann International.html'

# pages = [overstock1, overstock2, rtvslo1, rtvslo2]
pages = [kitara1, kitara2]

# function = sys.argv[1]
function = 'C'

if function == 'A2':
    extractRegex(pages)
elif function == 'B':
    extractXpath(pages)
elif function == 'C':
    autoExtract(pages)
else:
    print("Wrong run!")
