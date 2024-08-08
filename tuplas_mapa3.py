import math
import matplotlib.pyplot as plt

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

caminho_arquivo= '/home/rodrigo/projetoiceis/tuplas.txt'

with open(caminho_arquivo, 'r') as arquivo:
    lidar_data = arquivo.read()

# Transforma os dados do lidar em uma lista de tuplas (x, y) excluindo as linhas onde a distância é zero
lidar_readings = filter_non_zero_distance(lidar_data.strip().split('\n'))

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

# Exemplo de uso
lidar_data_exemplo = lidar_readings
plot_lidar_data(lidar_data_exemplo)
