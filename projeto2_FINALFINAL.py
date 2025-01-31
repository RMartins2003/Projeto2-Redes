import networkx as nx
import random
import matplotlib.pyplot as plt
import socket
import struct

###############################################
# CLASSE IPDatagram – DATAGRAMA IPv4 COMPLETO
###############################################
class IPDatagram:
    def __init__(self, src_ip, dest_ip, payload, protocol='TCP', type_of_service=0, ttl=64, flags='DF', options=b''):
        """
        Inicializa um datagrama IPv4 com todos os campos do cabeçalho.

        Campos do cabeçalho IPv4:
          - Version (4 bits): Número da versão (IPv4 = 4).
          - Header Length (4 bits): Número de palavras de 32 bits (mínimo 5 → 20 bytes).
          - Type of Service (8 bits): Dividido em DiffServ (6 bits) e ECN (2 bits).
          - Total Length (16 bits): Tamanho total do datagrama (cabeçalho + payload).
          - Identification (16 bits): Identificação do datagrama para fragmentação.
          - Flags (3 bits): Controle de fragmentação (Reserved, DF, MF).
          - Fragment Offset (13 bits): Deslocamento do fragmento.
          - Time To Live (8 bits): Número de saltos restantes.
          - Protocol (8 bits): Protocolo da camada superior (ex.: TCP, UDP, ICMP).
          - Header Checksum (16 bits): Soma de verificação do cabeçalho.
          - Source IP Address (32 bits)
          - Destination IP Address (32 bits)
          - IP Options (se houver – deve ser múltiplo de 4 bytes)
          - Data Portion: Payload da camada superior.

        Parâmetros:
         - src_ip (str): Endereço IP de origem (ex.: "192.168.1.4").
         - dest_ip (str): Endereço IP de destino (ex.: "192.168.1.5").
         - payload (str): Dados a serem transportados.
         - protocol (str/int): "TCP", "UDP", "ICMP" ou número.
         - type_of_service (int): Valor entre 0 e 255.
         - ttl (int): Valor entre 1 e 255.
         - flags (str): "DF", "MF" ou "Reserved" (caso contrário, assume 000).
         - options (bytes): Opcional; se fornecido, será ajustado para múltiplos de 4 bytes.
        """
        self.version = 4
        self.ihl = 5  # mínimo: 5 palavras de 32 bits (20 bytes)
        self.tos = type_of_service  # 8 bits (DiffServ: 6 bits; ECN: 2 bits)
        self.payload = payload.encode() if isinstance(payload, str) else payload

        # Processamento das opções (se houver)
        self.options = options if options else b''
        if self.options:
            if len(self.options) % 4 != 0:
                padding = 4 - (len(self.options) % 4)
                self.options += b'\x00' * padding
            self.ihl += len(self.options) // 4  # cada palavra extra adiciona 4 bytes
        self.total_length = self.ihl * 4 + len(self.payload)
        self.identification = random.randint(0, 0xFFFF)
        self.flags = self.parse_flags(flags)
        self.fragment_offset = 0
        self.ttl = ttl
        self.protocol = self.parse_protocol(protocol)
        self.checksum = 0  # será calculado posteriormente
        self.src_ip = src_ip
        self.dest_ip = dest_ip

    def parse_flags(self, flags_str):
        """
        Converte uma string de flags em um inteiro de 3 bits.
        Mapeamento:
          - "DF"  → Don't Fragment → 010 (valor 2)
          - "MF"  → More Fragments   → 001 (valor 1)
          - "Reserved" (ou outro valor) → 000 (valor 0)
        """
        flag_map = {'DF': 2, 'MF': 1, 'RESERVED': 0}
        return flag_map.get(flags_str.upper(), 0)

    def parse_protocol(self, proto):
        """
        Converte o protocolo para seu número correspondente.
        Aceita: "TCP", "UDP", "ICMP" ou um número.
        Retorna 6 (TCP) por padrão.
        """
        protocol_map = {'TCP': 6, 'UDP': 17, 'ICMP': 1}
        if isinstance(proto, str):
            p = proto.strip().upper()
            if p in protocol_map:
                return protocol_map[p]
            for name, num in protocol_map.items():
                if p.startswith(name):
                    return num
            try:
                p_int = int(p)
                return p_int if p_int in protocol_map.values() else 6
            except ValueError:
                return 6
        elif isinstance(proto, int):
            return proto if proto in protocol_map.values() else 6
        else:
            return 6

    def compute_checksum(self):
        """
        Calcula o checksum do cabeçalho.
        O campo checksum é calculado sobre o cabeçalho (com o campo checksum zerado),
        somando os valores de 16 bits, somando o carry e aplicando o complemento de 1.
        """
        header_without_checksum = struct.pack("!BBHHHBBH4s4s",
            (self.version << 4) + self.ihl,
            self.tos,
            self.total_length,
            self.identification,
            (self.flags << 13) + self.fragment_offset,
            self.ttl,
            self.protocol,
            0,  # checksum zerado para o cálculo
            socket.inet_aton(self.src_ip),
            socket.inet_aton(self.dest_ip)
        )
        if self.options:
            header_without_checksum += self.options
        checksum = 0
        for i in range(0, len(header_without_checksum), 2):
            word = (header_without_checksum[i] << 8) + header_without_checksum[i+1]
            checksum += word
        # Adiciona os carries
        while checksum >> 16:
            checksum = (checksum & 0xFFFF) + (checksum >> 16)
        checksum = ~checksum & 0xFFFF
        return checksum

    def generate(self):
        """
        Gera o datagrama completo (cabeçalho + payload) em bytes.
        """
        self.checksum = self.compute_checksum()
        header = struct.pack("!BBHHHBBH4s4s",
            (self.version << 4) + self.ihl,
            self.tos,
            self.total_length,
            self.identification,
            (self.flags << 13) + self.fragment_offset,
            self.ttl,
            self.protocol,
            self.checksum,
            socket.inet_aton(self.src_ip),
            socket.inet_aton(self.dest_ip)
        )
        if self.options:
            header += self.options
        return header + self.payload

    def display_detailed(self):
        """
        Exibe detalhadamente todos os campos do datagrama.
        """
        diffserv = (self.tos >> 2) & 0x3F
        ecn = self.tos & 0x03
        print("==== Detailed IP Datagram ====")
        print(f"Version (4 bits): {self.version}")
        print(f"Header Length (4 bits): {self.ihl} words = {self.ihl*4} bytes")
        print(f"Type of Service (8 bits): {self.tos}")
        print(f"   DiffServ (6 bits): {diffserv}")
        print(f"   ECN (2 bits): {ecn}")
        print(f"Total Length (16 bits): {self.total_length} bytes")
        print(f"Identification (16 bits): {self.identification}")
        print(f"Flags (3 bits): {format(self.flags, '03b')} (Reserved: {(self.flags >> 2) & 1}, DF: {(self.flags >> 1) & 1}, MF: {self.flags & 1})")
        print(f"Fragment Offset (13 bits): {self.fragment_offset}")
        print(f"Time To Live (8 bits): {self.ttl}")
        print(f"Protocol (8 bits): {self.protocol}")
        print(f"Header Checksum (16 bits): {hex(self.checksum)}")
        print(f"Source IP Address (32 bits): {self.src_ip}")
        print(f"Destination IP Address (32 bits): {self.dest_ip}")
        if self.options:
            print(f"IP Options: {self.options.hex()} (length: {len(self.options)} bytes, padded to 32-bit boundary)")
        else:
            print("IP Options: None")
        print(f"Data Portion: {self.payload.decode()} (length: {len(self.payload)} bytes)")
        print("================================\n")


###############################################
# FUNÇÃO AUXILIAR – CONVERTE ENTRADA EM NÚMERO DE PROTOCOLO
###############################################
def protocolo_para_numero(protocolo_input):
    protocolo_map = {'TCP': 6, 'UDP': 17, 'ICMP': 1}
    if isinstance(protocolo_input, str):
        p = protocolo_input.strip().upper()
        if p in protocolo_map:
            return protocolo_map[p]
        for nome, num in protocolo_map.items():
            if p.startswith(nome):
                return num
        try:
            p_int = int(p)
            return p_int if p_int in protocolo_map.values() else None
        except ValueError:
            return None
    elif isinstance(protocolo_input, int):
        return protocolo_input if protocolo_input in protocolo_map.values() else None
    else:
        return None


###############################################
# FUNÇÃO PARA CRIAR E VISUALIZAR O DATAGRAMA IP
###############################################
def criar_e_visualizar_datagrama(enderecos_ip):
    print("\n==== Criação de Datagram IP ====")
    src_host = input("Digite o nome do host de origem (ex.: Host e1-1): ").strip()
    dest_host = input("Digite o nome do host de destino (ex.: Host e2-5): ").strip()

    if src_host not in enderecos_ip:
        print(f"Host de origem '{src_host}' não encontrado na rede.\n")
        return
    if dest_host not in enderecos_ip:
        print(f"Host de destino '{dest_host}' não encontrado na rede.\n")
        return

    src_ip = enderecos_ip[src_host]
    dest_ip = enderecos_ip[dest_host]
    payload = input("Digite a mensagem (payload) do datagrama: ").strip()
    protocolo_input = input("Digite o protocolo (TCP=6, UDP=17, ICMP=1): ").strip()

    protocolo = protocolo_para_numero(protocolo_input)
    if protocolo is None:
        print("Protocolo inválido. Usando TCP (6) por padrão.")
        protocolo = 6

    datagrama = IPDatagram(src_ip, dest_ip, payload, protocolo)
    # Gera o datagrama (isso calcula o checksum)
    _ = datagrama.generate()
    datagrama.display_detailed()
    print("Datagrama (em bytes):")
    print(datagrama.generate().hex())
    desenhar_diagrama_datagram(datagrama)


###############################################
# FUNÇÃO PARA DESENHAR O DIAGRAMA DO CABEÇALHO IP
###############################################
def desenhar_diagrama_datagram(datagrama):
    """
    Desenha um diagrama ilustrativo do cabeçalho IP (conforme o padrão IPv4),
    exibindo os principais campos em linhas.
    """
    total_width = 40  # unidades arbitrárias
    row_height = 3
    num_rows = 6 + (1 if datagrama.options else 0)

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, total_width)
    ax.set_ylim(-num_rows * row_height, row_height)
    ax.axis('off')

    # Linha 1: Version/Header Length | Type of Service | Total Length
    fields = [
        (f"Version/IHL\n{datagrama.version}/{datagrama.ihl}", 10),
        (f"TOS\n{datagrama.tos}", 10),
        (f"Total Length\n{datagrama.total_length}", 20)
    ]
    x = 0
    y = 0
    for text, w in fields:
        rect = plt.Rectangle((x, y), w, row_height, fill=False, edgecolor='black', lw=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + row_height/2, text, ha='center', va='center', fontsize=10)
        x += w

    # Linha 2: Identification
    y -= row_height
    rect = plt.Rectangle((0, y), total_width, row_height, fill=False, edgecolor='black', lw=2)
    ax.add_patch(rect)
    ax.text(total_width/2, y + row_height/2, f"ID\n{datagrama.identification}", ha='center', va='center', fontsize=10)

    # Linha 3: Flags | Fragment Offset
    y -= row_height
    fields = [
        (f"Flags\n{format(datagrama.flags, '03b')}", 10),
        (f"Frag Offset\n{datagrama.fragment_offset}", 30)
    ]
    x = 0
    for text, w in fields:
        rect = plt.Rectangle((x, y), w, row_height, fill=False, edgecolor='black', lw=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + row_height/2, text, ha='center', va='center', fontsize=10)
        x += w

    # Linha 4: TTL | Protocol | Checksum
    y -= row_height
    fields = [
        (f"TTL\n{datagrama.ttl}", 10),
        (f"Protocol\n{datagrama.protocol}", 10),
        (f"Checksum\n{hex(datagrama.checksum)}", 20)
    ]
    x = 0
    for text, w in fields:
        rect = plt.Rectangle((x, y), w, row_height, fill=False, edgecolor='black', lw=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + row_height/2, text, ha='center', va='center', fontsize=10)
        x += w

    # Linha 5: Source IP Address
    y -= row_height
    rect = plt.Rectangle((0, y), total_width, row_height, fill=False, edgecolor='black', lw=2)
    ax.add_patch(rect)
    ax.text(total_width/2, y + row_height/2, f"Source IP\n{datagrama.src_ip}", ha='center', va='center', fontsize=10)

    # Linha 6: Destination IP Address
    y -= row_height
    rect = plt.Rectangle((0, y), total_width, row_height, fill=False, edgecolor='black', lw=2)
    ax.add_patch(rect)
    ax.text(total_width/2, y + row_height/2, f"Dest IP\n{datagrama.dest_ip}", ha='center', va='center', fontsize=10)

    # Linha 7: IP Options (se houver)
    if datagrama.options:
        y -= row_height
        rect = plt.Rectangle((0, y), total_width, row_height, fill=False, edgecolor='black', lw=2)
        ax.add_patch(rect)
        try:
            options_text = datagrama.options.decode()
        except Exception:
            options_text = datagrama.options.hex()
        ax.text(total_width/2, y + row_height/2, f"Options\n{options_text}", ha='center', va='center', fontsize=10)

    plt.title("Diagrama do Cabeçalho IP", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()


###############################################
# FUNÇÃO PARA CONFIGURAR A REDE SIMULADA
###############################################
def configurar_rede():
    """
    Configura a rede simulada (roteadores, switches, subredes e hosts),
    atribui endereços IP e cria os enlaces.
    Retorna:
      G, subredes, enderecos_ip, mascaras_subrede, subredes_por_roteador_atualizadas,
      roteadores, switches_borda, especificacoes_rede
    """
    G = nx.Graph()
    network_class = "Classe C"
    base_ip = "192.168.1."
    subnet_mask_class = "255.255.255.0"
    network_address = "192.168.1.0"
    broadcast_address = "192.168.1.255"

    print("=== Configuração da Rede ===\n")
    while True:
        try:
            num_roteadores = int(input("Quantos roteadores a rede deve possuir? (mínimo 1): "))
            if num_roteadores < 1:
                print("Número mínimo de roteadores é 1.\n")
            else:
                break
        except ValueError:
            print("Entrada inválida. Insira um número inteiro.\n")
    roteadores = [f"a{i+1}" for i in range(num_roteadores)]
    G.add_node("Switch Central", tipo='Switch Central')

    ip_counter = 1
    enderecos_ip = {}
    switch_central_ip = f"{base_ip}{ip_counter}"
    enderecos_ip["Switch Central"] = switch_central_ip
    ip_counter += 1
    print(f"Assignando IP ao Switch Central: {switch_central_ip}")

    for roteador in roteadores:
        G.add_node(roteador, tipo='Roteador de Agregação')
        roteador_ip = f"{base_ip}{ip_counter}"
        enderecos_ip[roteador] = roteador_ip
        print(f"Assignando IP ao Roteador {roteador}: {roteador_ip}")
        ip_counter += 1

    subredes_por_roteador = {}
    total_subredes = 0
    print("\n=== Configuração das Subredes por Roteador ===")
    for roteador in roteadores:
        while True:
            try:
                num_subredes = int(input(f"Quantas subredes o roteador {roteador} gerenciará? (mínimo 1): "))
                if num_subredes < 1:
                    print("Cada roteador deve gerenciar pelo menos 1 subrede.\n")
                else:
                    subredes_por_roteador[roteador] = num_subredes
                    total_subredes += num_subredes
                    break
            except ValueError:
                print("Entrada inválida. Insira um número inteiro.\n")

    subredes_definidas = {}
    print("\n=== Definição das Subredes ===")
    for i in range(1, total_subredes + 1):
        subrede = f"e{i}"
        while True:
            nome = input(f"Digite o nome para a subrede {subrede} (ou pressione Enter para usar '{subrede}'): ").strip()
            if nome == "":
                nome = subrede
            if nome in subredes_definidas:
                print("Nome já utilizado. Escolha outro.\n")
            else:
                break
        while True:
            try:
                capacidade = int(input(f"Quantos hosts a subrede '{nome}' suportará? (mínimo 0): "))
                if capacidade < 0:
                    print("Número negativo não é permitido.\n")
                else:
                    break
            except ValueError:
                print("Entrada inválida. Insira um número inteiro.\n")
        subredes_definidas[nome] = {"capacidade": capacidade}
    print()

    active_subnets = [nome for nome, info in subredes_definidas.items() if info["capacidade"] > 0]
    inactive_subnets = [nome for nome, info in subredes_definidas.items() if info["capacidade"] == 0]

    subredes_por_roteador_atualizadas = {roteador: [] for roteador in roteadores}
    num_roteadores = len(roteadores)
    active_total = len(active_subnets)
    inactive_total = len(inactive_subnets)
    active_per_router = active_total // num_roteadores
    active_extra = active_total % num_roteadores
    inactive_per_router = inactive_total // num_roteadores
    inactive_extra = inactive_total % num_roteadores

    random.shuffle(active_subnets)
    random.shuffle(inactive_subnets)
    index = 0
    for i, roteador in enumerate(roteadores):
        count = active_per_router + (1 if i < active_extra else 0)
        for _ in range(count):
            if index < active_total:
                subredes_por_roteador_atualizadas[roteador].append(active_subnets[index])
                index += 1
    index = 0
    for i, roteador in enumerate(roteadores):
        count = inactive_per_router + (1 if i < inactive_extra else 0)
        for _ in range(count):
            if index < inactive_total:
                subredes_por_roteador_atualizadas[roteador].append(inactive_subnets[index])
                index += 1

    subredes = {}
    mascaras_subrede = {}
    enlaces = []
    print("=== Configuração das Subredes e Hosts ===")
    for roteador, subrede_list in subredes_por_roteador_atualizadas.items():
        print(f"\nConfiguração do Roteador {roteador}:")
        for subrede in subrede_list:
            capacidade = subredes_definidas[subrede]["capacidade"]
            status = "Ativa" if capacidade > 0 else "Inativa"
            print(f"  Subrede '{subrede}' - {status} com {capacidade} hosts.")
            subredes[subrede] = {
                "hosts": [f"Host {subrede}-{j}" for j in range(1, capacidade + 1)],
                "roteador": roteador,
                "mask": subnet_mask_class,
                "capacidade": capacidade
            }
            mascaras_subrede[subrede] = subnet_mask_class
            switch_borda = f"Switch {subrede}"
            G.add_node(switch_borda, tipo='Switch de Borda')
            switch_borda_ip = f"{base_ip}{ip_counter}"
            enderecos_ip[switch_borda] = switch_borda_ip
            print(f"  Assignando IP ao {switch_borda}: {switch_borda_ip}")
            ip_counter += 1
            if capacidade > 0:
                for host in subredes[subrede]["hosts"]:
                    host_ip = f"{base_ip}{ip_counter}"
                    enderecos_ip[host] = host_ip
                    print(f"    Assignando IP ao {host}: {host_ip}")
                    ip_counter += 1
    print()

    switches_borda = [f"Switch {subrede}" for subrede in subredes.keys() if subredes[subrede]["capacidade"] > 0]
    for switch in switches_borda:
        G.add_node(switch, tipo='Switch de Borda')

    print("=== Configuração dos Enlaces ===")
    for roteador in roteadores:
        G.add_edge("Switch Central", roteador, tipo_enlace='Fibra Óptica', capacidade='1 Gbps')
        enlaces.append(("Switch Central", roteador, {'tipo_enlace': 'Fibra Óptica', 'capacidade': '1 Gbps'}))
        print(f"  Switch Central <--> {roteador}: Fibra Óptica, 1 Gbps")
    for subrede, info in subredes.items():
        roteador = info["roteador"]
        switch_borda = f"Switch {subrede}"
        G.add_edge(roteador, switch_borda, tipo_enlace='Par Trançado', capacidade='100 Mbps')
        enlaces.append((roteador, switch_borda, {'tipo_enlace': 'Par Trançado', 'capacidade': '100 Mbps'}))
        print(f"  {roteador} <--> {switch_borda}: Par Trançado, 100 Mbps")
        if info["capacidade"] > 0:
            G.add_nodes_from(info["hosts"], tipo='Host')
            for host in info["hosts"]:
                G.add_edge(switch_borda, host, tipo_enlace='Par Trançado', capacidade='100 Mbps')
                enlaces.append((switch_borda, host, {'tipo_enlace': 'Par Trançado', 'capacidade': '100 Mbps'}))
                print(f"    {switch_borda} <--> {host}: Par Trançado, 100 Mbps")
        else:
            print(f"    (Subrede '{subrede}' não utilizada)")
    print()

    especificacoes_rede = {
        "Classe de Rede": network_class,
        "Endereço de Rede": network_address,
        "Máscara de Subrede Padrão": subnet_mask_class,
        "Endereço de Broadcast": broadcast_address,
        "Total de Roteadores": len(roteadores),
        "Total de Subredes": len(subredes),
        "Total de Hosts": ip_counter - 1,
        "Enlaces": enlaces
    }

    return G, subredes, enderecos_ip, mascaras_subrede, subredes_por_roteador_atualizadas, roteadores, switches_borda, especificacoes_rede


###############################################
# FUNÇÃO PARA DESENHAR A TOPOLOGIA DA REDE (MELHORADA)
###############################################
def desenhar_topologia(G):
    plt.figure(figsize=(16, 12))
    pos = nx.spring_layout(G, seed=42, k=0.3)

    # Cores suaves com bordas pretas
    color_map = []
    for node in G:
        tipo = G.nodes[node].get('tipo', 'Unknown')
        if tipo == 'Switch Central':
            color_map.append('#FF6347')  # Tomato
        elif tipo == 'Roteador de Agregação':
            color_map.append('#FFA500')  # Laranja
        elif tipo == 'Switch de Borda':
            color_map.append('#32CD32')  # Verde Limão
        elif tipo == 'Host':
            color_map.append('#87CEFA')  # Azul Céu Claro
        else:
            color_map.append('#D3D3D3')  # Cinza Claro

    nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=2000, edgecolors='black', linewidths=1.5)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', font_family='sans-serif')

    # Configuração das arestas
    edge_colors = []
    edge_widths = []
    for u, v, data in G.edges(data=True):
        tipo_enlace = data.get('tipo_enlace', 'Default')
        if tipo_enlace == 'Fibra Óptica':
            edge_colors.append('#8A2BE2')  # Blue Violet
            edge_widths.append(3)
        elif tipo_enlace == 'Par Trançado':
            edge_colors.append('#1E90FF')  # Dodger Blue
            edge_widths.append(2)
        else:
            edge_colors.append('gray')
            edge_widths.append(1.5)

    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths, alpha=0.8)

    # Legenda personalizada
    import matplotlib.patches as mpatches
    from matplotlib.lines import Line2D
    legend_elements = [
        mpatches.Patch(facecolor='#FF6347', edgecolor='black', label='Switch Central'),
        mpatches.Patch(facecolor='#FFA500', edgecolor='black', label='Roteador de Agregação'),
        mpatches.Patch(facecolor='#32CD32', edgecolor='black', label='Switch de Borda'),
        mpatches.Patch(facecolor='#87CEFA', edgecolor='black', label='Host'),
        Line2D([0], [0], color='#8A2BE2', lw=3, label='Fibra Óptica'),
        Line2D([0], [0], color='#1E90FF', lw=2, label='Par Trançado')
    ]
    plt.legend(handles=legend_elements, loc='upper left', fontsize=12,
               frameon=True, facecolor='white', edgecolor='black')

    plt.title("Topologia de Rede - Árvore Hierárquica", fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.show()


###############################################
# FUNÇÕES DE EXIBIÇÃO DE CONFIGURAÇÃO E IPs
###############################################
def exibir_enderecos_ip(enderecos_ip):
    print("\n==== Tabela de Endereços IP ====")
    print(f"{'Dispositivo':<25} {'Endereço IP':<15}")
    print("-" * 40)
    for dispositivo, ip in sorted(enderecos_ip.items()):
        print(f"{dispositivo:<25} {ip:<15}")
    print("-" * 40)


def exibir_configuracao_rede(subredes, mascaras_subrede, subredes_por_roteador, roteadores, switches_borda, especificacoes_rede, enderecos_ip):
    print("\n==== Configuração da Rede ====")
    for chave, valor in especificacoes_rede.items():
        print(f"{chave}: {valor}")
    print("\n---- Endereços IP ----")
    exibir_enderecos_ip(enderecos_ip)


###############################################
# FUNÇÕES DE PING E TRACEROUTE
###############################################
def ping(G, enderecos_ip, origem, destino):
    if origem not in enderecos_ip or destino not in enderecos_ip:
        return f"Ping de {origem} para {destino}: Falha (host inexistente)\n"
    if nx.has_path(G, origem, destino):
        latencia = round(random.uniform(1, 100), 2)
        return (f"Ping de {origem} ({enderecos_ip.get(origem)}) para {destino} ({enderecos_ip.get(destino)}):\n"
                f"  Pacotes: 4 enviados, 4 recebidos, 0% perda\n"
                f"  Tempo médio: {latencia} ms\n")
    else:
        return f"Ping de {origem} para {destino}: Falha (sem rota disponível)\n"


def traceroute(G, enderecos_ip, origem, destino):
    if origem not in enderecos_ip or destino not in enderecos_ip:
        return f"Traceroute de {origem} para {destino}: Sem rota disponível\n"
    if nx.has_path(G, origem, destino):
        caminho = nx.shortest_path(G, origem, destino)
        resultado = "Traceroute:\n"
        for i, node in enumerate(caminho):
            resultado += f"  {i+1}. {node} ({enderecos_ip.get(node)})\n"
        return resultado
    else:
        return f"Traceroute de {origem} para {destino}: Sem rota disponível\n"


###############################################
# MENU INTERATIVO DO SIMULADOR DE REDE
###############################################
def menu(G, subredes, enderecos_ip, mascaras_subrede, subredes_por_roteador, roteadores, switches_borda, especificacoes_rede):
    while True:
        print("\n==== Simulador de Rede ====")
        print("1. Exibir Topologia da Rede")
        print("2. Executar Ping")
        print("3. Executar Traceroute")
        print("4. Exibir Endereços IP")
        print("5. Exibir Configuração da Rede")
        print("6. Criar Datagram IP")
        print("7. Sair")
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            desenhar_topologia(G)
        elif opcao == "2":
            origem = input("Digite o nome do host de origem (ex.: Host e1-1): ").strip()
            destino = input("Digite o nome do host de destino (ex.: Host e2-5): ").strip()
            print(ping(G, enderecos_ip, origem, destino))
        elif opcao == "3":
            origem = input("Digite o nome do host de origem (ex.: Host e1-1): ").strip()
            destino = input("Digite o nome do host de destino (ex.: Host e2-5): ").strip()
            print(traceroute(G, enderecos_ip, origem, destino))
        elif opcao == "4":
            exibir_enderecos_ip(enderecos_ip)
        elif opcao == "5":
            exibir_configuracao_rede(subredes, mascaras_subrede, subredes_por_roteador, roteadores, switches_borda, especificacoes_rede, enderecos_ip)
        elif opcao == "6":
            criar_e_visualizar_datagrama(enderecos_ip)
        elif opcao == "7":
            print("Encerrando o simulador...")
            break
        else:
            print("Opção inválida. Tente novamente.")


###############################################
# FUNÇÃO MAIN – INÍCIO DO SIMULADOR
###############################################
def main():
    G, subredes, enderecos_ip, mascaras_subrede, subredes_por_roteador, roteadores, switches_borda, especificacoes_rede = configurar_rede()
    desenhar_topologia(G)
    menu(G, subredes, enderecos_ip, mascaras_subrede, subredes_por_roteador, roteadores, switches_borda, especificacoes_rede)


main()
