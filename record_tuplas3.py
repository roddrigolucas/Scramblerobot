#!/usr/bin/env python3
'''Records measurements to a given file and plots a 2D map.
Usage example:

$ ./lidar_mapping.py out.txt
'''
import sys
import time
from datetime import datetime
import math
import matplotlib.pyplot as plt
from rplidar import RPLidar
import signal

PORT_NAME = '/dev/ttyUSB0'
# ANGLE_MIN = 0 ##DEFINE O ANGULO MININO
# ANGLE_MAX = 360 ##ANGULO MAXIMO

def lidar_line_to_tuple(line):
    # Obtém o ângulo e a distância da leitura do lidar
    angle = float(line.split('\t')[1])
    distance = float(line.split('\t')[2])

    # Converte para coordenadas cartesianas
    x = distance * math.cos(math.radians(angle))
    y = distance * math.sin(math.radians(angle))

    # Limita as coordenadas entre -300 e 300
    x = max(-400, min(x, 400))
    y = max(-400, min(y, 400))

    return x, y

def filter_non_zero_distance(lidar_data):
    lidar_readings = []

    for line in lidar_data:
        # Ignora linhas em branco
        if not line.strip():
            continue

        # Converte cada linha em uma tupla (x, y)
        x, y = lidar_line_to_tuple(line)

        # Adiciona a tupla (x, y) à lista se a distância for diferente de zero
        if y != 0.0:
            lidar_readings.append((x, y))

    return lidar_readings

def plot_lidar_data(lidar_data):
    # lidar_data é uma lista de tuplas (x, y) representando as leituras do lidar

    # Extrai as coordenadas x e y das leituras
    x_values = [point[0] for point in lidar_data]
    y_values = [point[1] for point in lidar_data]

    # Cria um gráfico de dispersão (scatter plot) das leituras do lidar
    plt.scatter(x_values, y_values, marker='.', color='blue')

    # Configurações do gráfico com limites de -300 a 300 para X e Y
    plt.title('Leituras do Lidar - Plano 2D')
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.xlim(-400, 400)
    plt.ylim(-400, 400)
    plt.grid(True)

    # Exibe o gráfico
    plt.show()

def signal_handler(sig, frame):
    print('Plotting Lidar data...')
    
    # Lê os dados do arquivo
    with open(output_path, 'r') as arquivo:
        lidar_data = arquivo.read()
    
    # Transforma os dados do lidar em uma lista de tuplas (x, y) excluindo as linhas onde a distância é zero
    lidar_readings = filter_non_zero_distance(lidar_data.strip().split('\n'))

    # Plota os dados do Lidar
    plot_lidar_data(lidar_readings)
    
    sys.exit(0)

def run(path):
    '''Função principal'''
    lidar = RPLidar(PORT_NAME)
    
    try:
        signal.signal(signal.SIGINT, signal_handler)  # Associa o sinal de interrupção a signal_handler
        print('Recording measurements... Press Crl+C to stop.')
        start_time = time.time()  # Armazena o tempo de início
        
        for measurement in lidar.iter_measures():
            angle = measurement[3]
            
            # Verifica se a segunda coluna é diferente de 0 e o ângulo está na faixa desejada
            if measurement[3] != 0:
                 #Ajuste para gravar somente as duas últimas colunas
                line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t" + '\t'.join(str(v) for v in measurement[-2:])
                
                 #Adiciona uma linha ao arquivo
                with open(path, 'a') as outfile:
                    outfile.write(line + '\n')
                
    except KeyboardInterrupt:
        print('Stopping.')
    
    lidar.stop()
    lidar.disconnect()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: ./lidar_mapping.py <output_file.txt>")
        sys.exit(1)

    output_path = sys.argv[1]
    run(output_path)
