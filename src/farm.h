#ifndef FARM_H
#define FARM_H

#include <pthread.h>

#include "config.h"

typedef enum { LADO_ESQUERDA, LADO_DIREITA } LadoBarco;           /* Margem atual do barco.  */
typedef enum { TIPO_RAPOSA, TIPO_OVELHA, TIPO_FAZENDEIRO } TipoPassageiro; /* Tipo de thread. */

/* Estado compartilhado protegido por g_mutex (fila esquerda, barco, margem direita). */
typedef struct {
    /* Contadores da fila de espera na margem esquerda. */
    int raposas_fila;
    int ovelhas_fila;
    int fazendeiros_fila;
    /* Quantos de cada tipo foram reservados para a viagem atual. */
    int raposas_barco;
    int ovelhas_barco;
    int fazendeiros_barco;
    /* Quantos ja desembarcaram na margem direita (acumulado). */
    int raposas_direita;
    int ovelhas_direita;
    int fazendeiros_direita;
    int barco_ocupacao;              /* 0 = vazio, 3 = combo reservado.              */
    LadoBarco barco_lado;            /* Em qual margem o barco esta.                 */
    int travessias_completas_feitas;
    int simulacao_ativa;             /* 0 quando deadlock ou fim detectado.           */
    int trip_leader_id;              /* ID da thread lider da viagem atual.           */
    int trip_boarded;                /* Quantos ja embarcaram fisicamente (0..3).     */
    int boarded_r;                   /* Slots ja reivindicados por raposas.           */
    int boarded_o;
    int boarded_f;
    int trip_disembarked;            /* Quantos ja desembarcaram nesta viagem (0..3). */
    /* Totais configurados (imutaveis apos farm_init). */
    int total_raposas;
    int total_ovelhas;
    int total_fazendeiros;
    int pendentes_chegada;           /* Threads que ainda nao nasceram.               */
} FarmState;

extern FarmState g_farm;
extern pthread_mutex_t g_mutex;
extern pthread_cond_t g_cond_embarque;
extern pthread_cond_t g_cond_viagem;
/* Seguidores sinalizam ao lider que ja desembarcaram, antes de liberar o barco. */
extern pthread_cond_t g_cond_desembarque;
extern SimConfig g_config;

/* Retorna 1 se (r,o,f) formam um combo seguro de 3 passageiros. */
int combinacao_valida(int r, int o, int f);
/* Tenta encontrar o primeiro combo valido a partir da fila; preenche r,o,f. */
int escolher_combo(const FarmState *s, int *r, int *o, int *f);
/* Move passageiros da fila para o barco conforme o combo escolhido. */
void aplicar_combo(FarmState *s, int r, int o, int f);
/* Predicado rapido: existe algum combo viavel agora? */
int farm_pode_formar_combo(const FarmState *s);
/* Quantos slots ainda nao reivindicados existem para `tipo` na viagem atual. */
int farm_slots_disponiveis_tipo(TipoPassageiro tipo);
/* Reivindica 1 slot para `tipo`; retorna 1 se obteve, 0 se lotado. */
int farm_claim_slot(FarmState *s, TipoPassageiro tipo);
const char *tipo_nome(TipoPassageiro tipo);
/* Soma total de threads na fila esquerda. */
int farm_fila_total(const FarmState *s);
/* Retorna 1 se nenhum combo pode ser formado e ninguem mais vai chegar. */
int farm_deadlock(const FarmState *s);
/* Zera o estado global e aplica a configuracao recebida. */
void farm_init(SimConfig *cfg);

#endif
