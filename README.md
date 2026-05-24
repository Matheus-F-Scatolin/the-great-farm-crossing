# The Great Farm Crossing (A Grande Travessia da Fazenda) 🌾🛶

Animação multithread interativa desenvolvida como projeto prático para a disciplina **MC504 - Sistemas Operacionais** (Instituto de Computação - UNICAMP).

O projeto consiste em uma aplicação concorrente que resolve e visualiza um problema complexo de sincronização de threads utilizando **C (Pthreads)** no ecossistema de backend e uma interface gráfica rica desenvolvida em **Python (Pygame)**.

---

## 📚 Inspirações

Este projeto combina e estende duas fontes clássicas:

1. ***The Little Book of Semaphores*** (Allen B. Downey) — o *River Crossing Problem*, usado como referência de sincronização com threads, mutex e variáveis de condição.
2. **Problema do lobo, da cabra e do repolho** (*Propositiones ad acuendos juvenes*, Alcuin de York, século IX) — o enigma do fazendeiro que precisa atravessar um rio em um barco pequeno, levando um lobo, uma cabra (em muitas versões populares, uma **ovelha**) e um **repolho** (couve), sem deixar o lobo com a cabra/ovelha ou a cabra/ovelha com o repolho sozinhos em uma margem.

**A Grande Travessia da Fazenda** retoma esse clima de fazenda e travessia de rio, mas adapta o enredo para o contexto de SO: em vez de um único fazendeiro transportando um item por viagem, há **filas concorrentes** de ovelhas, raposas e fazendeiros, um barco com **capacidade 3**, e regras de embarque pensadas para exercitar mutex, condvars e o padrão líder-seguidor.

---

## 📝 O Problema: Ovelhas, Raposas e Fazendeiros

Inspirado no clássico *River Crossing Problem* do livro *The Little Book of Semaphores* e, no tema de fazenda e travessia de rio, no **problema do lobo, da cabra (ou ovelha) e do repolho** de Alcuin de York, esta versão estende a complexidade lógica ao introduzir **três categorias de threads** com restrições de segurança assimétricas baseadas em predicados de estado.

Na margem de origem de um rio, três tipos de personagens (threads) chegam de forma estocástica e aguardam em suas respectivas filas: **Ovelhas**, **Raposas** e **Fazendeiros**. O objetivo é transportá-los para a outra margem em um barco com capacidade máxima de **exatamente 3 passageiros**.

### Regras de Segurança (Predicados de Embarque):
Para que o barco possa partir com segurança sem que ocorra uma "carnificina" (condição de corrida lógica), a combinação de passageiros deve satisfazer estritamente um dos seguintes critérios:
1. **3 Raposas** (Viajam em harmonia cooperativa).
2. **3 Ovelhas** (Viajam em paz).
3. **3 Fazendeiros** (Viajam em paz).
4. **1 ou 2 Fazendeiros + Qualquer mistura de animais** (A presença do fazendeiro atua como trava de segurança, impedindo que as raposas ataquem as ovelhas durante o trajeto).

Qualquer outra combinação (ex: 2 raposas e 1 ovelha sem um fazendeiro) violará as restrições e o algoritmo impedirá o embarque.

---

## 🛠️ Arquitetura de Sincronização e Conceitos de S.O.

Para garantir a corretude e a exclusão mútua, o projeto explora robustamente os seguintes conceitos de Sistemas Operacionais:

* **Mutex Locks (`pthread_mutex_t`):** Garantem a exclusão mútua e evitam condições de corrida ao manipular os contadores globais das filas e o estado de ocupação do barco.
* **Variáveis de Condição (`pthread_cond_t`):** Utilizadas para bloquear as threads nas filas até que uma combinação válida seja formada, disparando sinais eficientes (`pthread_cond_broadcast`) para acordar as categorias exatas de threads selecionadas.
* **Barreiras de Sincronização (Rendezvous):** Mecanismo que garante que os 3 passageiros se encontrem e subam a bordo de forma coordenada antes do início da viagem.
* **Padrão Líder-Seguidor (Leader-Follower):** A última thread a subir a bordo e validar o predicado assume o papel de **Líder**. Ela é a única responsável por invocar a rotina de animação da travessia e, ao atracar, sinaliza às outras duas threads ("seguidoras") que o desembarque está liberado.

---

## 🎨 O Visualizador (Pygame UI)

A interface gráfica foi construída utilizando a biblioteca **Pygame** com pacotes de assets 2D gratuitos de alta qualidade, garantindo uma visualização clara da evolução do estado global do sistema em tempo real.

* **Renderização de Estados:** Exibição dinâmica das filas acumulando na margem esquerda, o processo de embarque dos 3 tripulantes selecionados, o deslocamento físico do barco pelo rio e o desembarque seguro na margem direita.
* **Variação de Parâmetros:** Através da interface ou de arquivos de configuração, é possível alterar dinamicamente taxas de chegada das threads (frequência de geração de cada criatura), velocidade do barco e limites de simulação.