# -*- coding: utf-8 -*-
#! /usr/bin/python3.6

# TP1 de Redes

import base64
import math
import socket
import sys

# CONSTANTES DO PROGRAMA
# ======================
TAMANHO_QUADRO = 512
TAMANHO_JANELA = 2
BYTE_ESCAPE    = bytearray([27])  # 1b
BYTE_INICIO    = bytearray([204]) # cc
BYTE_FINAL     = bytearray([205]) # cd
BYTE_CONFIRMA  = bytearray([128]) # 80
BYTE_RECEBE    = bytearray([127]) # 7f

# VARIÁVEIS DO PROGRAMA
# =====================
parametros = {'ip' : '', 'modoservidor': False, 'porta': 0, 'cliente': '', 'entrada': '', 'saida': ''}
lista_quadros = []

# FUNCOES DO PROGRAMA
# ===================

# Lê os argumentos do programa
# arg1 = -s ou -c
# arg2 = porta ou ip:porta
# arg3 = arquivo de entrada
# arg4 = arquivo de saída
def args_processar(parametros):
  parametros['modoservidor'] = True if sys.argv[1] == '-s' else False
  if parametros['modoservidor']:
    parametros['porta'] = int(sys.argv[2])
  else:
    temp = sys.argv[2].split(':')
    parametros['ip'] = temp[0]
    parametros['porta'] = int(temp[1])
  parametros['entrada'] = sys.argv[3]
  parametros['saida'] = sys.argv[4]

# Checa a integridade dos dadosGera os bytes para checksum de 16 bits
def chcksum_checar(valor):
  soma = 0
  for x in valor:
    soma = soma + x
  for x in range(0, 1):
    vaium = math.floor(soma / 0x100)
    soma = soma % 0x100 + vaium
    
  return (soma == 0xFF)

# Gera os bytes para checksum de 16 bits
def chcksum_gerar(valor):
  soma = 0
  for x in valor:
    soma = soma + x
  for x in range(0, 1):
    vaium = math.floor(soma / 0x10000)
    soma = soma % 0x10000 + vaium
  complemento = ~soma & 0xFFFF
  byte1 = math.floor(complemento / 0x100)
  byte2 = complemento % 0x100
  
  return (bytearray([byte1, byte2]))

# Efetua uma conexão ativa para IP informado
def conexaoativa_conectar(conexao, param):
  conexao.connect((param['ip'], param['porta']))

def conexaoativa_manipular(tcp):
  tcp.send(bytearray([0,1,2,3,4]))
  try:
    while True:
      r = tcp.recv(1)
      if not r:
        break
      if len(r) == 0:
        break
      print(r)
  except:
    exit()

# Espera passivamente por uma conexão
def conexaopassiva_conectar(tcp, param):
  # Espera por um pedido de conexão externo
  tcp.bind(('', param['porta']))
  tcp.listen(1)
  
  # Aceita uma conexao externa
  return tcp.accept()

# Recebe, processa e envia dados pela conexao  
def conexaopassiva_manipular(conexao):
  try:
    while True:
      r = conexao.recv(1)
      s = bytearray(1)
      s[0] = r[0] + 1
      conexao.send(s)
  except:
    exit()

# Abre um arquivo para leitura e o
# carrega na memória
def dados_obter(nomearquivo):
  arquivo = open(nomearquivo, "rb")
  dados = bytearray(arquivo.read())

  return dados

# Particionar dados em pedaços
def dados_partir(dados, tamanho):
  return [dados[i:i+tamanho] for i in range(0, len(dados), tamanho)]

# Adiciona DLE antes dos bytes de escape e de flags
def dados_rechear(dados, bytesflag, byteescape):
  x = dados.replace(byteescape, byteescape * 2)
  for byteflag in bytesflag:
    y = x.replace(byteflag, byteescape + byteflag)
  
  return y

# Codifica um quadro e base16
def quadro_codificar(quadro):
  return base64.b16encode(quadro)
  
# Gera um quadro conforme especificação do TP
def quadro_gerar(dados, quadroid):
  espacovazio = bytearray([0,0])

  quadro = BYTE_INICIO       # sentinela Inicio do Quadro
  quadro.extend(quadroid)    # ID do quadro
  quadro.extend(BYTE_RECEBE) # Flag de recepcao
  quadro.extend(espacovazio) # Espaço reservado para o checksum
  quadro.extend(dados)       # Dados do quadro
  quadro.extend(BYTE_FINAL)  # sentinela Fim do Quadro
  
  # calcula o checksum
  checksum = chcksum_gerar(quadro)
  quadro[3] = checksum[0]
  quadro[4] = checksum[1]
  
  return quadro

# Gera os IDs disponíveis para identificar
# os quadros da fila
def filaquadros_gerarids(quantidade):
  lista = []
  for i in range(0, quantidade):
    lista.append(bytearray([i]))
    
  return lista
    
# Gera a fila de quadros para transmitir
def filaquadros_gerar(lista):
  i = 0
  ids = filaquadros_gerarids(TAMANHO_JANELA)
  quadros = []
  for item in lista:
    quadros.append(quadro_gerar(item, ids[i % TAMANHO_JANELA]))
    i = i + 1
  return quadros

# Configura uma conexão via TCP/IP
def tcp_obter():
  # Cria um soquete para comunicação externa
  tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  # Para evitar a exceção "address already in use",
  # desligar esse comportamento com uma opção da API de soquetes:
  tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
  return tcp
  
# Desliga e fecha uma conexão TCP/IP
def tcp_encerrar(tcp):
  tcp.shutdown(socket.SHUT_RDWR)
  tcp.close()

# CORPO DO PROGRAMA
# =================  
if len(sys.argv) > 4:  
  args_processar(parametros)
  dados = dados_obter(parametros['entrada'])
  dadosrecheados = dados_rechear(dados, [BYTE_FINAL], BYTE_ESCAPE)
  pedacos = dados_partir(dadosrecheados, TAMANHO_QUADRO)
  fila = filaquadros_gerar(pedacos)
  tcp = tcp_obter()
  
  if parametros['modoservidor']:
    conexao, parametros['cliente'] = conexaopassiva_conectar(tcp, parametros)
    conexaopassiva_manipular(conexao)
  else:
    conexaoativa_conectar(tcp, parametros)
    conexaoativa_manipular(tcp)
  tcp_encerrar(tcp)
