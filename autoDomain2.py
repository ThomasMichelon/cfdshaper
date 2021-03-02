#!/usr/bin/env python3.8

from stl import mesh
import os
import math

# TODO: implement ground/off ground
#       maybe make it handle files with weird aspect ratios like
#       using max(l_x,l_y,l_z) instead of l_x

def get_bounds():
    minx_temp=[]; maxx_temp=[]; miny_temp=[]; maxy_temp=[]; minz_temp=[]; maxz_temp=[]
    for part in stl_file:
        minx_temp.append(part.x.min())
        maxx_temp.append(part.x.max())
        miny_temp.append(part.y.min())
        maxy_temp.append(part.y.max())
        minz_temp.append(part.z.min())
        maxz_temp.append(part.z.max())
    bounds = {}
    bounds['minx'] = min(minx_temp)
    bounds['maxx'] = max(maxx_temp)
    bounds['miny'] = min(miny_temp)
    bounds['maxy'] = max(maxy_temp)
    bounds['minz'] = min(minz_temp)
    bounds['maxz'] = max(maxz_temp)
    bounds['l_x'] = bounds['maxx'] - bounds['minx']
    bounds['l_y'] = bounds['maxy'] - bounds['miny']
    bounds['l_z'] = bounds['maxz'] - bounds['minz']
    return bounds

stl_file_name='constant/triSurface/model.stl'
stl_file = mesh.Mesh.from_multi_file(stl_file_name)
bounds = get_bounds()

#float(os.environ.get('BOARD_SPEED'))
U = 10
turbulence_intensity = 0.05
chord_length = bounds['l_x']
rocker = bounds['l_z']
width = bounds['l_y']

#Bounds of the board box
minx =bounds['minx'] 
miny = bounds['miny']
minz = bounds['minz']
maxx = bounds['maxx']
maxy = bounds['maxy']
maxz = bounds['maxz']

rho = 999.8
mu = 1.31e-6

if os.environ.get('SIMULATION_TYPE')=='dummy':
    base_cell_size = chord_length * 0.8
else:
    base_cell_size = chord_length * 0.8

k = 1.5 * (turbulence_intensity * U)**2
omega = (k**0.5) / (( 0.09**0.25)*chord_length)

# blockMeshDict

length_dom = 42
width_dom = 24
height_dom = 20
l_caract = min( length_dom / chord_length, height_dom / rocker, width_dom / width)

scale = round((1/l_caract)*70)

print('chord_length :', chord_length)
print('rocker :', rocker )
print('width :', width)


print('Rx', length_dom / chord_length )
print('Ry', height_dom / rocker )
print('Rz', width_dom / width )

print('scale:', scale )

adjustementx = 0.5
adjustementwake = 3
adjustementy = 2
adjustementz = 2


# snappyHexMeshDict

refinement_minx = round(bounds['minx'] - bounds['l_x'] * adjustementwake, 1)
refinement_miny = round(bounds['miny'] - bounds['l_y'] * adjustementy, 1) 
refinement_minz = round(bounds['minz'] - bounds['l_z'] * adjustementz, 1)

refinement_maxx = round(bounds['maxx'] + bounds['l_x'] * adjustementx)
refinement_maxy = -refinement_miny
refinement_maxz = -refinement_minz

#topoSetDict

bx = []; by = [];bz = [];bxx = [];byy = [];bzz = []

bx.append(round(-chord_length * 5, 1))
by.append(round(-width * 5, 1 ))
bz.append(round(-rocker * 5, 1))

bxx.append(round(chord_length * 5, 1))
byy.append(round(width * 5, 1 ))
bzz.append(round(rocker * 5, 1))

for i in range(1,5):

    bx.append(round(bx[0]- i * 0.25 * scale))
    by.append(round(by[0]- i * 0.25 * scale))
    bz.append(round(bz[0]- i * 0.25 * scale))

    bxx.append(round(bxx[0]+ i * 0.25 * scale))
    byy.append(round(byy[0]+ i * 0.25 * scale))
    bzz.append(round(bzz[0]+ i * 0.25 * scale))



x_in_mesh = int(- 5 * bounds['l_x'])
y_in_mesh = int(- 5 * bounds['l_y'])
z_in_mesh = int(- 5 * bounds['l_z'])

# controlDict
if os.environ.get('SIMULATION_TYPE')=='dummy':
    endTime = 5
else:
    endTime = 10

writeInterval = round(endTime/10)

# decomposeParDict
if os.environ.get('SIMULATION_TYPE')=='dummy':
    numCores = 16
else:
    numCores = 32

# Write all values to file

with open('system/blockMeshDict', 'r') as file :
    filedata = file.read()
filedata = filedata.replace('{{scale}}', str(scale))

with open('system/blockMeshDict', 'w') as file:
    file.write(filedata)

with open('system/snappyHexMeshDict', 'r') as file :
    filedata = file.read()
filedata = filedata.replace('{{refinement_minx}}', str(refinement_minx))
filedata = filedata.replace('{{refinement_maxx}}', str(refinement_maxx))
filedata = filedata.replace('{{refinement_miny}}', str(refinement_miny))
filedata = filedata.replace('{{refinement_maxy}}', str(refinement_maxy))
filedata = filedata.replace('{{refinement_minz}}', str(refinement_minz))
filedata = filedata.replace('{{refinement_maxz}}', str(refinement_maxz))


filedata = filedata.replace('{{x_in_mesh}}', str(x_in_mesh))
filedata = filedata.replace('{{y_in_mesh}}', str(y_in_mesh))
filedata = filedata.replace('{{z_in_mesh}}', str(z_in_mesh))

with open('system/snappyHexMeshDict', 'w') as file:
    file.write(filedata)

with open('system/controlDict', 'r') as file :
    filedata = file.read()
filedata = filedata.replace('{{endTime}}', str(int(endTime)))
filedata = filedata.replace('{{writeInterval}}', str(int(writeInterval)))

with open('system/controlDict', 'w') as file:
    file.write(filedata)


for i in range (0,5):
   
    with open(str('system/topoSetDict.' + str(i+1)), 'r') as file :
        filedata = file.read()
    filedata = filedata.replace(str('{{bx['+ str(i+1) + ']}}') , str(float(bx[i])))
    filedata = filedata.replace(str('{{by['+ str(i+1) + ']}}') , str(float(by[i])))
    filedata = filedata.replace(str('{{bz['+ str(i+1) + ']}}') , str(float(bz[i])))
    filedata = filedata.replace(str('{{bxx['+ str(i+1) + ']}}') , str(float(bxx[i])))
    filedata = filedata.replace(str('{{byy['+ str(i+1) + ']}}') , str(float(byy[i])))
    filedata = filedata.replace(str('{{bzz['+ str(i+1) + ']}}') , str(float(bzz[i])))

    with open(str('system/topoSetDict.' + str(i+1)), 'w') as file:
        file.write(filedata)

with open('system/decomposeParDict', 'r') as file :
    filedata = file.read()
filedata = filedata.replace('{{numCores}}', str(int(numCores)))
with open('system/decomposeParDict', 'w') as file:
    file.write(filedata)


print('bx', bx)
print('by:', by)
print('bz:', bz)

print('bxx', bx)
print('byy:', byy)
print('bzz:', bzz)

print('U:                     %2.1f' % U)
print('chord_length:          %2.3f' % chord_length)

