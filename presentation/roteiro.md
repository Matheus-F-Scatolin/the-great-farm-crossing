# Roteiro do video: A Grande Travessia da Fazenda

Duracao alvo: 8 a 10 minutos.

## Slide 1 - Capa (0:00-0:35)

"Ola, eu sou o Matheus Ferracciu Scatolin, RA 252099, e este e o projeto A Grande Travessia da Fazenda, desenvolvido para MC504. A ideia central foi criar uma simulacao multithread em C, usando pthreads, mutex e variaveis de condicao, e representar a execucao com um visualizador grafico em Pygame.

O projeto nao e apenas uma animacao: a animacao reflete eventos reais emitidos pelo motor da simulacao."

## Slide 2 - Enunciado (0:35-1:10)

"O enunciado pedia uma aplicacao multithread que explorasse sincronizacao e tambem um visualizador do estado global. Eu quis evitar que a saida fosse so uma sequencia de logs, porque logs mostram eventos isolados, mas nao deixam claro o estado do sistema em cada momento.

Entao o objetivo virou: fazer threads competirem por um recurso compartilhado, o barco, e mostrar essa disputa visualmente."

## Slide 3 - Inspiracao (1:10-1:45)

"A formulacao mistura duas referencias. A primeira e o River Crossing Problem, do The Little Book of Semaphores, que e uma familia de problemas em que passageiros precisam formar grupos validos para atravessar.

A segunda e o enigma classico do lobo, da cabra e do repolho. No meu caso, adaptei isso para raposas, ovelhas e fazendeiros. O fazendeiro atua como uma especie de garantia de seguranca: se ele esta no barco, raposas e ovelhas podem viajar juntas."

## Slide 4 - Conceitos de SO no problema (1:45-2:35)

"Antes de entrar nas regras específicas do barco, vale mapear os conceitos de Sistemas Operacionais para elementos do problema.

O mutex aparece como a proteção do estado global: fila, barco e margem direita não podem ser atualizados por duas threads ao mesmo tempo. As variáveis de condição aparecem quando uma thread precisa dormir até que o estado mude: por exemplo, até existir um combo válido para embarcar ou até a viagem terminar.

O predicado é a regra que decide se o estado atual permite continuar. E o padrão líder-seguidor aparece quando uma thread fecha o grupo e conduz a travessia, enquanto as outras sincronizam com ela."

## Slide 5 - Regras do barco (2:35-3:10)

"O barco tem capacidade exatamente 3. Ele so parte cheio, e a combinacao precisa ser segura.

Sao validos: 3 raposas, 3 ovelhas, 3 fazendeiros, ou uma mistura com 1 ou 2 fazendeiros e animais. O caso perigoso e misturar raposa e ovelha sem fazendeiro.

Essa regra e importante porque ela vira o predicado de sincronizacao. As threads nao embarcam so porque chegaram; elas embarcam quando o estado da fila permite uma combinacao valida."

## Slide 6 - Chegadas estocasticas com lambda (3:10-4:00)

"As entidades nao chegam todas ao mesmo tempo. Cada tipo tem uma taxa de chegada, chamada lambda. No README existem parametros como `--lambda-raposa`, `--lambda-ovelha` e `--lambda-fazendeiro`.

A interpretacao e: lambda e a taxa media de chegada por segundo. Isso modela um processo de Poisson, em que chegadas acontecem de forma independente ao longo do tempo. Para simular isso no codigo, eu nao sorteio diretamente a quantidade de chegadas; eu sorteio o tempo de espera ate a proxima chegada.

Esse tempo segue uma distribuicao exponencial, calculada no codigo como `delay = -log(u) / lambda`. No grafico, quando lambda aumenta, a curva fica mais concentrada perto de zero. Em termos praticos: as threads tendem a chegar mais rapidamente, a fila muda mais rapido e a ordem dos combos pode variar mais."

## Slide 7 - Modelo concorrente (4:00-4:40)

"O modelo de concorrencia e uma thread por passageiro. Cada raposa, ovelha e fazendeiro nasce como uma thread independente.

No ciclo de vida, a thread primeiro espera seu atraso de chegada. Depois entra na fila protegida pelo mutex. Em seguida, tenta formar um combo como lider ou tenta reivindicar um slot se outro lider ja reservou um combo que inclui o seu tipo.

Isso cria a concorrencia real: varias threads podem acordar em tempos diferentes, disputar o mutex e depender de condicoes globais para continuar."

## Slide 8 - Estado compartilhado (4:40-5:20)

"O estado compartilhado fica em `FarmState`. Ele guarda os contadores da fila esquerda, os passageiros reservados no barco, os passageiros que ja chegaram na margem direita, a ocupacao do barco, o lado do barco, o numero de travessias e alguns campos de controle da viagem atual.

Esse estado e pequeno, mas concentra toda a verdade da simulacao. Por isso ele e protegido por `g_mutex`. Uma decisao importante foi separar o motor da UI: o Pygame nao acessa esse estado diretamente. Ele recebe eventos com snapshots desse estado."

## Slide 9 - Predicado e escolha de combo (5:20-6:05)

"A funcao `combinacao_valida` implementa a regra do problema. Primeiro ela exige total 3. Depois aceita os tres casos homogeneos: 3 raposas, 3 ovelhas ou 3 fazendeiros. Por fim, aceita misturas quando existe 1 ou 2 fazendeiros a bordo.

A funcao `escolher_combo` percorre uma lista fixa de combinacoes possiveis e escolhe a primeira que a fila consegue formar. Depois `aplicar_combo` tira esses passageiros da fila e reserva os slots do barco.

Essa separacao deixa claro o que e regra do problema e o que e atualizacao do estado."

## Slide 10 - Sincronizacao e lider-seguidor (6:05-6:55)

"Aqui esta o desenho da sincronizacao principal. A sincronizacao usa um mutex global e duas variaveis de condicao principais.

`g_cond_embarque` acorda threads quando um combo pode ser formado ou quando existe slot reservado para embarque. `g_cond_viagem` serve para a barreira da viagem: os seguidores esperam o lider terminar a travessia.

O padrao e lider-seguidor. A thread que fecha o combo vira lider. Ela e responsavel por executar a travessia e emitir os eventos de partida, atracacao, desembarque e retorno. As outras duas threads embarcam como seguidoras e aguardam a conclusao."

## Slide 11 - Fluxo de uma viagem (6:55-7:30)

"Uma viagem aparece como uma sequencia de eventos: CHEGOU, EMBARQUE, PARTIDA, ATRACOU, DESEMBARQUE, RETORNO e, no fim, FIM.

O ponto legal e que essa sequencia vem da simulacao, nao de uma animacao inventada depois. Quando o lider chama a travessia, o motor emite `PARTIDA`, espera a duracao configurada, emite `ATRACOU`, emite desembarques e depois `RETORNO`.

Isso permite que o visualizador reproduza o ritmo real da execucao."

## Slide 12 - IPC em JSONL (7:30-8:10)

"A comunicacao entre o C e a UI e por JSONL: uma linha JSON por evento no stdout. Os logs humanos ficam no stderr, entao e facil salvar os eventos em um arquivo e usar esse arquivo no replay.

Cada evento carrega o tipo do evento, quem participou, contadores da fila, estado do barco, margem direita, numero de travessias e timestamp. Eventos como `PARTIDA` e `RETORNO` tambem carregam duracao.

Essa escolha deixou o visualizador desacoplado. A UI nao precisa conhecer pthreads; ela so precisa entender o protocolo de eventos."

## Slide 13 - Visualizador Pygame (8:10-8:55)

"No Pygame, `protocol.py` transforma cada linha JSON em objetos Python. `replay.py` usa os timestamps para agendar os eventos e controlar pausa e velocidade. `state.py` mantem um estado visual derivado, porque alguns eventos do motor carregam snapshots que precisam ser interpretados no momento certo. E `scene.py` desenha o fundo, as filas, o barco interpolado, os passageiros e o HUD.

Aqui entram os prints da execucao: primeiro o combo misto, depois o barco atravessando e finalmente a tela de fim. Esses prints mostram que a visualizacao esta ligada aos eventos reais da simulacao."

## Slide 14 - LLMs, aprendizados e demo (8:55-10:00)

"Eu tambem usei ferramentas de LLM em algumas etapas. Usei para revisar conceitos de sincronizacao, para ajudar a formular um problema mais criativo a partir do River Crossing e do enigma da fazenda, e para apoiar a elaboracao dos slides.

Na UI Pygame, a ajuda com Cursor e LLM nao resolveu tudo. Parte dos recortes e ajustes de assets precisou ser feita manualmente. Entao minha contribuicao principal foi transformar as sugestoes em uma implementacao coerente: definir o protocolo, ajustar o modelo de estado, integrar o replay e garantir que as regras de sincronizacao fossem respeitadas.

Para a demo, eu sugiro rodar a execucao curta com `--raposas 4 --ovelhas 4 --fazendeiros 1 --seed 1`, porque ela mostra logo o combo misto de raposa, ovelha e fazendeiro. Depois, se houver tempo, mencionar que `runs/demo.jsonl` tem uma execucao maior com 6 viagens.

Com isso, o projeto cobre os pontos principais: problema criativo, sincronizacao real com pthreads, parametros variaveis, visualizacao clara e uma separacao limpa entre motor e interface."

## Prints usados nos slides

1. `presentation/assets/screenshots/embarque.png`: momento de embarque/combo no visualizador.
2. `presentation/assets/screenshots/atravessando.png`: barco no meio do rio logo apos `PARTIDA`.
3. `presentation/assets/screenshots/fim.png`: overlay `FIM` com o total de viagens.

## Comandos da demo

```bash
./run.sh --raposas 4 --ovelhas 4 --fazendeiros 1 --seed 1 > runs/mixed.jsonl 2> runs/mixed.log
python -m ui.main -i runs/mixed.jsonl
```
