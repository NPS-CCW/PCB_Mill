#
# drill_reduce.py
# Zac Staples
# zhstaple(at)nps(dot)edu
# directer NPS-DAZL group
# github: https://github.com/NPS-DAZL
#
# Usage:
#   drill files produces by eagle produce measurements at .1 mils.
#   PCBmill free software used to convert eagle cam processor into
#   G-code require inputs in incremets of 1 mil.
#
#   drill_reduce.py divides all x and y axis coordinates by 10 in
#   order to properly import them into PCBmill
#
#   drill files from the eagle cam processor should be in Excellon
#   format.  See www.excellon.com/manuals for file format details

import sys

# conduct argument checking
if(len(sys.argv) != 2):
    print("Usage: drill_reduce.py <filename>")
    print("\t<filename> must point to the drill file output from the eagle")
    print("\tcam processor.")
    sys.exit()

# ensure the argument connects to a file that be opened
try:
    fp = open(sys.argv[1], 'r')
except IOError:
    print("Error: unable to open file " + str(sys.argv[1]))
    sys.exit()

# excellon drill formats begin like this:
#   %
#   M48
# ensure the passed file matches this format
def format_error():
    print("Error: " + str(sys.argv[1])+ " is not in Excellon format")
    sys.exit()

lines = fp.readlines()
if(str(lines[0]).strip() != '%'):
    format_error()
if(str(lines[1]).strip() != 'M48'):
    format_error()  

print ("Arguments are good")

#-------Process an X line---------#
def process_x_line(line):   #return dict {'x', 'y'}  
    str_list = line.split('Y')
    x_val = int(str_list[0].strip('X'))
    y_val = int(str_list[1])
    x_val = x_val/10
    y_val = y_val/10
    vals = {'x': x_val, 'y': y_val}
    return vals

#------------Write to output-----------#
# fp is a file handle to the output file
# line is a string line of code from the input file
# D is a dict of 'x' and 'y' values
def write_to_output(fp, line, D):   
    if(D == None):
        fp.write(line)
    else:
        output = "X"+str(D['x'])+"Y"+str(D['y'])+'\n'
        fp.write(output)

##############################################
#                 MAIN
##############################################
outfile_name = sys.argv[1] + "_mod"
outfile = open(outfile_name, 'w')
for line in lines:
    if line[0] == 'X':
        D = process_x_line(line)
    else:
        D = None

    write_to_output(outfile, line, D)

print("Drill output stored in: " + outfile_name)        
