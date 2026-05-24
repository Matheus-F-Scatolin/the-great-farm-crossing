# FORMULAÇÃO DO PROBLEMA CUSTOMIZADO
## "A Grande Travessia da Fazenda" (Ovelhas, Raposas e Fazendeiros)

> **Inspirações:** *River Crossing Problem* (Downey, *The Little Book of Semaphores*) + enigma clássico do **lobo, da cabra/ovelha e do repolho** (Alcuin de York, *Propositiones ad acuendos juvenes*, ~800 d.C.) — fazendeiro, barco e restrições de convivência nas margens do rio.

**Sim, é totalmente possível** e, na verdade, essa adaptação eleva a complexidade do problema original de forma brilhante! No clássico *River Crossing*, temos apenas 2 categorias hidrogenadas/ideológicas (Linux vs Windows) e uma barreira simétrica de 4 lugares. A versão de Alcuin traz o fazendeiro, animais e “planta” com regras de exclusão mútua nas margens; aqui substituímos o lobo por **raposas**, mantemos **ovelhas** (no lugar da cabra) e transformamos o fazendeiro em uma **categoria de thread** entre várias que competem pelo barco. A adaptação introduz **3 categorias com restrições de segurança baseadas em predicados de estado**, o que é um prato cheio para o uso avançado de **Variáveis de Condição**.

### Regras do Jogo (Capacidade Máxima do Barco = 3)
Na margem de origem, todos os passageiros começam "vigiados" em suas respectivas filas. O barco só pode partir se atingir uma das seguintes combinações válidas de 3 passageiros:

1. **3 Raposas** (Se controlam sozinhas na viagem).
2. **3 Ovelhas** (Viajam em paz).
3. **3 Fazendeiros** (Viajam em paz).
4. **1 ou 2 Fazendeiros + Qualquer mistura de animais** (Totalizando obrigatoriamente 3 passageiros). O fazendeiro atua como a trava de segurança; se ele estiver a bordo, as raposas não atacam as ovelhas e ninguém se come.

*Qualquer outra combinação (ex: 2 raposas e 1 ovelha sem fazendeiro) faria o barco virar uma carnificina, sendo uma combinação estritamente proibida pelo algoritmo.*

---

### Mapeamento dos Conceitos de Sincronização

Para implementar essa lógica robusta no código em C (`pthreads`), você estruturará o seguinte fluxo:

#### 1. Mutex Global e Variáveis de Condição
Você precisará de um mutex para proteger as variáveis que contam quantos passageiros de cada tipo estão na fila da margem e quantos já embarcaram.
```c
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond_embarque = PTHREAD_COND_INITIALIZER;
pthread_cond_t cond_viagem = PTHREAD_COND_INITIALIZER;

int raposas_na_fila = 0, ovelhas_na_fila = 0, fazendeiros_na_fila = 0;
int no_barco_raposas = 0, no_barco_ovelhas = 0, no_barco_fazendeiros = 0;
int barco_ocupacao = 0;
```

#### 2. O Predicado de Validação (A Lógica do Barco)

Sempre que uma nova thread chega à margem, ela incrementa seu respectivo contador de fila. A thread então entra em um laço de verificação. Apenas a combinação correta permitirá que os passageiros saiam do estado de espera.

Uma função de verificação simula se o passageiro atual pode fechar um "combo" válido com quem já está na fila:

```c
int combinacao_valida(int r, int o, int f) {
    int total = r + o + f;
    if (total != 3) return 0; // Barco precisa sair cheio com 3
    
    // Regra 1: Apenas Raposas
    if (r == 3) return 1;
    // Regra 2: Apenas Ovelhas
    if (o == 3) return 1;
    // Regra 3: Apenas Fazendeiros
    if (f == 3) return 1;
    // Regra 4: Mistura guardada por 1 ou 2 fazendeiros
    if ((f == 1 || f == 2) && (r > 0 || o > 0)) return 1;

    return 0; // Qualquer outra combinação é inválida
}
```

#### 3. O Mecanismo do Rendezvous (Encontro) e o Líder da Rodada (Continuação)

* **Formando o Grupo:** Quando uma thread percebe que sua entrada na fila valida uma das combinações permitidas, ela altera o estado do barco (transferindo os passageiros da fila para dentro do veículo) e acorda via `pthread_cond_broadcast` as threads específicas que ela escolheu para viajar consigo.
* **O Líder:** A última thread que entrou e disparou o sinal assume o papel de **Líder**. É ela quem vai chamar a função de animação gráfica do barco atravessando o rio (`atravessar_rio()`).
* **Barreira de Desembarque:** As outras duas threads que subiram a bordo entram em um segundo estágio de espera (`pthread_cond_wait(&cond_viagem, &mutex)`). Elas só acordam e finalizam sua execução quando o Líder termina a jornada e sinaliza que o barco atracou com segurança na margem oposta.

Veja abaixo o esboço estrutural de como as threads de cada criatura (ex: Ovelha) se comportam no código:

```c
void* thread_ovelha(void* arg) {
    pthread_mutex_lock(&mutex);
    
    ovelhas_na_fila++;
    printf("[Fila] Mais uma ovelha chegou. Total na fila: %d\n", ovelhas_na_fila);
    
    int sou_lider = 0;
    
    while (1) {
        // Caso 1: Fechar um combo de 3 ovelhas
        if (ovelhas_na_fila >= 3 && barco_ocupacao == 0) {
            ovelhas_na_fila -= 3;
            no_barco_ovelhas = 3;
            barco_ocupacao = 3;
            sou_lider = 1;
            pthread_cond_broadcast(&cond_embarque);
            break;
        }
        // Caso 2: Fechar combo com pelo menos 1 fazendeiro disponível e espaço no barco
        else if (fazendeiros_na_fila >= 1 && (ovelhas_na_fila + raposas_na_fila + fazendeiros_na_fila) >= 3 && barco_ocupacao == 0) {
            // A lógica exata de seleção do combo misto entraria aqui
            // ...
            sou_lider = 1;
            pthread_cond_broadcast(&cond_embarque);
            break;
        }
        
        // Se não fecha nenhum combo válido, espera na fila
        pthread_cond_wait(&cond_embarque, &mutex);
        
        // Se foi acordada porque já foi selecionada por outra thread líder
        if (no_barco_ovelhas > 0 && barco_ocupacao > 0) {
            break; 
        }
    }
    
    // --- ESTADO: A BORDO DO BARCO ---
    if (sou_lider) {
        pthread_mutex_unlock(&mutex);
        
        // O líder é o único que invoca a animação física no Pygame/Visualizador
        atravessar_rio_animacao(); 
        
        pthread_mutex_lock(&mutex);
        // Reseta o estado do barco para a próxima viagem
        no_barco_raposas = 0;
        no_barco_ovelhas = 0;
        no_barco_fazendeiros = 0;
        barco_ocupacao = 0;
        
        // Acorda os outros 2 tripulantes para desembarcarem
        pthread_cond_broadcast(&cond_viagem); 
    } else {
        // Os passageiros comuns esperam a animação do líder terminar
        pthread_cond_wait(&cond_viagem, &mutex);
    }
    
    printf("[Desembarque] Ovelha cruzou o rio com segurança!\n");
    pthread_mutex_unlock(&mutex);
    return NULL;
}
```

Com este modelo conceitual, seu professor verá a aplicação prática de **Exclusão Mútua**, **Sincronização Condicional Coletiva** (Barreiras de tamanho variável) e o padrão de design **Líder-Seguidor**. Usar pacotes 2D de fazenda/animais no Pygame vai deixar o visual incrivelmente intuitivo!