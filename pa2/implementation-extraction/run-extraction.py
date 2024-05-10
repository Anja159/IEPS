import sys
from A import extractRegex
from B import extractXpath
from C import run_roadrunner

overstock1 = '../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html'
overstock2 = '../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljs╠îe v razredu - RTVSLO.si.html'
rtvslo1 = '../input-extraction/overstock.com/jewelry01.html'
rtvslo2 = '../input-extraction/overstock.com/jewelry02.html'

kitara1 = '../input-extraction/thomann.de/harley_benton_eguitar_kit.html'
kitara2 = '../input-extraction/thomann.de/squier_affinity_strat_laurel_sg.html'

pages = [overstock1, overstock2, rtvslo1, rtvslo2, kitara1, kitara2]
# pages = [kitara1, kitara2]

# function = sys.argv[1]
function = 'C'

if function == 'A':
    extractRegex(pages)
elif function == 'B':
    extractXpath(pages)
elif function == 'C':
    run_roadrunner()
else:
    print("Wrong run!")
