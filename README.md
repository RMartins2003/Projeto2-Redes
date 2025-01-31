# Projeto2_FINALFINAL – Simulador de Rede com Datagram IP (CLI)

Este projeto é um simulador de rede desenvolvido em Python que permite:

- **Configurar uma rede simulada**: definir o número de roteadores, subredes por roteador e a capacidade (número de hosts) de cada subrede.
- **Gerar e visualizar um datagrama IPv4**: o datagrama é construído com todos os campos do cabeçalho conforme o padrão IPv4, incluindo:
  - **Version (4 bits)**
  - **Header Length (4 bits)** – em palavras de 32 bits e em bytes
  - **Type of Service (8 bits)** – dividido em DiffServ (6 bits) e ECN (2 bits)
  - **Total Length (16 bits)**
  - **Identification (16 bits)**
  - **Flags (3 bits)**
  - **Fragment Offset (13 bits)**
  - **Time To Live (8 bits)**
  - **Protocol (8 bits)**
  - **Header Checksum (16 bits)**
  - **Source IP Address (32 bits)**
  - **Destination IP Address (32 bits)**
  - **IP Options** (se houver – ajustadas para múltiplos de 4 bytes)
  - **Data Portion** (Payload)
- **Simular comandos de rede**: executar testes de *ping* e *traceroute* (simulados) com base na conectividade da rede configurada.
- **Exibir a topologia da rede**: utilizando o NetworkX e o Matplotlib para desenhar um diagrama da rede.

> **ATENÇÃO:**
> Este repositório contém dois arquivos. **BAIXE E UTILIZE APENAS O ARQUIVO `projeto2_FINALFINAL.py`**, pois é nele que se encontra a implementação completa do simulador. O outro arquivo não faz parte da solução final deste projeto.

## 📌 Pré-requisitos

Certifique-se de ter instalado:

- **Python 3.x**

Além disso, instale as seguintes dependências (caso ainda não estejam instaladas):

```bash
pip install networkx matplotlib
```

## 🚀 Como Executar

Siga os passos abaixo para executar o projeto:

### 1️⃣ Clone o repositório ou baixe o arquivo:

```bash
git clone https://github.com/seu-usuario/projeto2_FINALFINAL.git
cd projeto2_FINALFINAL
```

### 2️⃣ Execute o projeto:

No terminal, execute o seguinte comando:

```bash
python projeto2_FINALFINAL.py
```

> **Observação:** Em alguns sistemas, pode ser necessário utilizar `python3` em vez de `python`.

### 3️⃣ Interaja com o Menu Interativo:

Ao executar o projeto, um menu será exibido no terminal com as seguintes opções:

#### 📌 **Configurar Rede:**
- Insira os parâmetros solicitados (número de roteadores, subredes por roteador e capacidade de hosts por subrede) para configurar a rede.
- O script exibirá um resumo da configuração e uma tabela com os endereços IP.

#### 📌 **Gerar Datagram IP:**
- Informe os parâmetros do datagrama (endereço IP de origem, destino, payload e protocolo).
- O script exibirá os detalhes completos do datagrama (todos os campos com seus tamanhos em bits e a representação em hexadecimal) e abrirá uma janela com um diagrama ilustrativo do cabeçalho.

#### 📌 **Executar Ping/Traceroute:**
- Informe os nomes dos dispositivos (por exemplo, "Host a1-e1-1") e escolha entre ping e traceroute para simular a conectividade entre eles.

#### 📌 **Visualizar Topologia da Rede:**
- Exibe um diagrama da rede com a estrutura hierárquica dos dispositivos (utilizando NetworkX e Matplotlib).

#### 📌 **Exibir Configuração da Rede:**
- Mostra um resumo completo da configuração, incluindo a tabela de endereços IP.

## 🔍 Lógica da Rede

A rede simulada possui a seguinte estrutura:

### 🏛 **Hierarquia:**
- **Switch Central:** Ponto de conexão principal.
- **Roteadores de Agregação:** Conectados ao Switch Central; cada roteador gerencia uma ou mais subredes.
- **Subredes:** Cada subrede possui um Switch de Borda que conecta vários Hosts.
- **Endereçamento IP:** Os endereços IP são atribuídos sequencialmente a partir de um endereço base (por exemplo, `192.168.1.1` para o Switch Central).

### 🔗 **Conectividade:**
- **Roteadores** se conectam ao **Switch Central** via enlaces de alta velocidade (ex.: Fibra Óptica).
- **Subredes** se conectam aos roteadores via enlaces de menor velocidade (ex.: Par Trançado).

### 📦 **Datagrama IPv4:**
- O datagrama é composto por um cabeçalho detalhado e um payload.
- O cabeçalho inclui todos os campos obrigatórios conforme o padrão IPv4.
- O checksum é calculado com base na soma de 16 bits (com carry) e o complemento de 1.

---

📌 **Desenvolvido para o Projeto 2 da disciplina de Redes de Computadores.**
