#include "farm.h"

#include <string.h>

FarmState g_farm;
pthread_mutex_t g_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t g_cond_embarque = PTHREAD_COND_INITIALIZER;
pthread_cond_t g_cond_viagem = PTHREAD_COND_INITIALIZER;
SimConfig g_config;

int combinacao_valida(int r, int o, int f) {
    int total = r + o + f;
    if (total != 3) {
        return 0;
    }
    if (r == 3) {
        return 1;
    }
    if (o == 3) {
        return 1;
    }
    if (f == 3) {
        return 1;
    }
    if ((f == 1 || f == 2) && (r > 0 || o > 0)) {
        return 1;
    }
    return 0;
}

static int combo_disponivel(const FarmState *s, int r, int o, int f) {
    if (s->barco_ocupacao != 0 || s->barco_lado != LADO_ESQUERDA) {
        return 0;
    }
    if (s->raposas_fila < r || s->ovelhas_fila < o || s->fazendeiros_fila < f) {
        return 0;
    }
    return combinacao_valida(r, o, f);
}

int escolher_combo(const FarmState *s, int *r, int *o, int *f) {
    static const int combos[][3] = {
        {3, 0, 0}, {0, 3, 0}, {0, 0, 3},
        {0, 1, 2}, {1, 0, 2},
        {0, 2, 1}, {2, 0, 1},
        {1, 1, 1},
    };
    size_t i;
    for (i = 0; i < sizeof(combos) / sizeof(combos[0]); i++) {
        if (combo_disponivel(s, combos[i][0], combos[i][1], combos[i][2])) {
            *r = combos[i][0];
            *o = combos[i][1];
            *f = combos[i][2];
            return 1;
        }
    }
    return 0;
}

void aplicar_combo(FarmState *s, int r, int o, int f) {
    s->raposas_fila -= r;
    s->ovelhas_fila -= o;
    s->fazendeiros_fila -= f;
    s->raposas_barco = r;
    s->ovelhas_barco = o;
    s->fazendeiros_barco = f;
    s->barco_ocupacao = 3;
    s->boarded_r = 0;
    s->boarded_o = 0;
    s->boarded_f = 0;
    s->trip_boarded = 0;
}

int farm_pode_formar_combo(const FarmState *s) {
    int r, o, f;
    return escolher_combo(s, &r, &o, &f);
}

int farm_slots_disponiveis_tipo(TipoPassageiro tipo) {
    if (g_farm.barco_ocupacao != 3) {
        return 0;
    }
    switch (tipo) {
    case TIPO_RAPOSA:
        return g_farm.raposas_barco - g_farm.boarded_r;
    case TIPO_OVELHA:
        return g_farm.ovelhas_barco - g_farm.boarded_o;
    case TIPO_FAZENDEIRO:
        return g_farm.fazendeiros_barco - g_farm.boarded_f;
    }
    return 0;
}

int farm_claim_slot(FarmState *s, TipoPassageiro tipo) {
    switch (tipo) {
    case TIPO_RAPOSA:
        if (s->boarded_r >= s->raposas_barco) {
            return 0;
        }
        s->boarded_r++;
        break;
    case TIPO_OVELHA:
        if (s->boarded_o >= s->ovelhas_barco) {
            return 0;
        }
        s->boarded_o++;
        break;
    case TIPO_FAZENDEIRO:
        if (s->boarded_f >= s->fazendeiros_barco) {
            return 0;
        }
        s->boarded_f++;
        break;
    }
    s->trip_boarded++;
    return 1;
}

const char *tipo_nome(TipoPassageiro tipo) {
    switch (tipo) {
    case TIPO_RAPOSA:
        return "RAPOSA";
    case TIPO_OVELHA:
        return "OVELHA";
    case TIPO_FAZENDEIRO:
        return "FAZENDEIRO";
    }
    return "DESCONHECIDO";
}

void farm_init(SimConfig *cfg) {
    g_config = *cfg;
    memset(&g_farm, 0, sizeof(g_farm));
    g_farm.barco_lado = LADO_ESQUERDA;
    g_farm.simulacao_ativa = 1;
    g_farm.total_raposas = cfg->raposas;
    g_farm.total_ovelhas = cfg->ovelhas;
    g_farm.total_fazendeiros = cfg->fazendeiros;
    g_farm.pendentes_chegada = cfg->raposas + cfg->ovelhas + cfg->fazendeiros;
}

int farm_fila_total(const FarmState *s) {
    return s->raposas_fila + s->ovelhas_fila + s->fazendeiros_fila;
}

int farm_deadlock(const FarmState *s) {
    if (s->barco_ocupacao != 0 || s->barco_lado != LADO_ESQUERDA) {
        return 0;
    }
    if (s->pendentes_chegada > 0) {
        return 0;
    }
    if (farm_fila_total(s) == 0) {
        return 0;
    }
    return !farm_pode_formar_combo(s);
}
