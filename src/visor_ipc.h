#ifndef VISOR_IPC_H
#define VISOR_IPC_H

#include "farm.h"

/*
 * Protocolo de comunicacao C -> visualizador Pygame.
 * Cada funcao visor_emit_* escreve uma linha JSON em stdout.
 * visor_log() escreve mensagens de depuracao em stderr.
 */

void visor_emit_chegou(TipoPassageiro tipo, int id);     /* Passageiro entrou na fila.        */
void visor_emit_embarque(TipoPassageiro tipo, int id);   /* Passageiro subiu no barco.        */
void visor_emit_partida(void);                           /* Barco partiu da margem esquerda.  */
void visor_emit_atracou(void);                           /* Barco atracou na margem direita.  */
void visor_emit_desembarque(TipoPassageiro tipo, int id);/* Passageiro desceu na direita.     */
void visor_emit_retorno(void);                           /* Barco retornando vazio.           */
void visor_emit_fim(void);                               /* Simulacao encerrada.              */
void visor_log(const char *fmt, ...);                    /* Printf para stderr (depuracao).   */

/* Realiza a travessia completa (partida, atracagem, desembarques, retorno). */
void atravessar_rio(int leader_id, int trip_r, int trip_o, int trip_f);

#endif
