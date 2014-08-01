#
# G_final.py
# Zac Staples
# zhstaple(at)nps(dot)edu
# directer NPS-DAZL group
# github: https://github.com/NPS-DAZL
#
# Usage:
#   G -code files produced by PCBmill will not load onto the Roland
#   MDX-40A mill we use to cut PCB's because of formatting issues
#   in the files.
#
#   G_final.py processes the filenames provided as command line
#   arguments to so they will load into the Roland mill

import sys

# conduct argument checking
if(len(sys.argv) != 2):
    print("Usage: G_final.py <filename>")
    print("\t<filename> must point to the G-code file output from PCBmill.")
    sys.exit()

# ensure the argument connects to a file that be opened
try:
    fp = open(sys.argv[1], 'r')
except IOError:
    print("Error: unable to open file " + str(sys.argv[1]))
    sys.exit()

# PCBmill provided G-code files begin with
# excellon drill formats begin like this:
#   %~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   %        File was created with PCBMill V1.0          
#
# ensure the passed file matches this format
def format_error():
    print("Error: " + str(sys.argv[1])+ " is not a PCBMill V1.0 formatted file")
    sys.exit()

lines = fp.readlines()
if(str(lines[0]).strip() != '%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'):
    format_error()
if(str(lines[1]).rstrip() != '%        File was created with PCBMill V1.0'):
    format_error()  

print ("Arguments are good")

##############################################
#                 MAIN
##############################################
outfile_name = sys.argv[1] + "_final"
outfile = open(outfile_name, 'w')

for line in lines[5:]:
    if line.rstrip() == "G00 Z8":
        print"line match on G00"
        line = "G00 Z8.0\n"
    outfile.write(line)
