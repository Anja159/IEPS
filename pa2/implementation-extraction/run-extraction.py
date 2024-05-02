import sys
from A import extractRegex
from B import extractXpath

overstock1 = '../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html'
overstock2 = '../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljs╠îe v razredu - RTVSLO.si.html'
rtvslo1 = '../input-extraction/overstock.com/jewelry01.html'
rtvslo2 = '../input-extraction/overstock.com/jewelry02.html'

pages = [overstock1, overstock2, rtvslo1, rtvslo2]

function = sys.argv[1]
#function = 'A'

if function == 'A':
    extractRegex(pages)
elif function == 'B':
    extractXpath(pages)
elif function == 'C':
    extractRegex(pages)
else:
    print("Wrong run!")