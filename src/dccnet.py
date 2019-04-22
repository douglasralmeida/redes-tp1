# TP1 de Redes

import sys

# Constantes do programa
# ======================
TAMANHO_QUADRO = 512

# Variaveis do programa
# =====================
conexao = {'ip' : '', 'modoservidor': False, 'porta': 0, 'entrada': '', 'saida': ''}

# Funcoes do programa
# ===================

# Abre um arquivo para leitura e o
# quebra em pedaços
def ler_arquivo(nomearquivo, tamanhopedaco):
  arquivo = open(nomearquivo)
  while True:
    dados = arquivo.read(tamanhopedaco)
    if not dados:
      break
    yield dados

# Lê os argumentos do programa
# arg1 = -s ou -c
# arg2 = porta ou ip:porta
# arg3 = arquivo de entrada
# arg4 = arquivo de saída
def processar_args(conexao):
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
    
# Corpo do programa
# =================  
if len(sys.argv) < 5:
  exit

processar_args(conexao)

for pedaco in ler_arquivo(conexao['entrada'], int(TAMANHO_QUADRO / 2)):
  print(pedaco)
