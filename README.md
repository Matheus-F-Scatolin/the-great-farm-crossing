# The Great Farm Crossing (A Grande Travessia da Fazenda) 🌾🛶

Animação multithread desenvolvida como projeto prático para a disciplina **MC504 - Sistemas Operacionais** (Instituto de Computação - UNICAMP).

O repositório contém o **motor de simulação em C (Pthreads)** e os **assets** para uma interface gráfica a ser implementada separadamente. A especificação completa da UI e o contrato de dados estão em [handoff.md](handoff.md).

---

## 📚 Inspirações

1. ***The Little Book of Semaphores*** (Allen B. Downey) — *River Crossing Problem*.
2. **Problema do lobo, da cabra e do repolho** (Alcuin de York) — adaptado para filas concorrentes de ovelhas, raposas e fazendeiros, barco com capacidade **3**, e predicados de embarque com mutex/condvars e padrão líder–seguidor.

---

## 📝 O Problema

Na margem esquerda, três filas chegam de forma estocástica: **Ovelhas**, **Raposas**, **Fazendeiros**. O barco transporta **exatamente 3** passageiros por viagem quando a combinação é válida (3 iguais, ou 1–2 fazendeiros com animais). Após desembarque na margem direita, o barco volta vazio à esquerda.

---

## 🛠️ Arquitetura

- **Motor C:** threads, mutex, variáveis de condição, líder–seguidor.
- **Saída para visualização:** uma linha JSON por evento em `stdout` (ver [handoff.md](handoff.md)).
- **UI (futura):** processo ou ferramenta **separada** que lê o JSON gravado ou um pipe — **não** compartilha memória com o C. Fluxo recomendado: rodar `./farm_crossing ... > runs/demo.jsonl` e depois reproduzir com controles de pausa/velocidade.

---

## Pré-requisitos

- **gcc** com suporte a pthreads
- **make**

## Build e execução

```bash
make

# Simulação (JSON em stdout, logs em stderr)
./run.sh --raposas 6 --ovelhas 9 --fazendeiros 3 --seed 42

# Gravar eventos para a UI futura (pasta runs/ ja existe no repo)
./run.sh --raposas 6 --ovelhas 9 --fazendeiros 3 --seed 42 > runs/demo.jsonl 2> runs/demo.log

# Sem JSON (só logs em stderr)
./farm_crossing --no-vis --raposas 6 --ovelhas 9 --fazendeiros 3
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
| `--max-cruzes N` | Limite de viagens (0 = sem limite) | 0 |
| `--no-vis` | Desliga JSON no stdout | off |

> Combinações muito desbalanceadas podem deadlock. Demo estável: `6/9/3`.

---

## Estrutura do repositório

```
src/           Motor C (pthreads, mutex, condvars, JSON em stdout)
assets/        Tilesets e sprites (VectoRaith, fox, barco) — ver assets/CREDITS.md
handoff.md     Especificação da UI + protocolo + arquitetura desacoplada
Makefile
run.sh
```

## IPC (C → visualizador futuro)

Uma linha JSON por evento em `stdout`:

```json
{"evt":"EMBARQUE","who":"OVELHA","id":2,"fila":{"r":1,"o":3,"f":0},"barco":{"r":0,"o":1,"f":0,"lado":"ESQUERDA","ocupacao":3},"direita":{"r":0,"o":0,"f":0},"cruzes":0,"ts":1234}
```

Eventos: `CHEGOU`, `EMBARQUE`, `PARTIDA`, `ATRACOU`, `DESEMBARQUE`, `RETORNO`, `FIM`.

Detalhes, layout da tela, tilesets e controles de velocidade: **[handoff.md](handoff.md)** (seções 6 e 7).

## Créditos de assets

Ver [assets/CREDITS.md](assets/CREDITS.md).
