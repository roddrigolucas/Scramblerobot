import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Ajuste a porta serial conforme necessário

def send_command(command):
    ser.write(command.encode())

while True:
    user_input = input("Digite F para frente, B para trás, L para esquerda, R para direita, S para parar: ")
    send_command(user_input)
    time.sleep(0.1)  # Aguarda um curto período para evitar leituras incorretas
