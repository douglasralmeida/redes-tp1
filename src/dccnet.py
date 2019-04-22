# TP1 de Redes

import sys

# Variaveis do programa
# =====================
conexao = {'ip' : '', 'modoservidor': False, 'porta': 0, 'entrada': '', 'saida': ''}

# Funcoes do programa
# ===================

# Lê os argumentos do programa
# arg1 = -s ou -c
# arg2 = porta ou ip:porta
# arg3 = arquivo de entrada
# arg4 = arquivo de saída
def processar_args(conexao):
  if len(sys.argv) > 4:
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
  else:
    exit
    
# Corpo do programa
# =================
  
processar_args(conexao)

print(conexao['modoservidor'])
print(conexao['ip'])
print(conexao['porta'])
print(conexao['entrada'])
print(conexao['saida'])
