# from datetime import datetime

# # Dele contet of debug.log file
# file = open("debug.log", "w")
# file.write("")
# file.close()

# def debuger(string):
#     # Obter data e hora atuais no formato desejado
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
#     # Abrir o arquivo de log e gravar a linha com timestamp
#     with open("debug.log", "a") as file:
#         file.write(f"[{timestamp}] {string}\n")

def slip_encode(datagram):
    SLIP_END = 0xC0
    SLIP_ESC = 0xDB
    SLIP_ESC_END = 0xDC
    SLIP_ESC_ESC = 0xDD

    frame = [SLIP_END]  # start SLIP frame with SLIP_END

    for byte in datagram:
        if byte == SLIP_END:
            frame.extend([SLIP_ESC, SLIP_ESC_END])
        elif byte == SLIP_ESC:
            frame.extend([SLIP_ESC, SLIP_ESC_ESC])
        else:
            frame.append(byte)

    frame.append(SLIP_END)  # End framwe

    return bytearray(frame)
class CamadaEnlace:
    ignore_checksum = False

    def __init__(self, linhas_seriais):
        """
        Inicia uma camada de enlace com um ou mais enlaces, cada um conectado
        a uma linha serial distinta. O argumento linhas_seriais é um dicionário
        no formato {ip_outra_ponta: linha_serial}. O ip_outra_ponta é o IP do
        host ou roteador que se encontra na outra ponta do enlace, escrito como
        uma string no formato 'x.y.z.w'. A linha_serial é um objeto da classe
        PTY (vide camadafisica.py) ou de outra classe que implemente os métodos
        registrar_recebedor e enviar.
        """
        self.enlaces = {}
        self.callback = None
        # Constrói um Enlace para cada linha serial
        for ip_outra_ponta, linha_serial in linhas_seriais.items():
            enlace = Enlace(linha_serial)
            self.enlaces[ip_outra_ponta] = enlace
            enlace.registrar_recebedor(self._callback)

    def registrar_recebedor(self, callback):
        """
        Registra uma função para ser chamada quando dados vierem da camada de enlace
        """
        self.callback = callback

    def enviar(self, datagrama, next_hop):
        """
        Envia datagrama para next_hop, onde next_hop é um endereço IPv4
        fornecido como string (no formato x.y.z.w). A camada de enlace se
        responsabilizará por encontrar em qual enlace se encontra o next_hop.
        """
        # Encontra o Enlace capaz de alcançar next_hop e envia por ele
        self.enlaces[next_hop].enviar(datagrama)

    def _callback(self, datagrama):
        if self.callback:
            self.callback(datagrama)


class Enlace:
    def __init__(self, linha_serial):
        self.linha_serial = linha_serial
        self.linha_serial.registrar_recebedor(self.__raw_recv)

    def registrar_recebedor(self, callback):
        self.callback = callback

    def enviar(self, datagrama):
        """
        Envia o datagrama pela linha serial utilizando o protocolo SLIP.
        Insere um byte 0xC0 no início e no fim do datagrama.
        """

        #xodifica o datagrama com SLIP
        datagrama2 = slip_encode(datagrama)
        # # Byte especial de delimitação de quadro no SLIP
        # SLIP_END = 0xC0
        
        # # Delimita o início e o fim do quadro com 0xC0
        # quadro = bytearray([SLIP_END]) + datagrama2 + bytearray([SLIP_END])
        
        # Envia o quadro pela linha serial
        self.linha_serial.enviar((datagrama2))
        #print(quadro)
        debuger(str(datagrama2))

    def __raw_recv(self, dados):
        # TODO: Preencha aqui com o código para receber dados da linha serial.
        # Trate corretamente as sequências de escape. Quando ler um quadro
        # completo, repasse o datagrama contido nesse quadro para a camada
        # superior chamando self.callback. Cuidado pois o argumento dados pode
        # vir quebrado de várias formas diferentes - por exemplo, podem vir
        # apenas pedaços de um quadro, ou um pedaço de quadro seguido de um
        # pedaço de outro, ou vários quadros de uma vez só.
        pass
