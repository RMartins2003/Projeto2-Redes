# Simulador de Rede com Datagram IP (CLI)

Este projeto é um simulador de rede desenvolvido em Python que permite:

- Configurar uma rede simulada: Definindo o número de roteadores, subredes por roteador e a capacidade (número de hosts) de cada subrede.
- Gerar e visualizar um datagrama IPv4: O datagrama é construído com todos os campos do cabeçalho conforme o padrão IPv4 (versão, IHL, Type of Service – com DiffServ e ECN, Total Length, Identification, Flags, Fragment Offset, TTL, Protocol, Checksum, Source IP, Destination IP, Options e Payload). O cálculo do checksum é realizado de acordo com o padrão (soma de 16 bits com carry e complemento de 1).
- Simular comandos de rede: Executa testes de ping e traceroute com base na conectividade da rede configurada.
- Exibir a topologia da rede: Utilizando o NetworkX e Matplotlib para desenhar um diagrama da rede.

O projeto não possui interface gráfica; todas as interações são feitas por meio do terminal (linha de comando).

## Pré-requisitos

Certifique-se de ter instalados os seguintes pacotes:

- Python 3.x 
- NetworkX– para a simulação da topologia da rede.  
- Matplotlib– para desenhar os diagramas (do datagrama IPv4 e da topologia).

Caso não os possua, instale via `pip`:

```bash
pip install networkx matplotlib
