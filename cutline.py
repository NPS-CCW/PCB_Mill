#! /usr/bin/env python

#
# cutline.py
# Zac Staples & Carsten Sewing
# zhstaple(at)nps(dot)edu
# directer NPS-DAZL group
# github: https://github.com/NPS-DAZL
#
# Usage:
#   In order to cut the dimensional outline for our boards
#   we need to leave small tabs that the user chips off
#   after the board is finally cut.
#
#   Unfortunately, this path cannot be produces directly from
#   Eagle.  So cutline.py takes the plane file produced by
#   outputting the G-code from the outline layer and altering
#   it so that it has 2mm tabs at the edge of every board.

import sys

# conduct argument checking
if(len(sys.argv) != 2):
    print("Usage: cutline.py <filename>")
    print("\t<filename> must point to the G-code file of the board")
    print("\toutline produced in PCBmill.")
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

#---------Get X------------------------------#
def get_x(line):    #return float value of any x in the line
    x_val = None
    # line contains space delimited values as follows:
    #   G00 X100.3968 Y-0.3970 F100.0
    tokens = line.split(' ')
    for token in tokens:
        if (token.find('X') != -1):
            print("found an x")
            token = token.strip()
            token = token.strip('X')
            x_val = float(token)

    return x_val
    
#---------Get Y------------------------------#
def get_y(line):    #return float value of any y in the line
    y_val = None
    # line contains space delimited values as follows:
    #   G00 X100.3968 Y-0.3970 F100.0
    tokens = line.split(' ')
    for token in tokens:
        if (token.find('Y') != -1):
            print("found an y")
            token = token.strip()
            token = token.strip('Y')
            y_val = float(token)

    return y_val
    
#---------Find corners----------------------#
# return dict {x_max, x_min, y_max, y_min}
def find_corners(lines):
    x_max = None
    x_min = None
    y_max = None
    y_min = None
    
    for line in lines[11:-3]:
        x = get_x(line)
        y = get_y(line)
        if(x):
            #x max
            if (x_max):
                if(x > x_max):
                    x_max = x
            else:
                x_max = x
            #x min
            if(x_min):
                if(x < x_min):
                    x_min = x
            else:
                x_min = x
        if(y):
            #y max
            if (y_max):
                if(y > y_max):
                    y_max = y
            else:
                y_max = y
            #y min
            if(y_min):
                if(y < y_min):
                    y_min = y
            else:
                y_min = y
    D = {'x_max': x_max, 'x_min': x_min, 'y_max': y_max, 'y_min':y_min}
    print("corners: " + str(D))
    return D

#-------Lift cutter to travel height---#
def lift():
    res = []
    mv = "G00 Z" + str(z_travel_height)
    res.append(mv)

    return res

#---------Header--------------------------#
#return a List of lines
def header():
    res = []
    mv = '%'
    res.append(mv)
    mv = 'G90'
    res.append(mv)
    mv = coord_system
    res.append(mv)
    mv = "G00 Z50.0"
    res.append(mv)
    mv = "F600.0 S"+str(spindle_spd)+" M03"
    res.append(mv)
    mv = 'G00 X0.0 Y0.0'
    res.append(mv)
    res = res + lift()

    return res

#--------Footer--------------------------#
def footer():
    res = []
    mv = "G00 Z" +str(z_travel_height)
    res.append(mv)
    mv = 'G00 X0.0 Y0.0'
    res.append(mv)
    mv = 'M05'
    res.append(mv)
    mv = 'M02'
    res.append(mv)
    mv = '%'
    res.append(mv)

    return res

#---------Move to origin-----------------#
def move_to_origin(corners):
    #takes a dictionary of corners
    #return a list of lines
    res = []
    origin = "G00 X" + str(corners['x_min']) + " Y" + str(corners['y_min'])
    res.append(origin)

    return res                                                     

#---------Drop to copper depth----------#
def drop_to_cd():
    # return a list of lines
    res = []
    step1 = "G00 Z" + str(z_fast_stop)
    res.append(step1)
    step2 = "G01 Z" + str(copper_depth) + " F" + str(feed_rate)
    res.append(step2)

    return res

#---------Drop to fr4----------#
def drop_to_fr4():
    # return a list of lines
    res = []
    step1 = "G00 Z" + str(z_fast_stop)
    res.append(step1)
    step2 = "G01 Z" + str(fr4_depth) + " F" + str(feed_rate)
    res.append(step2)

    return res

#---------Drop to final----------#
def drop_to_final():
    # return a list of lines
    res = []
    step1 = "G00 Z" + str(z_fast_stop)
    res.append(step1)
    step2 = "G01 Z" + str(final_depth) + " F" + str(feed_rate)
    res.append(step2)

    return res

#--------Feed_rate----------------------#
def fr():
    return " F" +str(feed_rate)

#--------Make rectangle-----------------#
def make_rect(corners):
    #return a list of lines
    res = []
    mv = "G01 X" + str(corners['x_min']) + " Y" + str(corners['y_max']) +fr()
    res.append(mv)
    mv = "G01 X" + str(corners['x_max']) + " Y" + str(corners['y_max'])
    res.append(mv)
    mv = "G01 X" + str(corners['x_max']) + " Y" + str(corners['y_min'])
    res.append(mv)
    mv = "G01 X" + str(corners['x_min']) + " Y" + str(corners['y_min'])
    res.append(mv)
    
    return res

#-------Tab btwn 2 corners---------------#
def tab_line(c1, c2, depth):
    # return a list lines
    # c1 and and c2 are each a n [x,y] coord for the two points
    # c1 must be less than c2
    # I make a 10mm tab beginning 10mm away from each corner
    res = []
    
    if(c1[0] == c2[0]):
        # milling a vertical line
        # x stays constant, and we generate six points
        y_list = []
        y_list.append(c1[1])
        y_list.append(c1[1]+10)
        y_list.append(c1[1]+20)
        y_list.append(c2[1]-20)
        y_list.append(c2[1]-10)
        y_list.append(c2[1])

        down_cut = False
        for coord in y_list:
            res.append(str("G01 X"+str(c1[0])+" Y"+str(coord))+fr())
            if down_cut:
                res = res + lift()
            else:
                res.append("G01 Z"+str(depth)+fr())

            down_cut = not down_cut
               
    if(c1[1] == c2[1]):
        #milling a horizontal line
        # y stays constant, and we generate six points
        x_list = []
        x_list.append(c1[0])
        x_list.append(c1[0]+10)
        x_list.append(c1[0]+20)
        x_list.append(c2[0]-20)
        x_list.append(c2[0]-10)
        x_list.append(c2[0])

        down_cut = False
        for coord in x_list:
            res.append("G01 X"+str(coord)+" Y"+str(c1[1])+fr())
            if down_cut:
                res = res + lift()
            else:
                res.append("G01 Z"+str(depth)+fr())

            down_cut = not down_cut
            
    #add the feed rate to line[0]
    res[0] = res[0] + fr()
    
    return res

#-----------Translate in X--------------------#
def translate_x_abs(x_coord):
    #use the last line of global output to find the x pos and tranlate to the given
    global output
    res = []

    last_line = output[-1]

    token_list = last_line.split(' ')
    tokens = []
    
    for token in token_list:
        #find the x token and change it
        if(token.find('X') != -1):
            token = "X"+str(x_coord)
        #append all tokens to 
        tokens.append(token)

    mod_line = ' '.join(tokens)
 
    res.append(mod_line)
    return res

#-----------Translate in Y--------------------#
def translate_y_abs(y_coord):
    #use the last line of global output to find the x pos and tranlate to the given
    global output
    res = []

    last_line = output[-1]

    token_list = last_line.split(' ')
    tokens = []
    
    for token in token_list:
        #find the y token and change it
        if(token.find('Y') != -1):
            token = "Y"+str(y_coord)
        #append all tokens to 
        tokens.append(token)

    mod_line = ' '.join(tokens)
 
    res.append(mod_line)
    return res

##############################################
#                 MAIN
##############################################
coord_system = "G55"

z_travel_height = 8.0
z_fast_stop = 3.0
copper_depth = -.6
fr4_depth = -1.65
final_depth = -2.4

feed_rate = 250.0

spindle_spd = 15000

output = []   #List of string lines of G-code

corners = find_corners(lines)

output = output + header()

output = output + move_to_origin(corners)

output = output + drop_to_cd()

output = output + make_rect(corners)

output = output + lift()

#---------FR4 Cut----------------------------#
output = output + move_to_origin(corners)

output = output + drop_to_fr4()

output = output + tab_line([corners['x_min'], corners['y_min']], [corners['x_min'], corners['y_max']], fr4_depth)

output = output + lift()

output = output + move_to_origin(corners)

output = output + drop_to_fr4()

output = output + tab_line([corners['x_min'], corners['y_min']], [corners['x_max'], corners['y_min']], fr4_depth)

output = output + lift()

output = output + move_to_origin(corners)

output = output + translate_x_abs(corners['x_max'])

output = output + drop_to_fr4()

output = output + tab_line([corners['x_max'], corners['y_min']], [corners['x_max'], corners['y_max']], fr4_depth)

output = output + lift()

output = output + move_to_origin(corners)

output = output + translate_y_abs(corners['y_max'])

output = output + drop_to_fr4()

output = output + tab_line([corners['x_min'], corners['y_max']], [corners['x_max'], corners['y_max']], fr4_depth)

output = output + lift()

#---------------Through Cut------------------#
output = output + move_to_origin(corners)

output = output + drop_to_final()

output = output + tab_line([corners['x_min'], corners['y_min']], [corners['x_min'], corners['y_max']], final_depth)

output = output + lift()

output = output + move_to_origin(corners)

output = output + drop_to_final()

output = output + tab_line([corners['x_min'], corners['y_min']], [corners['x_max'], corners['y_min']], final_depth)

output = output + lift()

output = output + move_to_origin(corners)

output = output + translate_x_abs(corners['x_max'])

output = output + drop_to_final()

output = output + tab_line([corners['x_max'], corners['y_min']], [corners['x_max'], corners['y_max']], final_depth)

output = output + lift()

output = output + move_to_origin(corners)

output = output + translate_y_abs(corners['y_max'])

output = output + drop_to_final()

output = output + tab_line([corners['x_min'], corners['y_max']], [corners['x_max'], corners['y_max']], final_depth)

output = output + footer()

outfile_name = 'GZ_test.txt'
out_fp = open(outfile_name, 'w')

for line in output:
    print line.rstrip()
    out_fp.write(line+'\n')

    
