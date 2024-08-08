import cv2
import numpy as np
import matplotlib.pyplot as plt

# Função para encontrar correspondências ORB + RANSAC
def encontrar_correspondencias(img_referencia, img_camera, limiar=50):
    # Implementação do ORB + RANSAC ...
	orb = cv2.ORB_create()

    # Encontrar os keypoints e descritores com o ORB
    kp_referencia, des_referencia = orb.detectAndCompute(img_referencia, None)
    kp_camera, des_camera = orb.detectAndCompute(img_camera, None)

    # Inicializar o BFMatcher (Brute-Force Matcher)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # Match features
    matches = bf.match(des_referencia, des_camera)

    # Ordenar os matches com base na distância
    matches = sorted(matches, key=lambda x: x.distance)

    # Calcular a distância média dos matches
    distancias = [match.distance for match in matches]
    distancia_media = np.mean(distancias)

    # Imprimir as correspondências (opcional)
    img_correspondencias = cv2.drawMatches(img_referencia, kp_referencia, img_camera, kp_camera, matches[:10], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    cv2.imshow("Correspondencias", img_correspondencias)

    # Verificar se as imagens estão alinhadas com base no limiar
    if distancia_media < limiar:
        # Obter os pontos correspondentes
        pontos_referencia = np.float32([kp_referencia[match.queryIdx].pt for match in matches]).reshape(-1, 1, 2)
        pontos_camera = np.float32([kp_camera[match.trainIdx].pt for match in matches]).reshape(-1, 1, 2)

        # Calcular a matriz de transformação
        matriz_transformacao, _ = cv2.findHomography(pontos_referencia, pontos_camera, cv2.RANSAC, 5.0)

        # Verificar se os pontos estão totalmente alinhados
        if matriz_transformacao is not None:
            return True
    return False

# Função para desenhar o mapa de grid com as imagens
def desenhar_mapa(grid_size, imagens_posicoes, imagem_reconhecida_posicao):
    mapa = np.zeros((grid_size, grid_size))

    # Colocar as imagens no mapa
    for posicao in imagens_posicoes:
        x, y = posicao
        mapa[x, y] = 1  # 1 representa a presença de uma imagem

    # Colocar a imagem reconhecida no mapa
    x_rec, y_rec = imagem_reconhecida_posicao
    mapa[x_rec, y_rec] = 3  # 3 representa a posição da imagem reconhecida

    return mapa

# Função para plotar o mapa local usando dados do LiDAR
def plotar_mapa_local(mapa_local, dados_lidar):
    for angulo, distancia in dados_lidar:
        # Converter ângulo para índice de matriz
        indice_angulo = int(angulo % 360)
        
        # Converter distância para índice de matriz (considerando escala apropriada)
        indice_distancia = int(distancia / escala)

        # Adicionar ponto ao mapa local
        mapa_local[indice_distancia, indice_angulo] = 1

    return mapa_local

# Exemplo de imagens previamente posicionadas
imagens_posicoes = [(1, 1), (3, 1), (5, 1), (1, 5), (3, 5), (5, 5), (1, 3), (5, 3)]

# Tamanho do grid
grid_size = 7

# Criar o mapa de grid
mapa = desenhar_mapa(grid_size, imagens_posicoes, (0, 0))  # Inicialmente, a posição da imagem reconhecida é (0, 0)

# Carregar a imagem de referência
imagem_referencia = cv2.imread('/home/rodrigo/Desktop/mosaico/t09.jpg', cv2.IMREAD_GRAYSCALE)

# Inicializar a webcam
cap = cv2.VideoCapture(0)  # 0 representa a câmera padrão do Raspberry Pi

# Inicializar dados do LiDAR
dados_lidar = [(45, 500), (90, 1000), (135, 700), (180, 800)]  # Exemplo de dados do LiDAR

# Escala para converter distâncias do LiDAR para índices de matriz
escala = 10  # Ajuste conforme necessário

# Capturar um único quadro
ret, frame_camera = cap.read()

# Converter o quadro da câmera para escala de cinza
frame_cinza = cv2.cvtColor(frame_camera, cv2.COLOR_BGR2GRAY)

# Verificar se há correspondência e alinhamento
imagem_reconhecida_posicao = None  # Inicializar com None

if encontrar_correspondencias(imagem_referencia, frame_cinza):
    # Obter a posição dinamicamente
    imagem_reconhecida_posicao = (int(kp_camera[matches[0].trainIdx].pt[1] / grid_size), int(kp_camera[matches[0].trainIdx].pt[0] / grid_size))

    # Atualizar a posição da imagem reconhecida no mapa
    mapa = desenhar_mapa(grid_size, imagens_posicoes, imagem_reconhecida_posicao)

    print("Pontos totalmente alinhados encontrados na imagem de referência.")
else:
    print("Não foi encontrada correspondência ou alinhamento suficiente.")

# Criar o mapa local
mapa_local = np.zeros((360, 1000))  # Ajuste o tamanho conforme necessário

# Plotar o mapa local usando dados do LiDAR
mapa_local = plotar_mapa_local(mapa_local, dados_lidar)

# Visualizar o mapa local
plt.imshow(mapa_local, cmap='gray', interpolation='nearest', aspect='auto')
plt.title('Mapa Local com Dados do LiDAR')
plt.show()

# Visualizar o mapa
plt.imshow(mapa, cmap='viridis', interpolation='nearest')
plt.title('Mapa de Grid com Imagens e Posição Reconhecida')
plt.show()

# Mostrar a imagem da câmera (opcional)
cv2.imshow('Video', frame_camera)

# Esperar por uma tecla e depois liberar os recursos
cv2.waitKey(0)
cap.release()
cv2.destroyAllWindows()

