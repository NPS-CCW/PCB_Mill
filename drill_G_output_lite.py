#! /usr/bin/env python

#Matthew A. Porter
#drill_G_output_lite.py
#
#This file outputs three separated Excellon files for use with the PCBmill program when
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

##group_lines(): groups lines into three drill bit size categories, depending upon the
##original drill bit size specified in the Excellon file. The ordering process applies
##a ceiling function to each bit size: if a drill bit is between #65 and #58, it will be grouped in
##the #58 group, which is the larger of the two bits.
def group_lines(drill_list,drill_lines):
    grouped_lines = []
    D65_lines = []
    D58_lines = []
    D52_lines = []
    D44_lines = []
    ##If the drill bit size is not 0.086, 0.0625, 0.042 or 0.035, round to the nearest
    i = 0
    for bit_vals in drill_list:
        if( drill_list[i] < 0.035 ):
            for line in drill_lines[i]:
                D65_lines.append(line)
        elif( drill_list[i] >= 0.035 and drill_list[i] < 0.042 ):
            for line in drill_lines[i]:
                D58_lines.append(line)
        elif( drill_list[i] >= 0.042 and drill_list[i] <= 0.0625 ):
            for line in drill_lines[i]:
                D52_lines.append(line)
        elif( drill_list[i] > 0.0625 ):
            for line in drill_lines[i]:
                D44_lines.append(line)
        i += 1
    grouped_lines.append(D65_lines)
    grouped_lines.append(D58_lines)
    grouped_lines.append(D52_lines)
    grouped_lines.append(D44_lines)
    print("Drill file successfully grouped into #44, #58 and #65 bit groupings!")
    return grouped_lines

##Output a '%', the only header/footer character necessary for PCBmill drill files
def get_x(line):
    line = line.strip()
    X_ind = line.find('X')
    Y_ind = line.find('Y')
    hold = str(line[X_ind+1:Y_ind])
    x_val = int(hold)/10
    print("Found X: " + str(x_val))
    return x_val

def get_y(line):
    line = line.strip()
    X_ind = line.find('X')
    Y_ind = line.find('Y')
    hold = str(line[Y_ind+1:len(line)])
    y_val = int(hold)/10
    print("Found Y: " + str(y_val))
    return y_val

def make_header_footer():
    output = '%'
    return output

def make_xy_pos(x_val,y_val):
    output = "X" + str(x_val) + "Y" + str(y_val)
    return output

##Compile an output drill file from a list of drill positions
def make_drill_output(grouped_lines):
    drill_file = []
    drill_file.append(make_header_footer())
    for line in grouped_lines:
        x_val=get_x(line)
        y_val=get_y(line)
        drill_file.append(make_xy_pos(x_val,y_val))
    drill_file.append(make_header_footer())
    return drill_file

##MAIN Body##

d_sizes = get_drill_sizes() #Parse the drill list
output = strip_e_file() #Cut the fat from the Excellon file
output2 = split_e_file_by_bit(output) #Divide the drill positioning elements of the Excellon file by bit
grouped = group_lines(d_sizes,output2) #Group the divided drill list into three lists

outfiles = ["65_drill.txt_int","58_drill.txt_int","52_drill.txt_int","44_drill.txt_int"]

i=0
for item in grouped:
    G_outfile = make_drill_output(item) #Attach a percent sign header/footer to each bit list
    out_fp = open(outfiles[i],'w') 
    for line in G_outfile: #Write each bit list to a separate file
       print line
       out_fp.write(line+'\n')
    out_fp.close()
    i += 1

print("Drill Excellon file sucessfully split into 65_drill.txt_int, 58_drill.txt_int and 44_drill.txt_int!")
