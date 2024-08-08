import cv2
import numpy as np
import time
from rplidar import RPLidar
import serial

# Função para determinar se há uma parede à frente a uma distância de 5 cm ou menos
def detectar_parede_frente(rplidar, distancia_limite=500):  # Distância em milímetros
    # Obtém dados do RPLIDAR
    scan_data = [scan[2] for scan in rplidar.iter_scans()]

    # Verifica se há uma parede à frente
    frente = any(0 < angulo < 180 and 0 < distancia < distancia_limite for angulo, distancia in scan_data)

    return frente

# Função para determinar se há espaço à direita
def verificar_espaco_direita(scan_data, angulo_limite=45, distancia_limite=500):
    # Filtra os dados para obter apenas leituras à direita
    leituras_direita = [(angulo, distancia) for angulo, distancia in scan_data if 0 < angulo < angulo_limite]

    # Verifica se há espaço suficiente à direita
    espaco_suficiente = any(distancia > distancia_limite for _, distancia in leituras_direita)

    return espaco_suficiente

# Função para enviar comandos para o Arduino via comunicação serial
def enviar_comando_arduino(ser, comando):
    ser.write(comando.encode())

# Inicializa o RPLidar (substitua '/dev/ttyUSB0' pela porta correta)
rplidar = RPLidar('/dev/ttyUSB0')

# Inicializa a comunicação serial com o Arduino (ajuste a porta serial conforme necessário)
ser = serial.Serial('/dev/ttyACM0', 9600)

# Tempo entre cada captura de imagem em segundos
intervalo_captura = 1

while True:
    # Captura um frame da câmera
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    # Convertendo o frame para escala de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Aplicando um desfoque para reduzir o ruído
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detecção de bordas usando Canny
    edges = cv2.Canny(blurred, 30, 90)

    # Encontrando contornos na imagem
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Limiar de confiança para considerar um obstáculo detectado
    confidence_threshold = 0.1  # Ajuste conforme necessário

    # Verificando se há contornos (obstáculos) na frente na imagem
    if len(contours) > 0:
        # Se houver obstáculos na imagem, enviar sinal para o Arduino parar o carrinho
        print("Obstáculo detectado na imagem! Parando o carrinho.")
        enviar_comando_arduino(ser, 'S')

    else:
        # Se não houver obstáculos na imagem, continuar verificando a presença de paredes com o RPLidar
        if detectar_parede_frente(rplidar):
            # Verifica se há espaço à direita
            if verificar_espaco_direita(rplidar.iter_scans()):
                # Se há espaço à direita, vira à direita
                print("Parede à frente! Espaço à direita. Virando à direita.")
                enviar_comando_arduino(ser, 'R')
            else:
                # Se não há espaço à direita, vira à esquerda
                print("Parede à frente! Sem espaço à direita. Virando à esquerda.")
                enviar_comando_arduino(ser, 'L')

        else:
            # Se não houver obstáculos na imagem e não detectar parede à frente, mover para frente
            print("Nenhum obstáculo na imagem. Nenhuma parede à frente. Movendo para frente.")
            enviar_comando_arduino(ser, 'F')

    # Aguarda o intervalo entre as capturas
    time.sleep(intervalo_captura)

# Liberando os recursos
rplidar.stop()
rplidar.disconnect()
ser.close()
cv2.destroyAllWindows()
