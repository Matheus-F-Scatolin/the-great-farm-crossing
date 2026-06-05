# The Great Farm Crossing (A Grande Travessia da Fazenda) 🌾🛶

Animação multithread desenvolvida como projeto prático para a disciplina **MC504 - Sistemas Operacionais** (Instituto de Computação - UNICAMP).

O projeto consiste de uma aplicação concorrente robusta implementada em **C (Pthreads)** e de um visualizador desacoplado em **Python (Pygame)**. O motor físico e a interface comunicam-se via protocolo de eventos **JSONL** em `stdout`.

---

## 📚 Inspirações e Formulação

1. ***The Little Book of Semaphores*** (Allen B. Downey): O problema clássico da travessia de rio (*River Crossing Problem*), onde threads de diferentes tipos precisam cooperar em grupos de tamanho fixo para cruzar um obstáculo compartilhado.
2. **O Problema do Lobo, da Cabra e do Repolho** (Enigma medieval de Alcuin de York, *Propositiones ad Acuendos Juvenes*): Adaptado para um ecossistema concorrente moderno composto de três filas concorrentes: **Ovelhas**, **Raposas** e **Fazendeiros**. 

---

## 📝 O Problema

Na margem esquerda de um rio, chegam de forma independente e assíncrona três tipos de personagens. Um barco com capacidade para **exatamente 3 passageiros** realiza a travessia. Para evitar que hajam mortes, o embarque deve respeitar um **predicado de segurança rigoroso**:

* **Combinações Homogêneas (Válidas):** 
  * 3 Raposas (elas não brigam entre si no barco).
  * 3 Ovelhas (viajam tranquilamente juntas).
  * 3 Fazendeiros (três trabalhadores focados).
* **Combinações Heterogêneas (Válidas):**
  * Qualquer mistura de 3 passageiros que inclua **pelo menos 1 Fazendeiro** (ex: 1 Fazendeiro, 1 Raposa e 1 Ovelha; ou 2 Fazendeiros e 1 Raposa; etc.). A presença de um ou mais humanos garante a ordem a bordo, impedindo que as raposas devorem as ovelhas.
* **Combinações Inválidas (Perigosas):**
  * Misturas de animais sem a presença de um fazendeiro (ex: 2 Raposas e 1 Ovelha; ou 1 Raposa e 2 Ovelhas). Nessas condições, as raposas atacariam as ovelhas, violando a segurança da simulação.

Após atracar e desembarcar os passageiros na margem direita, o barco retorna **vazio** para a esquerda para buscar o próximo combo.

### 📈 Modelagem Estocástica de Chegadas (Processo de Poisson)
As threads não chegam de forma estática. O nascimento de cada personagem segue um **Processo de Poisson**, simulando chegadas estocásticas e independentes no tempo. 
Para cada tipo de thread, o intervalo entre as chegadas é governado por um parâmetro de taxa de chegada $\lambda$ (definido em Hertz, ou seja, chegadas/segundo). 
No código, o tempo de atraso ($t_{\text{wait}}$) para a ativação de cada thread é gerado sorteando uma variável uniforme $u \in (0, 1]$ e aplicando a distribuição exponencial inversa:

$$t_{\text{wait}} = \frac{-\ln(u)}{\lambda}$$

Isso garante uma simulação realista e dinâmica, na qual a ordem e o ritmo de chegada das filas são imprevisíveis, desafiando ativamente os algoritmos de sincronização.

---

## 🛠️ Arquitetura

A sincronização das threads em C foi projetada utilizando as primitivas nativas da biblioteca `pthread`, garantindo segurança de memória, exclusão mútua e ausência de deadlocks indesejados.

### 🔒 Primitivas Utilizadas
* `pthread_mutex_t g_mutex`: Exclusão mútua estrita que protege o estado global compartilhado (`FarmState`), que compreende as filas, o estado do barco e os contadores da margem direita.
* `pthread_cond_t g_cond_embarque`: Variável de condição para controlar a fila de espera. Threads que chegam à margem dormem nesta variável até que um combo seguro de 3 passageiros possa ser formado ou até que o barco abra vagas de embarque compatíveis com seus tipos.
* `pthread_cond_t g_cond_viagem`: Variável de condição usada como barreira de viagem. Os passageiros que embarcam como seguidores bloqueiam-se nesta condvar até que a thread líder termine a travessia e anuncie o desembarque seguro.

### 👑 O Padrão Líder-Seguidor (Leader-Follower)
A coordenação de cada viagem é descentralizada e dinâmica:
1. **Formação de Combo:** Cada thread, ao chegar e obter o mutex, verifica se o barco está vazio e na margem esquerda. Se sim, ela tenta encontrar um combo válido de 3 elementos a partir das threads presentes na fila (usando uma ordem de busca determinística).
2. **Eleição do Líder:** A thread que descobre um combo viável consome os personagens da fila, assume os 3 slots do barco e se autodeclara **Líder** daquela travessia. As outras duas threads do combo tornam-se **Seguidoras**.
3. **Reserva e Embarque:** O líder sinaliza `g_cond_embarque`. As threads seguidoras do tipo selecionado acordam, reivindicam seus slots individuais no barco (`trip_boarded++`) e incrementam o contador de embarque.
4. **Travessia Independente (Fora da Região Crítica):** Com o barco cheio (`trip_boarded == 3`), o líder **libera o mutex** (`g_mutex`) e realiza a travessia (`atravessar_rio()`). Isso permite que outras threads continuem chegando e se organizando na margem durante a viagem, sem bloquear o resto do sistema.
5. **Barreira de Viagem:** Enquanto o líder viaja, os seguidores aguardam bloqueados na variável `g_cond_viagem`.
6. **Conclusão:** Ao final da travessia física, o líder readquire o mutex, atualiza os contadores da margem direita, redefine o barco como vazio, acorda as threads seguidoras via `pthread_cond_broadcast(&g_cond_viagem)` e sinaliza `g_cond_embarque` para iniciar o próximo ciclo de viagem.

### 🛑 Detecção Dinâmica de Deadlocks
Uma fragilidade comum no problema de travessia do rio é o travamento definitivo (*deadlock*) no final da execução se o número total de threads geradas for desbalanceado (por exemplo, sobrar apenas 2 Ovelhas e 1 Raposa na fila, que não podem cruzar sozinhas sem um fazendeiro). 

Para resolver isso de forma elegante, o motor C possui um detector dinâmico de deadlock (`farm_deadlock`):
* O sistema monitora o número de threads que ainda vão nascer (`pendentes_chegada`).
* Se não houver mais threads por vir (`pendentes_chegada == 0`), o barco estiver vazio na esquerda, houver elementos na fila, mas **nenhum combo válido de 3 puder ser formado**, o motor detecta o deadlock inevitável.
* Ele altera `simulacao_ativa = 0`, acorda todas as threads adormecidas na fila de embarque, permitindo que elas saiam de forma limpa da execução (`pthread_join` bem-sucedido) e encerra o programa de maneira graciosa sem travar a máquina ou o terminal.

---

## Pré-requisitos

- **gcc** com suporte a pthreads
- **make**
- **Python 3.10+** e **pygame-ce** (apenas para o visualizador)

## Build e execução

```bash
make

# Simulação (JSON em stdout, logs em stderr)
./run.sh --raposas 6 --ovelhas 9 --fazendeiros 3 --seed 42

# Gravar eventos para o visualizador (pasta runs/ ja existe no repo)
./run.sh --raposas 6 --ovelhas 9 --fazendeiros 3 --seed 42 > runs/demo.jsonl 2> runs/demo.log

# Sem JSON (só logs em stderr)
./farm_crossing --no-vis --raposas 6 --ovelhas 9 --fazendeiros 3

# Visualizador (requer display; instalar deps uma vez)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m ui.main -i runs/demo.jsonl
# Controles: Espaço pausa, +/- velocidade, R reset, Esc sair
```

### Parâmetros CLI

| Flag | Descrição | Default |
|------|-----------|---------|
| `--raposas N` | Número de threads raposa | 6 |
| `--ovelhas N` | Número de threads ovelha | 9 |
| `--fazendeiros N` | Número de threads fazendeiro | 3 |
| `--lambda-raposa F` | Taxa de chegada (1/seg) | 0.5 |
| `--lambda-ovelha F` | Taxa de chegada (1/seg) | 0.4 |
| `--lambda-fazendeiro F` | Taxa de chegada (1/seg) | 0.3 |
| `--seed N` | Semente aleatória | 42 |
| `--boat-speed-ms N` | Duração da travessia (ms); `dur_ms` em `PARTIDA` | 1200 |
| `--embark-ms N` | Pausa entre embarques/desembarques no C | 200 |
| `--return-ms N` | Duração do retorno; `dur_ms` em `RETORNO` | 800 |
| `--max-travessias-completas N` | Limite de viagens (0 = sem limite) | 0 |
| `--no-vis` | Desliga JSON no stdout | off |

> Combinações muito desbalanceadas podem deadlock. Demo estável: `6/9/3`.

---

## Estrutura do repositório

```
├── src/                  # Motor de simulação em C
│   ├── config.h          # Configurações de simulação
│   ├── farm.h / .c       # Definições de estado, regras de combos e detecção de deadlock
│   ├── threads.h / .c    # Ciclo de vida das threads (lider-seguidor)
│   ├── visor_ipc.h / .c  # Serializador de eventos para JSONL (stdout)
│   └── main.c            # Ponto de entrada, parse do CLI e orquestração de pthreads
├── ui/                   # Visualizador Gráfico em Python (Pygame-ce)
│   ├── protocol.py       # Conversor do formato de dados JSONL para objetos Python
│   ├── replay.py         # Motor de tempo, controle de velocidade e pausa
│   ├── state.py          # Máquina de estados visual derivada
│   ├── scene.py          # Renderizador da paisagem, água e movimento do barco
│   └── main.py           # Interface de inicialização do Pygame
├── assets/               # Imagens, sprites de pixel-art e folhas de sprites
├── presentation/         # Slides e roteiro da apresentação acadêmica (HTML)
├── Makefile              # Automação do build do motor C
├── run.sh                # Script facilitador de execução e gravação de logs
├── requirements.txt      # Dependências em Python (pygame-ce)
└── README.md             # Esta documentação
```

## IPC (C → visualizador)

Uma linha JSON por evento em `stdout`:

```json
{"evt":"EMBARQUE","who":"OVELHA","id":2,"fila":{"r":1,"o":3,"f":0},"barco":{"r":0,"o":1,"f":0,"lado":"ESQUERDA","ocupacao":3},"direita":{"r":0,"o":0,"f":0},"travessias_completas":0,"ts":1234}
```

Eventos: `CHEGOU`, `EMBARQUE`, `PARTIDA`, `ATRACOU`, `DESEMBARQUE`, `RETORNO`, `FIM`.

Mapeamento de tilesets e sprites: [assets/CREDITS.md](assets/CREDITS.md).

## Créditos de assets

Ver [assets/CREDITS.md](assets/CREDITS.md).
