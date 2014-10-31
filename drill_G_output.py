#Matthew A. Porter
#drill_G_output.py
#
#This file outputs a G-code script for use with a CNC milling machine when
#fed an Excellon formatted drill file.  The current version assumes a
#1/10000" scale for the Excellon units and no offset in the excellon file.

import sys

##Error catch for file IO issues
if(len(sys.argv) != 2):
    print("Usage: drill_G_output.py <filename>")
    print("\t<filename> must point to the Excellon drill file")
    print("\tproduced in Eagle.")
    sys.exit()

try:
    fp = open(sys.argv[1], 'r')
except IOError:
    print("Unable to open drill file " + str(sys.argv[1]))
    sys.exit()

##Read in the file as a list of strings
lines=fp.readlines()

##Check that loaded file is of excellon type: starts with %\n != '%')
if(str(lines[0]).strip() != '%' or str(lines[1]).strip() != 'M48'):
    print("Error: " + str(sys.argv[1]) + " is not an Excellon drill file")
    sys.exit()
else:
    print("Arguments are good")

##Function definitions
##get_drill_sizes(): outputs a list of drill bits from the beginning of the
##Excellon file ordered by size
def get_drill_sizes():
    drill_list = []
    drill_size = 0    
    ## Drill definitions lines are separated from the drill block by a % sign.
    ## Definitions are of the form T##C0.####, where the last block of numbers
    ## is the drill bit size in 1/10000"
    for line in lines[1:len(lines)]:
        if(str(line).strip() == '%'):
            break
        else:
            holder = str(line).strip()
            if(holder[0] == 'T'):
                tokens = holder[1:len(holder)].split('.')
                drill_size = float(tokens[1])/10000
                print("Found a drill bit of size: " + str(drill_size))
                drill_list.append(drill_size)     

    return drill_list

##strip_e_file(): removes the bit definition block from the excellon files 
##lines
def strip_e_file():
    sep_in = 1
    for line in lines[1:len(lines)]:
        if(str(line) == '%\n'):
            break
        sep_in += 1
    print('Excellon file stripped!')
    return lines[sep_in+1:len(lines)-1]

##split_file_by_bit(): splits drill pattern part of Excellon file by bit
##size, returns list of string lists ordered by bit size    
def split_e_file_by_bit(stripped_file):
    drill_lines = []
    i = 1
    while(i <= len(stripped_file)-1 ):
        holder = []
        while(stripped_file[i][0] != 'T'):
            holder.append(stripped_file[i])
            i += 1
            if( i == len(stripped_file) ):
                break         
        drill_lines.append(holder)
        i += 1
    print("Drill file split!")
    return drill_lines

def group_lines(drill_list,drill_lines):
    grouped_lines = []
    D65_lines = []
    D58_lines = []
    D44_lines = []
    ##If the drill bit size is not 0.086, 0.042 or 0.035, round to the nearest
    i = 0
    for bit_vals in drill_list:
        if( drill_list[i] < 0.035 ):
            for line in drill_lines[i]:
                D65_lines.append(line)
        elif( drill_list[i] >= 0.035 and drill_list[i] < 0.0385 ):
            for line in drill_lines[i]:
                D65_lines.append(line)
        elif( drill_list[i] >= 0.0385 and drill_list[i] < 0.064 ):
            for line in drill_lines[i]:
                D58_lines.append(line)
        elif( drill_list[i] >= 0.064 ):
            for line in drill_lines[i]:
                D44_lines.append(line)
        i += 1
    grouped_lines.append(D65_lines)
    grouped_lines.append(D58_lines)
    grouped_lines.append(D44_lines)
    print("Drill file successfully grouped into #44, #58 and #65 bit groupings!")
    return grouped_lines

##
def convert_in_to_mm(in_val):
    mm_val = in_val/0.0393
    mm_val = round(mm_val,4)
    return mm_val

def get_x(line):
    line = line.strip()
    X_ind = line.find('X')
    Y_ind = line.find('Y')
    hold = str(line[X_ind+1:Y_ind])
    x_val = float(hold)/10000
    x_val = round(x_val,4)
    print("Found X: " + str(x_val))
    return x_val

def get_y(line):
    line = line.strip()
    X_ind = line.find('X')
    Y_ind = line.find('Y')
    hold = str(line[Y_ind+1:len(line)])
    y_val = float(hold)/10000
    y_val = round(y_val,4)
    print("Found Y: " + str(y_val))
    return y_val

def make_G_header(coord_sys,feed_rate, drill_speed):
    output = []
    holder = "%"
    output.append(holder)
    holder = "G90"
    output.append(holder)
    holder = coord_sys
    output.append(holder)
    holder = "F" + str(feed_rate) + "S" + str(drill_speed) + "M03"
    output.append(holder)
    return output

def make_G_footer():
    output = []
    holder = "G00 Z50.0"
    output.append(holder)
    holder = "M05"
    output.append(holder)
    holder = "%"
    output.append(holder)
    return output

def raise_bit(travel_height):
    output = "G00 Z" + str(travel_height)
    return output

def drop_bit(drill_depth,feed_rate):
    output = []
    holder = "G00 Z3.0"
    output.append(holder)
    holder = "G01 Z" + str(drill_depth) + " F" + str(feed_rate)
    output.append(holder)
    return output

def mv_to_xy(x_val,y_val):
    output = "G00 X" + str(x_val) + " Y" + str(y_val)
    return output

def make_drill_G_output(grouped_lines,coord_sys,feed_rate,drill_speed,travel_height,drill_depth):
    G_file = []
    holder = make_G_header(coord_sys,feed_rate,drill_speed)
    for line in holder:
        G_file.append(line)
    for line in grouped_lines:
        G_file.append(raise_bit(travel_height))
        x_val = convert_in_to_mm(get_x(line))
        y_val = convert_in_to_mm(get_y(line))
        G_file.append(mv_to_xy(x_val,y_val))
        holder = drop_bit(drill_depth,feed_rate)
        for linea in holder:
            G_file.append(linea)
    holder = make_G_footer()
    for line in holder:
        G_file.append(line)
    return G_file

##MAIN Body##

coord_sys = 'G55'
feed_rate = 100
drill_speed = 15000
travel_height = 8.0
drill_depth = -2.5

d_sizes = get_drill_sizes()
output = strip_e_file()
output2 = split_e_file_by_bit(output)
grouped = group_lines(d_sizes,output2)

outfiles = ["65_drill.txt","58_drill.txt","44_drill.txt"]

i=0
for item in grouped:
    G_outfile = make_drill_G_output(item,coord_sys,feed_rate,drill_speed,travel_height,drill_depth)
    out_fp = open(outfiles[i],'w')
    for line in G_outfile:
       print line
       out_fp.write(line+'\n')
    out_fp.close()
    i += 1

print("Drill G-code sucessfully written to 65_drill.txt, 58_drill.txt and 44_drill.txt!")
print(outfiles)
