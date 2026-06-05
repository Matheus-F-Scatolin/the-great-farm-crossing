#define _DEFAULT_SOURCE
#define _XOPEN_SOURCE 600

#include "threads.h"

#include <math.h>
#include <pthread.h>
#include <stdlib.h>
#include <unistd.h>

#ifdef _WIN32
#include <windows.h>
#define usleep(us) Sleep((us) / 1000)
#endif

#include "visor_ipc.h"

static double lambda_for_tipo(TipoPassageiro tipo) {
    switch (tipo) {
    case TIPO_RAPOSA:
        return g_config.lambda_raposa;
    case TIPO_OVELHA:
        return g_config.lambda_ovelha;
    case TIPO_FAZENDEIRO:
        return g_config.lambda_fazendeiro;
    }
    return 0.5;
}

static void sleep_arrival_delay(TipoPassageiro tipo) {
    double lambda = lambda_for_tipo(tipo);
    if (lambda <= 0.0) {
        return;
    }
    double u = (double)rand() / (double)RAND_MAX;
    if (u <= 0.0) {
        u = 0.0001;
    }
    double delay = -log(u) / lambda;
    usleep((unsigned int)(delay * 1000000.0));
}

static void increment_fila(TipoPassageiro tipo) {
    switch (tipo) {
    case TIPO_RAPOSA:
        g_farm.raposas_fila++;
        break;
    case TIPO_OVELHA:
        g_farm.ovelhas_fila++;
        break;
    case TIPO_FAZENDEIRO:
        g_farm.fazendeiros_fila++;
        break;
    }
}

static int try_claim_boarding_slot(TipoPassageiro tipo, int id) {
    if (g_farm.barco_ocupacao != 3) {
        return 0;
    }
    if (farm_slots_disponiveis_tipo(tipo) <= 0) {
        return 0;
    }
    if (!farm_claim_slot(&g_farm, tipo)) {
        return 0;
    }
    visor_emit_embarque(tipo, id);
    visor_log("[Embarque] %s %d subiu no barco (%d/%d)\n", tipo_nome(tipo), id,
              g_farm.trip_boarded, 3);
    if (g_farm.trip_boarded == 3) {
        pthread_cond_broadcast(&g_cond_embarque);
    }
    return 1;
}

static int combo_inclui_tipo(int r, int o, int f, TipoPassageiro tipo) {
    switch (tipo) {
    case TIPO_RAPOSA:
        return r > 0;
    case TIPO_OVELHA:
        return o > 0;
    case TIPO_FAZENDEIRO:
        return f > 0;
    }
    return 0;
}

static int try_form_combo_as_leader(int id, TipoPassageiro tipo) {
    int r, o, f;
    if (!escolher_combo(&g_farm, &r, &o, &f)) {
        return 0;
    }
    if (!combo_inclui_tipo(r, o, f, tipo)) {
        return 0;
    }
    if (g_config.max_travessias_completas > 0 && g_farm.travessias_completas_feitas >= g_config.max_travessias_completas) {
        return 0;
    }

    aplicar_combo(&g_farm, r, o, f);
    g_farm.trip_leader_id = id;

    visor_log("[Lider] %s %d formou combo (%d,%d,%d)\n", tipo_nome(tipo), id, r, o, f);

    if (!try_claim_boarding_slot(tipo, id)) {
        visor_log("[Erro] lider %d nao conseguiu embarcar\n", id);
    }
    pthread_cond_broadcast(&g_cond_embarque);
    return 1;
}

static int simulacao_terminou(void) {
    return g_farm.raposas_direita >= g_farm.total_raposas &&
           g_farm.ovelhas_direita >= g_farm.total_ovelhas &&
           g_farm.fazendeiros_direita >= g_farm.total_fazendeiros;
}

/*
 * Ciclo de vida de cada passageiro (padrao lider–seguidor):
 * 1) chegada estocastica e entrada na fila;
 * 2) espera em cond_embarque ate reservar slot (lider forma combo ou seguidor entra);
 * 3) barreira de 3 embarques antes da viagem;
 * 4) lider chama atravessar_rio() sem mutex; seguidores aguardam cond_viagem.
 */
void *passageiro_thread(void *arg) {
    PassageiroArg *p = (PassageiroArg *)arg;
    int id = p->id;
    TipoPassageiro tipo = p->tipo;

    sleep_arrival_delay(tipo);

    pthread_mutex_lock(&g_mutex);

    if (!g_farm.simulacao_ativa) {
        pthread_mutex_unlock(&g_mutex);
        free(p);
        return NULL;
    }

    increment_fila(tipo);
    g_farm.pendentes_chegada--;
    visor_emit_chegou(tipo, id);
    visor_log("[Fila] %s %d chegou. Fila r=%d o=%d f=%d\n", tipo_nome(tipo), id,
              g_farm.raposas_fila, g_farm.ovelhas_fila, g_farm.fazendeiros_fila);

    int sou_lider = 0;
    int embarcou = 0;

    while (!embarcou && g_farm.simulacao_ativa) {
        /* Barco vazio na margem esquerda: tentativa de formar um novo combo como lider. */
        if (g_farm.barco_ocupacao == 0 && g_farm.barco_lado == LADO_ESQUERDA) {
            if (try_form_combo_as_leader(id, tipo)) {
                sou_lider = 1;
                embarcou = 1;
                break;
            }
        /* Combo ja reservado: seguidores reivindicam slots restantes do tipo deles. */
        } else if (g_farm.barco_ocupacao == 3 && g_farm.trip_boarded < 3) {
            if (try_claim_boarding_slot(tipo, id)) {
                embarcou = 1;
                break;
            }
        }

        if (farm_deadlock(&g_farm)) {
            visor_log("[Erro] Deadlock: fila r=%d o=%d f=%d nao forma combo valido\n",
                      g_farm.raposas_fila, g_farm.ovelhas_fila, g_farm.fazendeiros_fila);
            g_farm.simulacao_ativa = 0;
            pthread_cond_broadcast(&g_cond_embarque);
            pthread_cond_broadcast(&g_cond_viagem);
            break;
        }

        pthread_cond_wait(&g_cond_embarque, &g_mutex);
    }

    if (!embarcou) {
        pthread_mutex_unlock(&g_mutex);
        free(p);
        return NULL;
    }

    if (!g_farm.simulacao_ativa) {
        pthread_mutex_unlock(&g_mutex);
        free(p);
        return NULL;
    }

    while (g_farm.trip_boarded < 3 && g_farm.simulacao_ativa) {
        pthread_cond_wait(&g_cond_embarque, &g_mutex);
    }

    int trip_r = g_farm.raposas_barco;
    int trip_o = g_farm.ovelhas_barco;
    int trip_f = g_farm.fazendeiros_barco;

    if (sou_lider) {
        /* Animacao/travessia fora da secao critica para nao bloquear as outras threads. */
        pthread_mutex_unlock(&g_mutex);
        atravessar_rio(id, trip_r, trip_o, trip_f);
        pthread_mutex_lock(&g_mutex);

        g_farm.raposas_direita += trip_r;
        g_farm.ovelhas_direita += trip_o;
        g_farm.fazendeiros_direita += trip_f;
        g_farm.travessias_completas_feitas++;

        g_farm.raposas_barco = 0;
        g_farm.ovelhas_barco = 0;
        g_farm.fazendeiros_barco = 0;
        g_farm.barco_ocupacao = 0;
        g_farm.trip_boarded = 0;
        g_farm.trip_leader_id = -1;

        visor_log("[Desembarque] viagem %d concluida. Direita r=%d o=%d f=%d\n",
                  g_farm.travessias_completas_feitas, g_farm.raposas_direita, g_farm.ovelhas_direita,
                  g_farm.fazendeiros_direita);

        if (simulacao_terminou()) {
            g_farm.simulacao_ativa = 0;
        }

        pthread_cond_broadcast(&g_cond_viagem);
        pthread_cond_broadcast(&g_cond_embarque);
    } else {
        pthread_cond_wait(&g_cond_viagem, &g_mutex);
    }

    visor_log("[Desembarque] %s %d cruzou o rio com seguranca\n", tipo_nome(tipo), id);

    pthread_mutex_unlock(&g_mutex);
    free(p);
    return NULL;
}
