import numpy as np

def CreateTriangle3D(point,view_matrix,stack):

    point_matrix = np.array([point[i:i + 3] + [1] for i in range(0, len(point), 3)]).transpose()

    render_matrix = np.identity(4)
    render_matrix = np.matmul(render_matrix,view_matrix)
    render_matrix = np.matmul(render_matrix,stack[-1])
    render_matrix = np.matmul(render_matrix,point_matrix)

    for i in range(render_matrix.shape[1]):
        render_matrix[0][i] /= render_matrix[3][i]
        render_matrix[1][i] /= render_matrix[3][i]
        render_matrix[2][i] /= render_matrix[3][i]
        render_matrix[3][i] /= render_matrix[3][i]

    return np.concatenate([ [int(render_matrix[0][i]), int(render_matrix[1][i])] 
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

# CORES POR VÉRTICE
#area = abs(x1(y2-y3)+x2(y3-y1)+x3(y1-y2))/2
#alph = abs(x(y2-y3)+x2(y3-y)+x3(y-y2))/2/area
#beta = abs(x(y3-y1)+x3(y1-y)+x1(y-y3))/2/area
#gama = abs(x(y1-y2)+x1(y2-y)+x2(y-y1))/2/area