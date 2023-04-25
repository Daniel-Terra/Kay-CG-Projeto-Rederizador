#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# pylint: disable=invalid-name

"""
Biblioteca Gráfica / Graphics Library.

Desenvolvido por: KAY
Disciplina: Computação Gráfica
Data: 16 de Fevereiro 2023
"""

import time         # Para operações com tempo
import gpu          # Simula os recursos de uma GPU
import math         # Funções matemáticas
import numpy as np  # Biblioteca do Numpy
import lab3D

class GL:
    """Classe que representa a biblioteca gráfica (Graphics Library)."""

    width = 800   # largura da tela
    height = 600  # altura da tela
    near = 0.01   # plano de corte próximo
    far = 1000    # plano de corte distante

    #Transforming Matrixes
    view_matrix = np.identity(4)
    stack = [np.identity(4)]

    #Base Color
    base_color = {'diffuseColor': [0.8, 0.8, 0.8], 'emissiveColor': [1.0, 1.0, 1.0],
                  'specularColor': [0.0, 0.0, 0.0], 'shininess': 0.2, 'transparency': 0.0}

    @staticmethod # Used to setup the environment
    def setup(width, height, near=0.01, far=1000):

        GL.width = width*2
        GL.height = height*2
        GL.near = near
        GL.far = far

    @staticmethod # Used to create a 2D Pixel on screen
    def polypoint2D(point, colors):

        colors = (np.array(colors['emissiveColor'])*255).tolist()
        colors = [int(color) for color in colors]

        for i in range(len(point)//2):
            i *= 2

            x,y = int(point[i]),int(point[i+1])

            if (x < 0 or x >= GL.width) or (y < 0 or y >= GL.height):
                continue               
            
            gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, colors)

    @staticmethod # Used to create a 2D Line on screen
    def polyline2D(lineSegments, colors):

        line = list(map(int, lineSegments))
        for i in range(len(line)//2-1):
            i *= 2
            
            point  = [line[i],line[i+1]]
            target = [line[i+2],line[i+3]]

            # iterative x and y
            x = line[i]
            y = line[i+1]

            # declare the angular variation between the first point and the target
            dx = abs(target[0]-point[0])
            dy = abs(target[1]-point[1])

            # sign for each axis variation
            sign_dx = 1 if target[0] > point[0] else -1
            sign_dy = 1 if target[1] > point[1] else -1

            #lets beguin with the point adding
            
            #this line is horizontal
            if dx>=dy:
                # the angular variation due dx
                a = dy/dx if dx != 0 else 0
                # for each add on x
                for i in range(dx+1):
                    # set the pixel on gpu
                    GL.polypoint2D([int(x),
                                    int(y)],
                                    colors)
                    # move towards x
                    x+=sign_dx
                    # rise angular variation
                    y+=sign_dy*a 

            #vertical 
            if dy>dx:
                # the angular variation due dy
                a = dx/dy if dy != 0 else 0
                # for each add on dy
                for i in range(dy+1):
                    # set the pixel on gpu
                    GL.polypoint2D([int(x),
                                    int(y)],
                                    colors)
                    # move towards y
                    x+=sign_dx*a
                    # dash angular variation
                    y+=sign_dy
    
    @staticmethod # Used to create a 2D Triangle on screen
    def triangleSet2D(vertices, colors):

        for i in range(len(vertices)//6):
            i *= 6

            x1, x2, x3 = int(vertices[i+0]), int(vertices[i+2]), int(vertices[i+4])
            y1, y2, y3 = int(vertices[i+1]), int(vertices[i+3]), int(vertices[i+5])

            xmin, ymin = min(x1,x2,x3), min(y1,y2,y3)
            xmax, ymax = max(x1,x2,x3), max(y1,y2,y3)

            for y in range(ymin,ymax):
                for x in range(xmin,xmax):
                    
                    linha1 = (y2-y1)*x - (x2-x1)*y + y1*(x2-x1) - x1*(y2-y1)
                    if linha1 < 0:
                        continue
                    
                    linha2 = (y3-y2)*x - (x3-x2)*y + y2*(x3-x2) - x2*(y3-y2)
                    if linha2 < 0:
                        continue

                    linha3 = (y1-y3)*x - (x1-x3)*y + y3*(x1-x3) - x3*(y1-y3)
                    if linha3 < 0:
                        continue

                    GL.polypoint2D([x,y],colors)

    @staticmethod # Used to create a 3D Triangle on screen
    def triangleSet(point, colors):

        vertices = lab3D.CreateTriangle3D(point,GL.view_matrix,GL.stack)

        #print("\n Render: \n{0}".format(vertices), end="\n")
        GL.triangleSet2D(vertices, colors)

    @staticmethod # Used to create a Virtual Camera
    def viewpoint(position, orientation, fieldOfView):

        screen_matrix = np.diag([GL.width/2,-GL.height/2,1,1])
        screen_matrix[3] = [GL.width/2,GL.height/2,0,1]
        screen_matrix = screen_matrix.transpose()

        persp_matrix = np.identity(4)
        fieldOfView = lab3D.Tfovy(fieldOfView,GL.width,GL.height)
        persp_matrix[0][0] = GL.height/fieldOfView/GL.width
        persp_matrix[1][1] = 1/fieldOfView
        persp_matrix[2][2] = -(GL.far+GL.near)/(GL.far-GL.near)
        persp_matrix[2][3] = -2*GL.far*GL.near/(GL.far-GL.near)
        persp_matrix[3][2] = -1
        persp_matrix[3][3] = 0

        try: position 
        except: position = np.full(3,0)
        position = (np.array(position)*(-1)).tolist()
        position_matrix = np.identity(4)
        position_matrix[3] = position + [1]
        position_matrix = position_matrix.transpose()

        try: orientation
        except: orientation = np.full(4,0)
        orientation_matrix = lab3D.Rotate3D(orientation).transpose()

        lookat_matrix = np.identity(4)
        lookat_matrix = np.matmul(position_matrix,lookat_matrix)
        lookat_matrix = np.matmul(orientation_matrix,lookat_matrix)

        view_matrix = np.identity(4)
        view_matrix = np.matmul(lookat_matrix,view_matrix)
        view_matrix = np.matmul(persp_matrix,view_matrix)
        view_matrix = np.matmul(screen_matrix,view_matrix)

        #print("\n View: \n{0}".format(view_matrix), end="\n")
        GL.view_matrix = view_matrix

    @staticmethod # Used to manage Input Transformation
    def transform_in(translation, scale, rotation):

        try: scale 
        except: scale = np.full(3,1)
        scale_matrix = np.identity(4)
        for i in range(3): scale_matrix[i][i] = scale[i]

        try: translation 
        except: translation = np.full(3,0)
        translation_matrix = np.identity(4)
        translation_matrix[3] = translation + [1]
        translation_matrix = translation_matrix.transpose()

        try: rotation 
        except: rotation = np.full(4,0)
        rotation_matrix = lab3D.Rotate3D(rotation)

        model_matrix = np.identity(4)
        model_matrix = np.matmul(scale_matrix,model_matrix)
        model_matrix = np.matmul(rotation_matrix,model_matrix)
        model_matrix = np.matmul(translation_matrix,model_matrix)

        #print("\n Transform IN: \n{0}".format(model_matrix), end="\n")
        GL.stack.append(np.matmul(GL.stack[-1],model_matrix))
        
    @staticmethod # Used to delete last Input Transformation
    def transform_out():
        GL.stack.pop()

    @staticmethod # Strip of triangles (stripCount determines the lenth of each strip)
    def triangleStripSet(point, stripCount, colors):

        strip = lab3D.Strip(point)
        
        stripEnd = 0
        for i in range(len(strip)-2):
            if stripEnd == stripCount[0]:
                stripCount.pop(0) if len(stripCount) > 1 else None
                stripEnd = 0
                continue
            elif i%2 == 0:
                try: GL.triangleSet(strip[i]+strip[i+1]+strip[i+2],colors)
                except: continue
            elif i%2 != 0:
                try: GL.triangleSet(strip[i]+strip[i+2]+strip[i+1],colors)
                except: continue
            stripEnd += 1
                
    @staticmethod # Strip of triangles (index determines by -1 the lenth of each strip)
    def indexedTriangleStripSet(point, index, colors):

        strip = lab3D.Strip(point)

        for i in index:
            if i == -1:
                continue
            elif i%2 == 0:
                try: GL.triangleSet(strip[i]+strip[i+1]+strip[i+2],colors)
                except: continue
            elif i%2 != 0:
                try: GL.triangleSet(strip[i]+strip[i+2]+strip[i+1],colors)
                except: continue

    @staticmethod # Used to create a 3D Face on screen
    def indexedFaceSet(coord, coordIndex, colorPerVertex=False, color=None, colorIndex=None,
                       texCoord=None, texCoordIndex=None, colors=base_color, current_texture=None):
        
        # O QUE FALTA FAZER:
        # TRANSPARÊNCIA(.4), ZBUFFER(.4), TEXTURA(.5), PRIMITIVAS(.5), ILUMINAÇÃO(.6), ANIMAÇÃO(.6)

        start = time.process_time()

        texCoord = lab3D.ListSlicer(texCoord,2,condition=texCoord)
        print(texCoord,'\n',texCoordIndex,'\n',current_texture,'\n')

        color = lab3D.ListSlicer(color,3,condition=color)

        strip = lab3D.Strip(coord)

        face = []
        for i in coordIndex:
            if i != -1:
                face.append(i)
                continue
            
            for f in range((len(face)-1)//2):
                f *= 2

                colors = [color[i] for i in face] if color else colors

                triangle3D = strip[face[0]]+strip[face[f+1]]+strip[face[f+2]]

                vertices3D = lab3D.CreateTriangle3D(triangle3D,GL.view_matrix,GL.stack)

                for i in range(len(vertices3D)//9):
                    i *= 9

                    x = [0, int(vertices3D[i+0]), int(vertices3D[i+3]), int(vertices3D[i+6])]
                    y = [0, int(vertices3D[i+1]), int(vertices3D[i+4]), int(vertices3D[i+7])]
                    z = [0, int(vertices3D[i+2]), int(vertices3D[i+5]), int(vertices3D[i+8])]

                    xmin, ymin = min(x[1],x[2],x[3]), min(y[1],y[2],y[3])
                    xmax, ymax = max(x[1],x[2],x[3]), max(y[1],y[2],y[3])

                    for y[0] in range(ymin,ymax):
                        for x[0] in range(xmin,xmax):

                            linha1 = (y[2]-y[1])*x[0] - (x[2]-x[1])*y[0] + y[1]*(x[2]-x[1]) - x[1]*(y[2]-y[1])
                            if linha1 < 0:
                                continue
                            
                            linha2 = (y[3]-y[2])*x[0] - (x[3]-x[2])*y[0] + y[2]*(x[3]-x[2]) - x[2]*(y[3]-y[2])
                            if linha2 < 0:
                                continue

                            linha3 = (y[1]-y[3])*x[0] - (x[1]-x[3])*y[0] + y[3]*(x[1]-x[3]) - x[3]*(y[1]-y[3])
                            if linha3 < 0:
                                continue

                            if (x[0] < 0 or x[0] >= GL.width) or (y[0] < 0 or y[0] >= GL.height):
                                continue
                            
                            interp = lab3D.PixelInterp(x,y)

                            rgb = lab3D.ColorInterp(z,interp,colors) if color else lab3D.ColorFlat(colors)
                            
                            #rgb = lab3D.Texture(x,y,interp) if texCoord else rgb

                            gpu.GPU.draw_pixel([x[0], y[0]], gpu.GPU.RGB8, rgb)

            face = []

        finish = time.process_time()
        print("Code consumed {} seconds".format(round(finish-start,2)))

    """ PRIMITIVES """

    @staticmethod
    def box(size, colors):
        """Função usada para renderizar Boxes."""
        # A função box é usada para desenhar paralelepípedos na cena. O Box é centrada no
        # (0, 0, 0) no sistema de coordenadas local e alinhado com os eixos de coordenadas
        # locais. O argumento size especifica as extensões da caixa ao longo dos eixos X, Y
        # e Z, respectivamente, e cada valor do tamanho deve ser maior que zero. Para desenha
        # essa caixa você vai provavelmente querer tesselar ela em triângulos, para isso
        # encontre os vértices e defina os triângulos.

        # Não sei não, só n rolou
        GL.indexedFaceSet([-3.0, 0.5, -0.5, 3.0, 0.5, 0.5, -3.0, 1.5, -0.5, 3.0, 1.5, 0.5],
                          [0, 1, 2, -1, 1, 3, 2, -1])

    @staticmethod
    def sphere(radius, colors):
        """Função usada para renderizar Esferas."""
        # A função sphere é usada para desenhar esferas na cena. O esfera é centrada no
        # (0, 0, 0) no sistema de coordenadas local. O argumento radius especifica o
        # raio da esfera que está sendo criada. Para desenha essa esfera você vai
        # precisar tesselar ela em triângulos, para isso encontre os vértices e defina
        # os triângulos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Sphere : radius = {0}".format(radius)) # imprime no terminal o raio da esfera
        print("Sphere : colors = {0}".format(colors)) # imprime no terminal as cores

    """ LIGHT """

    @staticmethod
    def navigationInfo(headlight):
        """Características físicas do avatar do visualizador e do modelo de visualização."""
        # O campo do headlight especifica se um navegador deve acender um luz direcional que
        # sempre aponta na direção que o usuário está olhando. Definir este campo como TRUE
        # faz com que o visualizador forneça sempre uma luz do ponto de vista do usuário.
        # A luz headlight deve ser direcional, ter intensidade = 1, cor = (1 1 1),
        # ambientIntensity = 0,0 e direção = (0 0 −1).

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        #print("NavigationInfo : headlight = {0}".format(headlight)) # imprime no terminal

    @staticmethod
    def directionalLight(ambientIntensity, color, intensity, direction):
        """Luz direcional ou paralela."""
        # Define uma fonte de luz direcional que ilumina ao longo de raios paralelos
        # em um determinado vetor tridimensional. Possui os campos básicos ambientIntensity,
        # cor, intensidade. O campo de direção especifica o vetor de direção da iluminação
        # que emana da fonte de luz no sistema de coordenadas local. A luz é emitida ao
        # longo de raios paralelos de uma distância infinita.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("DirectionalLight : ambientIntensity = {0}".format(ambientIntensity))
        print("DirectionalLight : color = {0}".format(color)) # imprime no terminal
        print("DirectionalLight : intensity = {0}".format(intensity)) # imprime no terminal
        print("DirectionalLight : direction = {0}".format(direction)) # imprime no terminal

    @staticmethod
    def pointLight(ambientIntensity, color, intensity, location):
        """Luz pontual."""
        # Fonte de luz pontual em um local 3D no sistema de coordenadas local. Uma fonte
        # de luz pontual emite luz igualmente em todas as direções; ou seja, é omnidirecional.
        # Possui os campos básicos ambientIntensity, cor, intensidade. Um nó PointLight ilumina
        # a geometria em um raio de sua localização. O campo do raio deve ser maior ou igual a
        # zero. A iluminação do nó PointLight diminui com a distância especificada.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("PointLight : ambientIntensity = {0}".format(ambientIntensity))
        print("PointLight : color = {0}".format(color)) # imprime no terminal
        print("PointLight : intensity = {0}".format(intensity)) # imprime no terminal
        print("PointLight : location = {0}".format(location)) # imprime no terminal

    @staticmethod
    def fog(visibilityRange, color):
        """Névoa."""
        # O nó Fog fornece uma maneira de simular efeitos atmosféricos combinando objetos
        # com a cor especificada pelo campo de cores com base nas distâncias dos
        # vários objetos ao visualizador. A visibilidadeRange especifica a distância no
        # sistema de coordenadas local na qual os objetos são totalmente obscurecidos
        # pela névoa. Os objetos localizados fora de visibilityRange do visualizador são
        # desenhados com uma cor de cor constante. Objetos muito próximos do visualizador
        # são muito pouco misturados com a cor do nevoeiro.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Fog : color = {0}".format(color)) # imprime no terminal
        print("Fog : visibilityRange = {0}".format(visibilityRange))

    """ TIMERS """

    @staticmethod
    def timeSensor(cycleInterval, loop):
        """Gera eventos conforme o tempo passa."""
        # Os nós TimeSensor podem ser usados para muitas finalidades, incluindo:
        # Condução de simulações e animações contínuas; Controlar atividades periódicas;
        # iniciar eventos de ocorrência única, como um despertador;
        # Se, no final de um ciclo, o valor do loop for FALSE, a execução é encerrada.
        # Por outro lado, se o loop for TRUE no final de um ciclo, um nó dependente do
        # tempo continua a execução no próximo ciclo. O ciclo de um nó TimeSensor dura
        # cycleInterval segundos. O valor de cycleInterval deve ser maior que zero.

        # Deve retornar a fração de tempo passada em fraction_changed

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("TimeSensor : cycleInterval = {0}".format(cycleInterval)) # imprime no terminal
        print("TimeSensor : loop = {0}".format(loop))

        # Esse método já está implementado para os alunos como exemplo
        epoch = time.time()  # time in seconds since the epoch as a floating point number.
        fraction_changed = (epoch % cycleInterval) / cycleInterval

        return fraction_changed

    @staticmethod
    def splinePositionInterpolator(set_fraction, key, keyValue, closed):
        """Interpola não linearmente entre uma lista de vetores 3D."""
        # Interpola não linearmente entre uma lista de vetores 3D. O campo keyValue possui
        # uma lista com os valores a serem interpolados, key possui uma lista respectiva de chaves
        # dos valores em keyValue, a fração a ser interpolada vem de set_fraction que varia de
        # zeroa a um. O campo keyValue deve conter exatamente tantos vetores 3D quanto os
        # quadros-chave no key. O campo closed especifica se o interpolador deve tratar a malha
        # como fechada, com uma transições da última chave para a primeira chave. Se os keyValues
        # na primeira e na última chave não forem idênticos, o campo closed será ignorado.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("SplinePositionInterpolator : set_fraction = {0}".format(set_fraction))
        print("SplinePositionInterpolator : key = {0}".format(key)) # imprime no terminal
        print("SplinePositionInterpolator : keyValue = {0}".format(keyValue))
        print("SplinePositionInterpolator : closed = {0}".format(closed))

        # Abaixo está só um exemplo de como os dados podem ser calculados e transferidos
        value_changed = [0.0, 0.0, 0.0]
        
        return value_changed

    @staticmethod
    def orientationInterpolator(set_fraction, key, keyValue):
        """Interpola entre uma lista de valores de rotação especificos."""
        # Interpola rotações são absolutas no espaço do objeto e, portanto, não são cumulativas.
        # Uma orientação representa a posição final de um objeto após a aplicação de uma rotação.
        # Um OrientationInterpolator interpola entre duas orientações calculando o caminho mais
        # curto na esfera unitária entre as duas orientações. A interpolação é linear em
        # comprimento de arco ao longo deste caminho. Os resultados são indefinidos se as duas
        # orientações forem diagonalmente opostas. O campo keyValue possui uma lista com os
        # valores a serem interpolados, key possui uma lista respectiva de chaves
        # dos valores em keyValue, a fração a ser interpolada vem de set_fraction que varia de
        # zeroa a um. O campo keyValue deve conter exatamente tantas rotações 3D quanto os
        # quadros-chave no key.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("OrientationInterpolator : set_fraction = {0}".format(set_fraction))
        print("OrientationInterpolator : key = {0}".format(key)) # imprime no terminal
        print("OrientationInterpolator : keyValue = {0}".format(keyValue))

        # Abaixo está só um exemplo de como os dados podem ser calculados e transferidos
        value_changed = [0, 0, 1, 0]

        return value_changed

    """ FUTURE """

    def vertex_shader(self, shader):
        """Para no futuro implementar um vertex shader."""

    def fragment_shader(self, shader):
        """Para no futuro implementar um fragment shader."""
