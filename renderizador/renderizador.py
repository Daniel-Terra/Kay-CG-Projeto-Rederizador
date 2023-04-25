#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Renderizador X3D.

Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
Disciplina: Computação Gráfica
Data: 28 de Agosto de 2020
"""

import os           # Para rotinas do sistema operacional
import argparse     # Para tratar os parâmetros da linha de comando

import gl           # Recupera rotinas de suporte ao X3D

import interface    # Janela de visualização baseada no Matplotlib
import gpu          # Simula os recursos de uma GPU

import x3d          # Faz a leitura do arquivo X3D, gera o grafo de cena e faz traversal
import scenegraph   # Imprime o grafo de cena no console

import numpy as np

LARGURA = 60  # Valor padrão para largura da tela
ALTURA = 40   # Valor padrão para altura da tela

class Renderizador:
    """Realiza a renderização da cena informada."""

    def __init__(self):
        """Definindo valores padrão."""
        self.width = LARGURA
        self.height = ALTURA
        self.x3d_file = ""
        self.image_file = "tela.png"
        self.scene = None
        self.framebuffers = {}

    def setup(self):
        """Configura o sistema para a renderização."""
        
        # Creating all framebuffers
        fbo = gpu.GPU.gen_framebuffers(3)
        self.framebuffers["FRONT"] = fbo[0]
        self.framebuffers["SUPER"] = fbo[1]
        
        # --- FRONT ----
        gpu.GPU.framebuffer_storage(
            self.framebuffers["FRONT"],
            gpu.GPU.COLOR_ATTACHMENT, gpu.GPU.RGB8,
            self.width, self.height
        )

        # --- SUPER ----
        gpu.GPU.framebuffer_storage(
            self.framebuffers["SUPER"],
            gpu.GPU.COLOR_ATTACHMENT, gpu.GPU.RGB8,
            self.width*2, self.height*2
        )

        # Descomente as seguintes linhas se for usar um Framebuffer para profundidade
        # gpu.GPU.framebuffer_storage(
        #     self.framebuffers["FRONT"],
        #     gpu.GPU.DEPTH_ATTACHMENT,
        #     gpu.GPU.DEPTH_COMPONENT32F,
        #     self.width,
        #     self.height
        # )
    
        # Opções:
        # - COLOR_ATTACHMENT: alocações para as cores da imagem renderizada
        # - DEPTH_ATTACHMENT: alocações para as profundidades da imagem renderizada
        # Obs: Você pode chamar duas vezes a rotina com cada tipo de buffer.

        # Tipos de dados:
        # - RGB8: Para canais de cores (Vermelho, Verde, Azul) 8bits cada (0-255)
        # - RGBA8: Para canais de cores (Vermelho, Verde, Azul, Transparência) 8bits cada (0-255)
        # - DEPTH_COMPONENT16: Para canal de Profundidade de 16bits (half-precision) (0-65535)
        # - DEPTH_COMPONENT32F: Para canal de Profundidade de 32bits (single-precision) (float)

        gpu.GPU.clear_color([0, 0, 0]) # Por default preto
        gpu.GPU.clear_depth(1.0) # Assuma 1.0 o mais afastado e -1.0 o mais próximo da camera
        self.scene.viewport(width=self.width, height=self.height) # Definindo tamanho do Viewport para renderização

    def pre(self):
        """Rotinas pré renderização."""
        # Função invocada antes do processo de renderização iniciar.

        gpu.GPU.clear_buffer() # Limpa o frame buffers atual

        gpu.GPU.bind_framebuffer(gpu.GPU.DRAW_FRAMEBUFFER, self.framebuffers["SUPER"])

    def pos(self):
        """Rotinas pós renderização."""

        gpu.GPU.bind_framebuffer(gpu.GPU.READ_FRAMEBUFFER, self.framebuffers["SUPER"])

        gpu.GPU.bind_framebuffer(gpu.GPU.DRAW_FRAMEBUFFER, self.framebuffers["FRONT"])
        
        for x in range(self.width-1):
            for y in range(self.height-1):

                x1 = gpu.GPU.read_pixel([x*2+0,y*2],gpu.GPU.RGB8)
                x2 = gpu.GPU.read_pixel([x*2+1,y*2],gpu.GPU.RGB8)
                y1 = gpu.GPU.read_pixel([x*2,y*2+0],gpu.GPU.RGB8)
                y2 = gpu.GPU.read_pixel([x*2,y*2+1],gpu.GPU.RGB8)

                AVGcolor = (x1*.25 + x2*.25 + y1*.25 + y2*.25)

                gpu.GPU.draw_pixel([x,y],gpu.GPU.RGB8,AVGcolor)

        gpu.GPU.bind_framebuffer(gpu.GPU.READ_FRAMEBUFFER, self.framebuffers["FRONT"])

    def mapping(self):
        """Mapeamento de funções para as rotinas de renderização."""
        # Rotinas encapsuladas na classe GL (Graphics Library)
        x3d.X3D.renderer["Polypoint2D"] = gl.GL.polypoint2D
        x3d.X3D.renderer["Polyline2D"] = gl.GL.polyline2D
        x3d.X3D.renderer["TriangleSet2D"] = gl.GL.triangleSet2D
        x3d.X3D.renderer["TriangleSet"] = gl.GL.triangleSet
        x3d.X3D.renderer["Viewpoint"] = gl.GL.viewpoint
        x3d.X3D.renderer["Transform_in"] = gl.GL.transform_in
        x3d.X3D.renderer["Transform_out"] = gl.GL.transform_out
        x3d.X3D.renderer["TriangleStripSet"] = gl.GL.triangleStripSet
        x3d.X3D.renderer["IndexedTriangleStripSet"] = gl.GL.indexedTriangleStripSet
        x3d.X3D.renderer["IndexedFaceSet"] = gl.GL.indexedFaceSet
        x3d.X3D.renderer["Box"] = gl.GL.box
        x3d.X3D.renderer["Sphere"] = gl.GL.sphere
        x3d.X3D.renderer["NavigationInfo"] = gl.GL.navigationInfo
        x3d.X3D.renderer["DirectionalLight"] = gl.GL.directionalLight
        x3d.X3D.renderer["PointLight"] = gl.GL.pointLight
        x3d.X3D.renderer["Fog"] = gl.GL.fog
        x3d.X3D.renderer["TimeSensor"] = gl.GL.timeSensor
        x3d.X3D.renderer["SplinePositionInterpolator"] = gl.GL.splinePositionInterpolator
        x3d.X3D.renderer["OrientationInterpolator"] = gl.GL.orientationInterpolator

    def render(self):
        """Laço principal de renderização."""
        self.pre()  # executa rotina pré renderização
        self.scene.render()  # faz o traversal no grafo de cena
        self.pos()  # executa rotina pós renderização
        return gpu.GPU.get_frame_buffer()

    def main(self):
        """Executa a renderização."""
        # Tratando entrada de parâmetro
        parser = argparse.ArgumentParser(add_help=False)   # parser para linha de comando
        parser.add_argument("-i", "--input", help="arquivo X3D de entrada")
        parser.add_argument("-o", "--output", help="arquivo 2D de saída (imagem)")
        parser.add_argument("-w", "--width", help="resolução horizonta", type=int)
        parser.add_argument("-h", "--height", help="resolução vertical", type=int)
        parser.add_argument("-g", "--graph", help="imprime o grafo de cena", action='store_true')
        parser.add_argument("-p", "--pause", help="começa simulação em pausa", action='store_true')
        parser.add_argument("-q", "--quiet", help="não exibe janela", action='store_true')
        args = parser.parse_args() # parse the arguments
        if args.input:
            self.x3d_file = args.input
        if args.output:
            self.image_file = args.output
        if args.width:
            self.width = args.width
        if args.height:
            self.height = args.height

        path = os.path.dirname(os.path.abspath(self.x3d_file))

        # Iniciando simulação de GPU
        gpu.GPU(self.image_file, path)

        # Abre arquivo X3D
        self.scene = x3d.X3D(self.x3d_file)

        # Iniciando Biblioteca Gráfica
        gl.GL.setup(
            self.width,
            self.height,
            near=0.01,
            far=1000
        )

        # Funções que irão fazer o rendering
        self.mapping()

        # Se no modo silencioso não configurar janela de visualização
        if not args.quiet:
            window = interface.Interface(self.width, self.height, self.x3d_file)
            self.scene.set_preview(window)

        # carrega os dados do grafo de cena
        if self.scene:
            self.scene.parse()
            if args.graph:
                scenegraph.Graph(self.scene.root)

        # Configura o sistema para a renderização.
        self.setup()

        # Se no modo silencioso salvar imagem e não mostrar janela de visualização
        if args.quiet:
            gpu.GPU.save_image()  # Salva imagem em arquivo
        else:
            window.set_saver(gpu.GPU.save_image)  # pasa a função para salvar imagens
            window.preview(args.pause, self.render)  # mostra visualização

if __name__ == '__main__':
    renderizador = Renderizador()
    renderizador.main()
