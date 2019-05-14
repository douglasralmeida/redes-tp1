# -*- coding: utf-8 -*-
#! /usr/bin/python3.6

# TP1 de Redes

import base64
import math
import socket
import sys

# CONSTANTES DO PROGRAMA
# ======================
TAMANHO_SECAODADOS = 512
TAMANHO_JANELA     = 2
BYTE_ESCAPE        = bytearray([27])  # 1b
BYTE_INICIO        = bytearray([204]) # cc
BYTE_FINAL         = bytearray([205]) # cd
BYTE_CONFIRMA      = bytearray([128]) # 80
BYTE_DADOS         = bytearray([127]) # 7f
BYTES_FLAGS        = [BYTE_FINAL]
EXIBIR_LOG         = True

# VARIÁVEIS DO PROGRAMA
# =====================
parametros = {'ip' : '', 'modoservidor': False, 'porta': 0, 'cliente': '', 'entrada': '', 'saida': ''}

# FUNCOES DO PROGRAMA
# ===================

def log(msg):
  if EXIBIR_LOG:
    print(msg) 

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

# Codifica uma sequencia de bytes em base16
def base16_codificar(bytes):
  return base64.b16encode(bytes)

# Decodifica uma sequencia de bytes na base16
def base16_decodificar(bytes):
  return base64.b16decode(bytes, True)

def byte_einicio(bytescodificados):
  ba = bytearray()
  ba.extend(base16_decodificar(bytescodificados))
    
  return (ba == BYTE_INICIO)

# QQ + CD                     s
# QQ + 1B + CD                n
# QQ + 1B + 1B + CD           s
# QQ + 1B + 1B + 1B + CD      n
# QQ + 1B + 1B + 1B + 1B + CD s
def byte_efinal(bytescodificados):
  resultado = True
  ba = bytearray()
  ba.extend(base16_decodificar(bytescodificados))
  
  ehfinal = (ba[-1] == BYTE_FINAL[0])
  if not ehfinal:
    return False
  
  x = -2
  while (ba[x] == BYTE_ESCAPE[0]):
    resultado = not resultado
    x = x - 1
   
  return resultado

# Checa a integridade dos dados
# Gera os bytes para checksum de 16 bits
def chcksum_checar(valor):
  soma = 0
  for x in valor:
    soma = soma + x
    if math.floor(soma / 0x100) > 0:
      soma = soma % 0x100 + 1

  return (soma == 0xFF)

# Gera os bytes para checksum de 16 bits
def chcksum_gerar(valor):
  soma = 0
  for x in valor:
    soma = soma + x
    if math.floor(soma / 0x10000) > 0:
      soma = soma % 0x10000 + 1
  complemento = ~soma & 0xFFFF
  byte1 = math.floor(complemento / 0x100)
  byte2 = complemento % 0x100
  
  return (bytearray([byte1, byte2]))

# Abre um arquivo para leitura e o
# carrega na memória
def dados_obter(nomearquivo):
  arquivo = open(nomearquivo, "rb")
  dados = bytearray(arquivo.read())

  return dados
  
def dados_salvar(dados, arquivo):
  arquivo.write(dados)

# Particionar dados em pedaços
def dados_partir(dados, tamanho):
  return [dados[i:i+tamanho] for i in range(0, len(dados), tamanho)]

def dados_desrechear(dados, bytesflag, byteescape):
  x = dados.replace(byteescape * 2, byteescape)
  for byteflag in bytesflag:
    y = x.replace(byteescape + byteflag, byteflag)
  
  return y

def dados_processar(dados, parametros):
  # Remove o recheio
  dados = dados_desrechear(dados, BYTES_FLAGS, BYTE_ESCAPE)
  
  # Salva os dados no arquivo de saida
  dados_salvar(dados, parametros['saida'])

# Adiciona DLE antes dos bytes de escape e de flags
def dados_rechear(dados, bytesflag, byteescape):
  x = dados.replace(byteescape, byteescape * 2)
  for byteflag in bytesflag:
    y = x.replace(byteflag, byteescape + byteflag)
  
  return y

# Checa a integridade do quado
def quadro_checar(quadro):
  return chcksum_checar(quadro)

# Codifica um quadro e base16
def quadro_codificar(quadro):
  return base16_codificar(quadro)

def quadro_eresposta(quadro):
  return (bytearray([quadro[2]]) == BYTE_CONFIRMA)
 
# Gera um quadro conforme especificação do TP
def quadro_gerar(dados, quadroid, resposta):
  espacovazio = bytearray([0,0])
  quadro = bytearray()

  quadro.extend(BYTE_INICIO)     # sentinela Inicio do Quadro
  quadro.extend(quadroid)        # ID do quadro
  if resposta: 
    quadro.extend(BYTE_CONFIRMA) # Flag de recepcao
  else:
    quadro.extend(BYTE_DADOS)    # Flag de confirmação
  quadro.extend(espacovazio)     # Espaço reservado para o checksum
  if not resposta:
    quadro.extend(dados)         # Dados do quadro
  quadro.extend(BYTE_FINAL)      # sentinela Fim do Quadro
  
  # calcula o checksum
  checksum = chcksum_gerar(quadro)
  quadro[3] = checksum[0]
  quadro[4] = checksum[1]
  
  return quadro

def quadro_obterchecksum(quadro):
  return bytearray([quadro[3], quadro[4]])

def quadro_obterdados(quadro, tamanho):
  return (quadro[5:tamanho-1])

def quadro_obterid(quadro):
  return int(quadro[1])

# Gera um quadro de confirmação
def quadro_resposta(quadroid):
  return quadro_gerar(None, quadroid, True)

def conexao_enviar(tcp, quadro):
  dados = base16_codificar(quadro)
  try:
    tcp.sendall(dados)
  except:
    sys.exit()

def receber(conexao, quantidade):
  bytes = b''
  try:
    conexao.settimeout(1.0)
    bytes = bytes + conexao.recv(quantidade)
  except socket.timeout:
    # demorou mais de um segundo
    conexao.settimeout(None)
    return None
  except:
    sys.exit()
  conexao.settimeout(None)
    
  return bytes

def conexao_receber(conexao):
  while True:
    # recebe dois bytes
    dados = bytearray()
    tamanho = 1
    bytes_recebidos = receber(conexao, 2)

    # demorou mais de um segundo
    if not bytes_recebidos:
      return 1, None

    # se não recebeu nada então a conexão
    # do outro enlace foi desligada
    # não retorna nada
    if len(bytes_recebidos) == 0:  
      return 0, None
    dados.extend(bytes_recebidos)
  
    # checa pelo sentinela InicioDoQuadro
    # se é o inicio do quadro, então o recebe
    if byte_einicio(dados):
      # recebe o cabecalho
      bytes_recebidos = receber(conexao, 8)
      tamanho = tamanho + 4
      # demorou mais de um segundo
      if not bytes_recebidos:
        return 1, None
      
      # se não recebeu nada então a conexão
      # do outro enlace foi desligada
      # não retorna nada
      if len(bytes_recebidos) == 0:
        return 0, None
      dados.extend(bytes_recebidos)

      # recebe o restantes até FimDoQuadro
      while True:
        bytes_recebidos = receber(conexao, 2)
        
        # demorou mais de um segundo
        if not bytes_recebidos:
          return 1, None
      
        # se não recebeu nada então a conexão
        # do outro enlace foi desligada
        # não retorna nada
        if len(bytes_recebidos) == 0:
          return 0, None
        
        dados.extend(bytes_recebidos)
        tamanho = tamanho + 1

        # quando chegar o final, retorna o quadro
        if byte_efinal(dados):
          return tamanho, base16_decodificar(dados)
      # se não é o início de um quadro, então
      # continua esperando pelo sentinela

def conexao_confirmar(conexao, id):
  confirmacao = quadro_resposta(id)
  conexao_enviar(conexao, confirmacao)

def conexao_enviarquadro(conexao, quadro, info):
  temp = quadro_obterchecksum(quadro)
  x = quadro_obterid(quadro)
  log('Enviando quadro ID {0} Checksum ({1} {2})...'.format(x, temp[0], temp[1]))
  conexao_enviar(conexao, quadro)
  log('Enviado.')
  info['envia_id'] = quadro_obterid(quadro)
  info['aguarda_resposta'] = True

def conexao_obterquadro(conexao, info):
  while True:
    # recebe um quadro
    log('Aguardando quadro...')
    tamanho, quadro = conexao_receber(conexao)

    # se não recebeu nada então a conexão
    # foi desligada pelo outro enlace
    # hora de dar tchau
    if quadro is None and tamanho == 0:
      log('Soquete vazio. Desligando...')
      info['sair'] = True
      return None

    # Deu timeout
    if quadro is None and tamanho == 1:
      log('Timeout.')
      info['timeout'] = True 
      return None
    
    # checksum
    # se estiver errado entao ignora
    temp = quadro_obterchecksum(quadro)
    log('Quadro recebido. ID: {0} Checksum ({1} {2}).'.format(quadro_obterid(quadro), temp[0], temp[1]))
    if not quadro_checar(quadro):
      log('Chcksum ({0} {1}) inválido. Quadro ignorado.'.format(temp[0], temp[1]))
      log(quadro)
      return None

    # checa resposta
    # se for um quadro de resposta (ACK)
    # o retorna diretamente
    if quadro_eresposta(quadro):
      log('É um quadro de resposta.')
      return quadro

    # não é resposta...entao continua
    checksum = quadro_obterchecksum(quadro)
    log('É um quadro de dados.')

    # checa id
    # se for o mesmo quadro recebido
    # anteriormente então ignora quadro
    # mas reenvia a confirmação
    id = quadro_obterid(quadro)
    if info['rec_id'] == id:
      # Se os checksums forem iguais entao
      # é o mesmo quadro ja recebido anterioremente
      # assim reenvia a confirmacao e espera
      # o proximo
      mesmoquadro = (checksum == info['rec_checksum'])
      if mesmoquadro:
        log('Quadro repetido. Ignorando e reenviando ACK...')
        conexao_confirmar(conexao, bytearray([id]))
      continue

    # quadro foi aceito então avisa o
    # no enviando uma confirmacao
    log('É um quadro de dados. Enviando confirmação')
    conexao_confirmar(conexao, bytearray([id]))
      
    # quadro novo no pedaço...retorna-o
    info['rec_checksum'] = checksum
    info['rec_tamanho'] = tamanho
    info['rec_id'] = id

    return quadro

# Efetua uma conexão ativa para IP informado
def conexaoativa_conectar(conexao, param):
  conexao.connect((param['ip'], param['porta']))

# Espera passivamente por uma conexão
def conexaopassiva_conectar(tcp, param):
  # Espera por um pedido de conexão externo
  tcp.bind(('', param['porta']))
  tcp.listen(1)
  
  # Aceita uma conexao externa
  return tcp.accept()

# Recebe, processa e envia dados pela conexao  
def conexao_manipular(conexao, fila, parametros):
  info = {'aguarda_resposta': False, 'envia_id': 0, 'rec_id' : 1, 'rec_tamanho': 0, 'rec_checksum': bytearray(), 'timeout': False, 'sair': False}
  
  while True:
    # se nao estiver esperando resposta
    # enquanto tiver quadros na
    # fila para enviar...envia
    log('SEÇÃO DE ENVIO') 
    log('Tamanho da fila: {0}'.format(len(fila)))
    log('Aguarda resposta: {0}'.format(info['aguarda_resposta']))
    if not info['aguarda_resposta'] and len(fila) > 0:
      quadro_aenviar = fila.pop(0)
      conexao_enviarquadro(conexao, quadro_aenviar, info)

    # Recebe um quadro
    while True:
      log('SEÇÃO DE RECEBIMENTO')
      quadro_recebido = conexao_obterquadro(conexao, info)
    
      # Não recebeu nada então
      # conexão foi desligada e
      # pode sair do programa
      if info['sair']:
        exit()
       
      # Deu timeout então
      # reenvia e espera o proximo
      if info['timeout'] and info['aguarda_resposta']:
        log('Último quadro será reenviado.')
        log(quadro_aenviar)
        conexao_enviarquadro(conexao, quadro_aenviar, info)
        continue
      
      # Quadro foi ignorado então
      # envia o proximo da fila
      if quadro_recebido == None:
        log('Próximo da fila.')
        break
    
      # Checa se o quadro recebido é a resposta
      # esperada. 
      # se sim pode enviar o proximo da fila
      # se não reenvia o quadro e espera o proximo
      if quadro_eresposta(quadro_recebido):
        # Se não estava esperando por resposta
        # envia o proximo da fila
        if not info['aguarda_resposta']:
          log('Resposta não era esperada. Próximo da fila.')
          break
        
        # Se estava esperando por resposta
        id = quadro_obterid(quadro_recebido)
        if id == info['envia_id']:
          # Resposta confirmada entao
          # envia o proximo da fila
          
          log('Resposta confirmada. Próximo da fila.')
          info['aguarda_resposta'] = False
          info['timeout'] = False
          break
        else:
          # Nao era a resposta esperada
          # entao reenvia o ultimo quadro
          # e espera o proximo quadro
          log('Resposta não confirmada. Reenviando...')
          log(quadro_aenviar)
          conexao_enviarquadro(conexao, quadro_aenviar, info)
          continue
        
      # Se é quadro de dados então
      # extrai os dados do quadro
      dados_recebidos = quadro_obterdados(quadro_recebido, info['rec_tamanho'])

      # processa os dados recebidos
      dados_processar(dados_recebidos, parametros)
      
      # envia o proximo da fila
      log('Dados salvos. Próximo da fila.')
      break

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
    quadros.append(quadro_gerar(item, ids[i % TAMANHO_JANELA], False))
    i = i + 1
  return quadros
  
def filaquadros_proximo(fila):
  quadro = fila.pop()
  
  return base16.codificar(quadro)

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
  saida = open(parametros['saida'], 'w+b')
  parametros['saida'] = saida
  pedacos = dados_partir(dados, TAMANHO_SECAODADOS)
  for pedaco in pedacos:
    pedaco_recheado = dados_rechear(pedaco, BYTES_FLAGS, BYTE_ESCAPE)
    pedaco.clear()
    pedaco.extend(pedaco_recheado)
  fila = filaquadros_gerar(pedacos)
  tcp = tcp_obter()
  if parametros['modoservidor']:
    log('Aguardando conexão passivamente...')
    conexao, parametros['cliente'] = conexaopassiva_conectar(tcp, parametros)
    log('Conectado..')
  else:
    log('Conectando...')
    conexaoativa_conectar(tcp, parametros)
    conexao = tcp
    log('Conectado.')
  conexao_manipular(conexao, fila, parametros)
  saida.close()
  tcp_encerrar(tcp)
