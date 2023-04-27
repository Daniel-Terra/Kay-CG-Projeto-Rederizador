import numpy as np
import random as rd

def CreateTriangle3D(point,view_matrix,stack):

    point_matrix = np.array([point[i:i + 3] + [1] for i in range(0, len(point), 3)]).transpose()

    render_matrix = np.identity(4)
    render_matrix = np.matmul(render_matrix,view_matrix)
    render_matrix = np.matmul(render_matrix,stack[-1])
    render_matrix = np.matmul(render_matrix,point_matrix)

    for i in range(render_matrix.shape[1]):
        render_matrix[0][i] /= render_matrix[3][i]
        render_matrix[1][i] /= render_matrix[3][i]

    return np.concatenate([[render_matrix[0][i], render_matrix[1][i], render_matrix[2][i]]
                           for i in range(render_matrix.shape[1])],axis=0).tolist()

def Strip(coord):

    strip = []
    for i in range(len(coord)//3):
        i *= 3

        strip.append([coord[i],coord[i+1],coord[i+2]])

    return strip

def Rotate3D(rotation):

    qr = np.cos(rotation[3]/2)
    qi = np.sin(rotation[3]/2)*rotation[0]
    qj = np.sin(rotation[3]/2)*rotation[1]
    qk = np.sin(rotation[3]/2)*rotation[2]

    Mrot3D = np.identity(4)
    Mrot3D[0] = [1-2*(qj**2+qk**2), 2*(qi*qj-qk*qr), 2*(qi*qk+qj*qr),0]
    Mrot3D[1] = [2*(qi*qj+qk*qr), 1-2*(qi**2+qk**2), 2*(qj*qk-qi*qr),0]
    Mrot3D[2] = [2*(qi*qk-qj*qr), 2*(qj*qk+qi*qr), 1-2*(qi**2+qj**2),0]

    return Mrot3D

def Tfovy(fovx, width, height):
    return np.tan(2*np.tan(fovx/2)*(height/(height**2+width**2)**.5))

def ListSlicer(list,slicing,condition=None):

    return [list[i:i + slicing] for i in range(0, len(list), slicing)] if condition else None

def PixelInterp(x,y,area):

    if area != 0:

        interp = [0,1,2]
        interp[0] = abs(x[0]*(y[2]-y[3]) + x[2]*(y[3]-y[0]) + x[3]*(y[0]-y[2])) /2/area
        interp[1] = abs(x[0]*(y[3]-y[1]) + x[3]*(y[1]-y[0]) + x[1]*(y[0]-y[3])) /2/area
        interp[2] = abs(x[0]*(y[1]-y[2]) + x[1]*(y[2]-y[0]) + x[2]*(y[0]-y[1])) /2/area

    return interp

def ColorFlat(flat_color):
    flat_color = (np.array(flat_color['emissiveColor'])*255).astype(int).tolist()
    flat_color = [255,255,255] if flat_color == [0,0,0] else flat_color
    return flat_color

def ColorInterp(z,interp,colors):
    
    rgb = [0,1,2]
    rgb[0] = colors[0][0]*interp[0] + colors[1][0]*interp[1] + colors[2][0]*interp[2]
    rgb[1] = colors[0][1]*interp[0] + colors[1][1]*interp[1] + colors[2][1]*interp[2]
    rgb[2] = colors[0][2]*interp[0] + colors[1][2]*interp[1] + colors[2][2]*interp[2]

    # COLOCAR FORA?
    z[0] = 1/(interp[0]/z[1] + interp[1]/z[2] + interp[2]/z[3])
    rgb[0] = z[0]*(colors[0][0]*interp[0]/z[1] + colors[1][0]*interp[1]/z[2] + colors[2][0]*interp[2]/z[3])
    rgb[1] = z[0]*(colors[0][1]*interp[0]/z[1] + colors[1][1]*interp[1]/z[2] + colors[2][1]*interp[2]/z[3])
    rgb[2] = z[0]*(colors[0][2]*interp[0]/z[1] + colors[1][2]*interp[1]/z[2] + colors[2][2]*interp[2]/z[3])

    rgb = (np.array(rgb)*255).astype(int)

    return rgb

def ColorRandom(rgb,JustDoIt):
    
    return [rd.randint(0, 255) for _ in range(3)] if JustDoIt else rgb
'''
def Texture(interp,texCoord,texIndex,image):

    texFace = []
    for i in texIndex:
        if i != -1:
            texFace.append(i)
            continue
        
        for f in range((len(texFace)-1)//2):
            f *= 2

            Texture3D = texCoord[texFace[0]]+texCoord[texFace[f+1]]+texCoord[texFace[f+2]]

            u = Texture3D[0][0]*interp[1] + Texture3D[0][]*interp[2] + Texture3D[2]*interp[1]

        texface = []

    return None'''