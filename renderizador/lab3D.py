import numpy as np

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


