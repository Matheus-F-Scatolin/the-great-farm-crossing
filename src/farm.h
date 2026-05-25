#ifndef FARM_H
#define FARM_H

#include <pthread.h>

#include "config.h"

typedef enum { LADO_ESQUERDA, LADO_DIREITA } LadoBarco;
typedef enum { TIPO_RAPOSA, TIPO_OVELHA, TIPO_FAZENDEIRO } TipoPassageiro;

typedef struct {
    int raposas_fila;
    int ovelhas_fila;
    int fazendeiros_fila;
    int raposas_barco;
    int ovelhas_barco;
    int fazendeiros_barco;
    int raposas_direita;
    int ovelhas_direita;
    int fazendeiros_direita;
    int barco_ocupacao;
    LadoBarco barco_lado;
    int cruzes_feitas;
    int simulacao_ativa;
    int trip_leader_id;
    int trip_boarded;
    int boarded_r;
    int boarded_o;
    int boarded_f;
    int total_raposas;
    int total_ovelhas;
    int total_fazendeiros;
    int pendentes_chegada;
} FarmState;

extern FarmState g_farm;
extern pthread_mutex_t g_mutex;
extern pthread_cond_t g_cond_embarque;
extern pthread_cond_t g_cond_viagem;
extern SimConfig g_config;

int combinacao_valida(int r, int o, int f);
int escolher_combo(const FarmState *s, int *r, int *o, int *f);
void aplicar_combo(FarmState *s, int r, int o, int f);
int farm_pode_formar_combo(const FarmState *s);
int farm_slots_disponiveis_tipo(TipoPassageiro tipo);
int farm_claim_slot(FarmState *s, TipoPassageiro tipo);
const char *tipo_nome(TipoPassageiro tipo);
int farm_fila_total(const FarmState *s);
int farm_deadlock(const FarmState *s);
void farm_init(SimConfig *cfg);

#endif
