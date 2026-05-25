#ifndef VISOR_IPC_H
#define VISOR_IPC_H

#include "farm.h"

void visor_emit_chegou(TipoPassageiro tipo, int id);
void visor_emit_embarque(TipoPassageiro tipo, int id);
void visor_emit_partida(void);
void visor_emit_atracou(void);
void visor_emit_desembarque(TipoPassageiro tipo, int id);
void visor_emit_retorno(void);
void visor_emit_fim(void);
void visor_log(const char *fmt, ...);

void atravessar_rio(int leader_id, int trip_r, int trip_o, int trip_f);

#endif
