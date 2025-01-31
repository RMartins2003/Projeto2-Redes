import networkx as nx
import random
import matplotlib.pyplot as plt
import sys

def configurar_rede():
    G = nx.Graph()

    # Definição da classe de rede
    network_class = "Classe C"
    base_ip = "192.168.1."
    subnet_mask_class = "255.255.255.0"
    network_address = "192.168.1.0"
    broadcast_address = "192.168.1.255"

    # Informações Gerais da Rede
    print("=== Configuração da Rede ===\n")

    # Configuração dos Roteadores
    while True:
        try:
            num_roteadores = int(input("Quantos roteadores a rede deve possuir? (mínimo 1): "))
            if num_roteadores < 1:
                print("Número mínimo de roteadores é 1.\n")
            else:
                break
        except ValueError:
            print("Entrada inválida. Por favor, insira um número inteiro.\n")

    roteadores = [f"a{i+1}" for i in range(num_roteadores)]
    G.add_node("Switch Central", tipo='Switch Central')

    # Atribuição de IP ao Switch Central
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

    # Configuração das Subredes por Roteador
    subredes_por_roteador = {}
    total_subredes = 0
    print("\n=== Configuração das Subredes por Roteador ===")
    for roteador in roteadores:
        while True:
            try:
                num_subredes = int(input(f"Quantas subredes o roteador {roteador} irá gerenciar? (mínimo 1): "))
                if num_subredes < 1:
                    print("Cada roteador deve gerenciar pelo menos 1 subrede.\n")
                else:
                    subredes_por_roteador[roteador] = num_subredes
                    total_subredes += num_subredes
                    break
            except ValueError:
                print("Entrada inválida. Por favor, insira um número inteiro.\n")

    # Coleta das Subredes
    subredes_definidas = {}
    print("\n=== Definição das Subredes ===")
    for i in range(1, total_subredes + 1):
        subrede = f"e{i}"
        while True:
            nome = input(f"Digite o nome para a subrede {subrede} (ou pressione Enter para usar '{subrede}'): ").strip()
            if nome == "":
                nome = subrede
            if nome in subredes_definidas:
                print("Nome de subrede já utilizado. Por favor, escolha outro nome.\n")
            else:
                break
        while True:
            try:
                capacidade = int(input(f"Quantos hosts a subrede '{nome}' irá suportar? (mínimo 0): "))
                if capacidade < 0:
                    print("A quantidade de hosts não pode ser negativa.\n")
                else:
                    break
            except ValueError:
                print("Entrada inválida. Por favor, insira um número inteiro.\n")
        subredes_definidas[nome] = {
            "capacidade": capacidade
        }
    print()

    # Separar Subredes Ativas e Inativas
    active_subnets = [nome for nome, info in subredes_definidas.items() if info["capacidade"] > 0]
    inactive_subnets = [nome for nome, info in subredes_definidas.items() if info["capacidade"] == 0]

    # Distribuição Equilibrada de Subredes Ativas e Inativas
    subredes_por_roteador_atualizadas = {roteador: [] for roteador in roteadores}

    # Calculando a distribuição
    num_roteadores = len(roteadores)
    active_total = len(active_subnets)
    inactive_total = len(inactive_subnets)

    active_per_router = active_total // num_roteadores
    active_extra = active_total % num_roteadores

    inactive_per_router = inactive_total // num_roteadores
    inactive_extra = inactive_total % num_roteadores

    # Shuffle para distribuição aleatória
    random.shuffle(active_subnets)
    random.shuffle(inactive_subnets)

    # Distribuir Subredes Ativas
    index = 0
    for i, roteador in enumerate(roteadores):
        count = active_per_router + (1 if i < active_extra else 0)
        for _ in range(count):
            if index < active_total:
                subredes_por_roteador_atualizadas[roteador].append(active_subnets[index])
                index += 1

    # Distribuir Subredes Inativas
    index = 0
    for i, roteador in enumerate(roteadores):
        count = inactive_per_router + (1 if i < inactive_extra else 0)
        for _ in range(count):
            if index < inactive_total:
                subredes_por_roteador_atualizadas[roteador].append(inactive_subnets[index])
                index += 1

    # Configuração das Subredes e Hosts
    subredes = {}
    mascaras_subrede = {}
    enlaces = []

    print("=== Configuração das Subredes e Hosts ===")
    for roteador, subrede_list in subredes_por_roteador_atualizadas.items():
        print(f"\nConfiguração do Roteador {roteador}:")
        for subrede in subrede_list:
            capacidade = subredes_definidas[subrede]["capacidade"]
            status = "Ativa" if capacidade > 0 else "Inativa"
            print(f"  Subrede '{subrede}' está {status} com {capacidade} hosts.")
            subredes[subrede] = {
                "hosts": [f"Host {subrede}-{j}" for j in range(1, capacidade + 1)],
                "roteador": roteador,
                "mask": subnet_mask_class,
                "capacidade": capacidade
            }

            mascaras_subrede[subrede] = subnet_mask_class

            # Assign IP to Switch de Borda
            switch_borda = f"Switch {subrede}"
            G.add_node(switch_borda, tipo='Switch de Borda')
            switch_borda_ip = f"{base_ip}{ip_counter}"
            enderecos_ip[switch_borda] = switch_borda_ip
            print(f"Assignando IP ao {switch_borda}: {switch_borda_ip}")
            ip_counter += 1

            if capacidade > 0:
                # Atribuição de IPs aos Hosts
                for host in subredes[subrede]["hosts"]:
                    host_ip = f"{base_ip}{ip_counter}"
                    enderecos_ip[host] = host_ip
                    ip_counter += 1

    print()

    # Configuração dos Switches de Borda e Hosts
    switches_borda = [f"Switch {subrede}" for subrede in subredes.keys() if subredes[subrede]["capacidade"] > 0]
    for switch in switches_borda:
        G.add_node(switch, tipo='Switch de Borda')

    # Conexões Iniciais entre Switch Central e Roteadores
    print("=== Configuração dos Enlaces ===")
    for roteador in roteadores:
        G.add_edge("Switch Central", roteador, tipo_enlace='Fibra Óptica', capacidade='1 Gbps')
        enlaces.append(("Switch Central", roteador, {'tipo_enlace': 'Fibra Óptica', 'capacidade': '1 Gbps'}))
        print(f"  Switch Central <--> {roteador}: Fibra Óptica, 1 Gbps")

    # Conexão das Subredes aos Roteadores e Adição de Hosts
    for subrede, info in subredes.items():
        roteador = info["roteador"]
        switch_borda = f"Switch {subrede}"
        G.add_edge(roteador, switch_borda, tipo_enlace='Par Trançado', capacidade='100 Mbps')
        enlaces.append((roteador, switch_borda, {'tipo_enlace': 'Par Trançado', 'capacidade': '100 Mbps'}))
        print(f"  {roteador} <--> {switch_borda}: Par Trançado, 100 Mbps")

        if info["capacidade"] > 0:
            # Adiciona hosts ao grafo e conecta ao switch de borda
            G.add_nodes_from(info["hosts"], tipo='Host')
            for host in info["hosts"]:
                G.add_edge(switch_borda, host, tipo_enlace='Par Trançado', capacidade='100 Mbps')
                enlaces.append((switch_borda, host, {'tipo_enlace': 'Par Trançado', 'capacidade': '100 Mbps'}))
                print(f"    {switch_borda} <--> {host}: Par Trançado, 100 Mbps")
        else:
            print(f"    (Subrede '{subrede}' não utilizada)")
    print()

    # Armazenamento das especificações da rede
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

def desenhar_topologia(G):
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, seed=42)

    # Definição de cores por tipo de equipamento
    color_map = []
    for node in G:
        tipo = G.nodes[node].get('tipo', 'Unknown')
        if tipo == 'Switch Central':
            color_map.append('red')
        elif tipo == 'Roteador de Agregação':
            color_map.append('orange')
        elif tipo == 'Switch de Borda':
            color_map.append('green')
        elif tipo == 'Host':
            color_map.append('lightblue')
        else:
            color_map.append('gray')

    # Desenho dos nós
    nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=1500)
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')

    # Desenho das arestas com estilos diferentes baseados no tipo de enlace
    edge_colors = []
    for u, v, data in G.edges(data=True):
        tipo_enlace = data.get('tipo_enlace', 'Default')
        if tipo_enlace == 'Fibra Óptica':
            edge_colors.append('purple')
        elif tipo_enlace == 'Par Trançado':
            edge_colors.append('blue')
        else:
            edge_colors.append('gray')

    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2)

    # Criação de legendas para os tipos de equipamentos e enlaces
    import matplotlib.patches as mpatches
    from matplotlib.lines import Line2D

    legend_elements = [
        mpatches.Patch(color='red', label='Switch Central'),
        mpatches.Patch(color='orange', label='Roteador de Agregação'),
        mpatches.Patch(color='green', label='Switch de Borda'),
        mpatches.Patch(color='lightblue', label='Host'),
        Line2D([0], [0], color='purple', lw=2, label='Fibra Óptica'),
        Line2D([0], [0], color='blue', lw=2, label='Par Trançado')
    ]
    plt.legend(handles=legend_elements, loc='upper right')

    plt.title("Topologia de Rede - Árvore Hierárquica")
    plt.axis('off')
    plt.show()

def exibir_enderecos_ip(enderecos_ip):
    print("\n==== Tabela de Endereços IP ====")
    print(f"{'Dispositivo':<25} {'Endereço IP':<15}")
    print("-" * 40)
    for dispositivo, ip in sorted(enderecos_ip.items()):
        print(f"{dispositivo:<25} {ip:<15}")
    print("-" * 40)

def exibir_configuracao_rede(subredes, mascaras_subrede, subredes_por_roteador, roteadores, switches_borda, especificacoes_rede, enderecos_ip):
    print("\n==== Configuração da Rede ====")
    print(f"Classe de Rede: {especificacoes_rede['Classe de Rede']}")
    print(f"Endereço de Rede: {especificacoes_rede['Endereço de Rede']}")
    print(f"Máscara de Subrede Padrão: {especificacoes_rede['Máscara de Subrede Padrão']}")
    print(f"Endereço de Broadcast: {especificacoes_rede['Endereço de Broadcast']}")
    print(f"Total de Roteadores: {especificacoes_rede['Total de Roteadores']}")
    print(f"Total de Subredes: {especificacoes_rede['Total de Subredes']}")
    print(f"Total de Hosts: {especificacoes_rede['Total de Hosts']}\n")

    print("---- Roteadores ----")
    for roteador in roteadores:
        total_atribuido = len(subredes_por_roteador[roteador])
        ativo = len([s for s in subredes_por_roteador[roteador] if subredes[s]["capacidade"] > 0])
        inativo = total_atribuido - ativo
        print(f"  Roteador {roteador}: {ativo} subredes ativas e {inativo} subredes inativas de {total_atribuido} atribuídas")
    print()

    print("---- Subredes ----")
    for subrede, info in subredes.items():
        hosts_disponiveis = len(info["hosts"])
        hosts_usados = len([host for host in info["hosts"] if host in enderecos_ip and enderecos_ip[host] != "0"])
        mask = mascaras_subrede.get(subrede, "N/A")
        status = "Ativa" if info["capacidade"] > 0 else "Inativa"
        print(f"  Subrede '{subrede}':")
        print(f"    Roteador: {info['roteador']}")
        print(f"    Hosts Disponíveis: {hosts_disponiveis}")
        print(f"    Hosts Utilizados: {hosts_usados}")
        print(f"    Máscara: {mask}")
        print(f"    Status: {status}")
    print()

    print("---- Hosts ----")
    for subrede, info in subredes.items():
        for host in info["hosts"]:
            ip = enderecos_ip.get(host, "0")
            if ip == "0":
                continue  # Ignora subredes não utilizadas
            print(f"  {host}: {ip}")
    print()

    print("---- Enlaces ----")
    for enlace in especificacoes_rede['Enlaces']:
        u, v, attrs = enlace
        tipo = attrs.get('tipo_enlace', 'N/A')
        capacidade = attrs.get('capacidade', 'N/A')
        print(f"  {u} <--> {v}: Tipo de Enlace - {tipo}, Capacidade - {capacidade}")
    print("-" * 50)

def ping(G, enderecos_ip, origem, destino):
    if origem not in G or destino not in G:
        return f"Ping de {origem} para {destino}: Falha (nó inexistente)\n"

    if G.nodes[origem].get('tipo') != 'Host' or G.nodes[destino].get('tipo') != 'Host':
        return f"Ping de {origem} para {destino}: Falha (origem ou destino não é um host válido)\n"

    if nx.has_path(G, origem, destino):
        latencia = round(random.uniform(1, 100), 2)  # Latência em ms
        return (f"Ping de {origem} ({enderecos_ip.get(origem, 'N/A')}) para {destino} ({enderecos_ip.get(destino, 'N/A')}):\n"
                f"  Pacotes: 4 enviados, 4 recebidos, 0% perda\n"
                f"  Tempo médio: {latencia} ms\n")
    else:
        return f"Ping de {origem} para {destino}: Falha (sem rota disponível)\n"

def traceroute(G, enderecos_ip, origem, destino):
    if origem not in G or destino not in G:
        return f"Traceroute de {origem} para {destino}: Sem rota disponível\n"

    if G.nodes[origem].get('tipo') != 'Host' or G.nodes[destino].get('tipo') != 'Host':
        return f"Traceroute de {origem} para {destino}: Falha (origem ou destino não é um host válido)\n"

    if nx.has_path(G, origem, destino):
        caminho = nx.shortest_path(G, origem, destino)
        resultado = "Traceroute:\n"
        for i, node in enumerate(caminho):
            ip = enderecos_ip.get(node, 'N/A')
            resultado += f"  {i+1}. {node} ({ip})\n"
        return resultado
    else:
        return f"Traceroute de {origem} para {destino}: Sem rota disponível\n"

def menu(G, subredes, enderecos_ip, mascaras_subrede, subredes_por_roteador, roteadores, switches_borda, especificacoes_rede):
    while True:
        print("\n==== Simulador de Rede ====")
        print("1. Exibir Topologia da Rede")
        print("2. Executar Ping")
        print("3. Executar Traceroute")
        print("4. Exibir Endereços IP")
        print("5. Exibir Configuração da Rede")
        print("6. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            desenhar_topologia(G)
        elif opcao == "2":
            origem = input("Digite o nome do host de origem (ex: Host e1-1): ").strip()
            destino = input("Digite o nome do host de destino (ex: Host e2-5): ").strip()
            resultado = ping(G, enderecos_ip, origem, destino)
            print(resultado)
        elif opcao == "3":
            origem = input("Digite o nome do host de origem (ex: Host e1-1): ").strip()
            destino = input("Digite o nome do host de destino (ex: Host e2-5): ").strip()
            resultado = traceroute(G, enderecos_ip, origem, destino)
            print(resultado)
        elif opcao == "4":
            exibir_enderecos_ip(enderecos_ip)
        elif opcao == "5":
            exibir_configuracao_rede(subredes, mascaras_subrede, subredes_por_roteador, roteadores, switches_borda, especificacoes_rede, enderecos_ip)
        elif opcao == "6":
            print("Encerrando o simulador...")
            break
        else:
            print("Opção inválida. Escolha novamente.")

# Execução do programa
def main():
    G, subredes, enderecos_ip, mascaras_subrede, subredes_por_roteador, roteadores, switches_borda, especificacoes_rede = configurar_rede()
    if subredes:
        desenhar_topologia(G)
        menu(G, subredes, enderecos_ip, mascaras_subrede, subredes_por_roteador, roteadores, switches_borda, especificacoes_rede)


main()
