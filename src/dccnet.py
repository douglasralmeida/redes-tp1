# TP1 de Redes

import base64
import sys

# Constantes do programa
# ======================
TAMANHO_QUADRO = 512
BYTE_ESCAPE    = b'1b'
BYTE_INICIO    = b'cc'
BYTE_FINAL     = b'cd'
BYTE_CONFIRMA  = b'80'
BYTE_RECEBE    = b'7f'

# Variaveis do programa
# =====================
conexao = {'ip' : '', 'modoservidor': False, 'porta': 0, 'entrada': '', 'saida': ''}
lista_quadros = []

# Funcoes do programa
# ===================

# Gera o byte checksum
def gerar_chcksum(valor):
  lista = partir_dados(valor, 2)
  b = bytearray(str)
  soma = b'0'
  print(lista)
  for item in lista:
    soma += item
  print(soma)
  return (soma & 0xFF)

# Lê os argumentos do programa
# arg1 = -s ou -c
# arg2 = porta ou ip:porta
# arg3 = arquivo de entrada
# arg4 = arquivo de saída
def args_processar(conexao):
  conexao['modoservidor'] = True if sys.argv[1] == '-s' else False
  if conexao['modoservidor']:
    conexao['porta'] = int(sys.argv[2])
  else:
    temp = sys.argv[2]
    temp = temp.split(':')
    conexao['ip'] = temp[0]
    conexao['porta'] = int(temp[1])
  conexao['entrada'] = sys.argv[3]
  conexao['saida'] = sys.argv[4]

# Abre um arquivo para leitura e o
# carrega na memória
def dados_obter(nomearquivo):
  arquivo = open(nomearquivo, "rb")
  dados = arquivo.read() 

  return dados

# Partir dados em pedaços
def dados_partir(dados, tamanho):
  return [dados[i:i+tamanho] for i in range(0, len(dados), tamanho)]

# Adiciona DLE antes dos bytes de escape e de flags
def dados_rechear(dados, bytesflag, byteescape):
  x = dados.replace(byteescape, byteescape * 2)
  for byteflag in bytesflag:
    y = x.replace(byteflag, byteescape + byteflag)
  
  return y

# Codifica um quadro e base16
def quadro_codificar(quadro)
  return base64.b16encode(quadro)
  
# Gera um quadro conforme especificação do TP
def quadro_gerar(dados, quadroid):
  quadro = BYTE_INICIO    # sentinela Inicio do Quadro
  quadro += quadroid      # ID do quadro
  quadro += BYTE_RECEBE   # Flag de recepcao
  quadro += b'00'         # Espaço reservado para o chcksum
  quadro += dados         # Dados do quadro
  quadro += BYTE_FINAL    # sentinela Fim do Quadro
  
  return quadro
  
# Gera a fila de quadros para transmitir
def filaquadros_gerar(lista):
  ids = [b'0', b'1']
  i = 0
  quadros = list()
  for item in lista:
    quadros.append(quadro_gerar(item, ids[i % 2]))
    i = i+1
  return quadros

# Corpo do programa
# =================  
if len(sys.argv) < 5:
  exit

args_processar(conexao)
dados = dados_obter(conexao['entrada'])
dadosrecheados = dados_rechear(dados, [BYTE_FINAL], BYTE_ESCAPE)
pedacos = dados_partir(dadosrecheados, TAMANHO_QUADRO)
fila = filaquadros_gerar(pedacos)

print(fila)
