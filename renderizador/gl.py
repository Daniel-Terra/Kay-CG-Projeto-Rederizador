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
    model_matrix = np.identity(4)
    view_matrix = np.identity(4)

    @staticmethod
    def setup(width, height, near=0.01, far=1000):
        """Definir parametros para câmera de razão de aspecto, plano próximo e distante."""

        GL.width = width
        GL.height = height
        GL.near = near
        GL.far = far

    @staticmethod
    def polypoint2D(point, colors):
        """Função usada para renderizar Polypoint2D."""

        colors = (np.array(colors['emissiveColor'])*255).tolist()
        colors = [int(color) for color in colors]

        for i in range(len(point)):
            if (i%2) == 0:
                x,y = int(point[i]),int(point[i+1])
                if (x >= 0 and x < GL.width) and (y >= 0 and y < GL.height):
                    gpu.GPU.draw_pixel([x, y], gpu.GPU.RGB8, colors)

    @staticmethod
    def polyline2D(lineSegments, colors):
        """Função usada para renderizar Polyline2D."""

        # gets four by four the list to create each line
        linha = []
        for num in lineSegments:
            linha.append(int(num))
            if len(linha) == 4:
                
                # where do we wanna get and the list of the points that will be written
                target = [linha[2],linha[3]]
                point  = [linha[0],linha[1]]
                
                # iterative x and y
                x = linha[0]
                y = linha[1]

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
    
    @staticmethod
    def triangleSet2D(vertices, colors):
        """Função usada para renderizar TriangleSet2D."""
        
        # gets six by six the list to create each triangle as a matrix
        xy = []
        triangulo = []
        for num in vertices:
            xy.append(int(num))
            if len(xy) == 2:
                triangulo.append(xy)
                xy = []
                if len(triangulo) == 3:

                    # declaring the vertices of the triangle
                    x1, x2, x3 = triangulo[0][0], triangulo[1][0], triangulo[2][0]
                    y1, y2, y3 = triangulo[0][1], triangulo[1][1], triangulo[2][1]
                    
                    # using min and max of each x and y of the matrix, we discover the bounding box
                    xmin, ymin = min(x1,x2,x3), min(y1,y2,y3)
                    xmax, ymax = max(x1,x2,x3), max(y1,y2,y3)

                    # to loop every single pixel inside the bounding box
                    for y in range(ymin,ymax):
                        for x in range(xmin,xmax):
                            
                            # to test if the value of each point is out or in the triangle
                            linha1 = (y2-y1)*x - (x2-x1)*y + y1*(x2-x1) - x1*(y2-y1)
                            if linha1 < 0:
                                continue
                            
                            linha2 = (y3-y2)*x - (x3-x2)*y + y2*(x3-x2) - x2*(y3-y2)
                            if linha2 < 0:
                                continue

                            linha3 = (y1-y3)*x - (x1-x3)*y + y3*(x1-x3) - x3*(y1-y3)
                            if linha3 < 0:
                                continue

                            # check if the xy is negative or positive relative to the sides
                            if linha1 >= 0 and linha2 >= 0 and linha3 >= 0:
                                # print it in the gpu graf
                                GL.polypoint2D([x,y],colors)

                    triangulo = []

    @staticmethod
    def triangleSet(point, colors):
        """Function to render the triangles called"""        

        point_matrix = np.array([point[i:i + 3] + [1] for i in range(0, len(point), 3)]).transpose()

        print("\n Pontos: \n{0}".format(point_matrix), end="\n")

        render_matrix = np.identity(4)
        render_matrix = np.matmul(render_matrix,GL.view_matrix)
        render_matrix = np.matmul(render_matrix,GL.model_matrix)
        render_matrix = np.matmul(render_matrix,point_matrix)

        for i in range(render_matrix.shape[1]):
            render_matrix[0][i] /= render_matrix[3][i]
            render_matrix[1][i] /= render_matrix[3][i]
            render_matrix[2][i] /= render_matrix[3][i]
            render_matrix[3][i] /= render_matrix[3][i]

        vertices = np.concatenate([ [int(render_matrix[0][i]), int(render_matrix[1][i])] 
                                   for i in range(render_matrix.shape[1])],axis=0).tolist()
        
        print("\n Render: \n{0}".format(vertices), end="\n")
        GL.triangleSet2D(vertices, colors)

    @staticmethod
    def viewpoint(position, orientation, fieldOfView):
        """Function for the virtual camera"""

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

        print("\n View: \n{0}".format(view_matrix), end="\n")
        GL.view_matrix = view_matrix

    @staticmethod
    def transform_in(translation, scale, rotation):
        """Function to manage inputed transformations"""

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

        print("\n Transform IN: \n{0}".format(model_matrix), end="\n")
        GL.model_matrix = model_matrix
        
    @staticmethod
    def transform_out():
        """Função usada para renderizar (na verdade coletar os dados) de Transform."""
        # A função transform_out será chamada quando se sair em um nó X3D do tipo Transform do
        # grafo de cena. Não são passados valores, porém quando se sai de um nó transform se
        # deverá recuperar a matriz de transformação dos modelos do mundo da estrutura de
        # pilha implementada.

        #print("\n Transform OUT: \n{0}".format(" - "), end="\n")

    @staticmethod
    def triangleStripSet(point, stripCount, colors):
        """Função usada para renderizar TriangleStripSet."""
        # A função triangleStripSet é usada para desenhar tiras de triângulos interconectados,
        # você receberá as coordenadas dos pontos no parâmetro point, esses pontos são uma
        # lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x
        # do primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
        # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e assim
        # por diante. No TriangleStripSet a quantidade de vértices a serem usados é informado
        # em uma lista chamada stripCount (perceba que é uma lista). Ligue os vértices na ordem,
        # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
        # depois 2, 3 e 4, e assim por diante. Cuidado com a orientação dos vértices, ou seja,
        # todos no sentido horário ou todos no sentido anti-horário, conforme especificado.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("TriangleStripSet : pontos = {0} ".format(point), end='')
        for i, strip in enumerate(stripCount):
            print("strip[{0}] = {1} ".format(i, strip), end='')
        print("")
        print("TriangleStripSet : colors = {0}".format(colors)) # imprime no terminal as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        gpu.GPU.draw_pixel([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

    @staticmethod
    def indexedTriangleStripSet(point, index, colors):
        """Função usada para renderizar IndexedTriangleStripSet."""
        # A função indexedTriangleStripSet é usada para desenhar tiras de triângulos
        # interconectados, você receberá as coordenadas dos pontos no parâmetro point, esses
        # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor
        # da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto, point[2]
        # o valor z da coordenada z do primeiro ponto. Já point[3] é a coordenada x do
        # segundo ponto e assim por diante. No IndexedTriangleStripSet uma lista informando
        # como conectar os vértices é informada em index, o valor -1 indica que a lista
        # acabou. A ordem de conexão será de 3 em 3 pulando um índice. Por exemplo: o
        # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
        # depois 2, 3 e 4, e assim por diante. Cuidado com a orientação dos vértices, ou seja,
        # todos no sentido horário ou todos no sentido anti-horário, conforme especificado.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("IndexedTriangleStripSet : pontos = {0}, index = {1}".format(point, index))
        print("IndexedTriangleStripSet : colors = {0}".format(colors)) # imprime as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        gpu.GPU.draw_pixel([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

    @staticmethod
    def box(size, colors):
        """Função usada para renderizar Boxes."""
        # A função box é usada para desenhar paralelepípedos na cena. O Box é centrada no
        # (0, 0, 0) no sistema de coordenadas local e alinhado com os eixos de coordenadas
        # locais. O argumento size especifica as extensões da caixa ao longo dos eixos X, Y
        # e Z, respectivamente, e cada valor do tamanho deve ser maior que zero. Para desenha
        # essa caixa você vai provavelmente querer tesselar ela em triângulos, para isso
        # encontre os vértices e defina os triângulos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Box : size = {0}".format(size)) # imprime no terminal pontos
        print("Box : colors = {0}".format(colors)) # imprime no terminal as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        gpu.GPU.draw_pixel([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

    @staticmethod
    def indexedFaceSet(coord, coordIndex, colorPerVertex, color, colorIndex,
                       texCoord, texCoordIndex, colors, current_texture):
        """Função usada para renderizar IndexedFaceSet."""
        # A função indexedFaceSet é usada para desenhar malhas de triângulos. Ela funciona de
        # forma muito simular a IndexedTriangleStripSet porém com mais recursos.
        # Você receberá as coordenadas dos pontos no parâmetro cord, esses
        # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim coord[0] é o valor
        # da coordenada x do primeiro ponto, coord[1] o valor y do primeiro ponto, coord[2]
        # o valor z da coordenada z do primeiro ponto. Já coord[3] é a coordenada x do
        # segundo ponto e assim por diante. No IndexedFaceSet uma lista de vértices é informada
        # em coordIndex, o valor -1 indica que a lista acabou.
        # A ordem de conexão será de 3 em 3 pulando um índice. Por exemplo: o
        # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
        # depois 2, 3 e 4, e assim por diante.
        # Adicionalmente essa implementação do IndexedFace aceita cores por vértices, assim
        # se a flag colorPerVertex estiver habilitada, os vértices também possuirão cores
        # que servem para definir a cor interna dos poligonos, para isso faça um cálculo
        # baricêntrico de que cor deverá ter aquela posição. Da mesma forma se pode definir uma
        # textura para o poligono, para isso, use as coordenadas de textura e depois aplique a
        # cor da textura conforme a posição do mapeamento. Dentro da classe GPU já está
        # implementadado um método para a leitura de imagens.

        # Os prints abaixo são só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("IndexedFaceSet : ")
        if coord:
            print("\tpontos(x, y, z) = {0}, coordIndex = {1}".format(coord, coordIndex))
        print("colorPerVertex = {0}".format(colorPerVertex))
        if colorPerVertex and color and colorIndex:
            print("\tcores(r, g, b) = {0}, colorIndex = {1}".format(color, colorIndex))
        if texCoord and texCoordIndex:
            print("\tpontos(u, v) = {0}, texCoordIndex = {1}".format(texCoord, texCoordIndex))
        if current_texture:
            image = gpu.GPU.load_texture(current_texture[0])
            print("\t Matriz com image = {0}".format(image))
            print("\t Dimensões da image = {0}".format(image.shape))
        print("IndexedFaceSet : colors = {0}".format(colors))  # imprime no terminal as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        gpu.GPU.draw_pixel([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

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

    # Para o futuro (Não para versão atual do projeto.)
    def vertex_shader(self, shader):
        """Para no futuro implementar um vertex shader."""

    def fragment_shader(self, shader):
        """Para no futuro implementar um fragment shader."""
