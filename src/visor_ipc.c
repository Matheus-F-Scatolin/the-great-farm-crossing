#include "visor_ipc.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

static long long visor_ts_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000LL + ts.tv_nsec / 1000000LL;
}

static const char *lado_str(LadoBarco lado) {
    return lado == LADO_ESQUERDA ? "ESQUERDA" : "DIREITA";
}

static void emit_json_ex(const char *evt, TipoPassageiro who, int id, int dur_ms) {
    if (g_config.no_vis) {
        return;
    }
    /* Eventos globais (PARTIDA, FIM, …) usam id < 0 e omitem o campo who. */
    const char *who_str = (who == TIPO_RAPOSA || who == TIPO_OVELHA || who == TIPO_FAZENDEIRO) ? tipo_nome(who) : "";
    if (dur_ms > 0) {
        printf(
            "{\"evt\":\"%s\",\"who\":\"%s\",\"id\":%d,\"dur_ms\":%d,"
            "\"fila\":{\"r\":%d,\"o\":%d,\"f\":%d},"
            "\"barco\":{\"r\":%d,\"o\":%d,\"f\":%d,\"lado\":\"%s\",\"ocupacao\":%d},"
            "\"direita\":{\"r\":%d,\"o\":%d,\"f\":%d},"
            "\"cruzes\":%d,\"ts\":%lld}\n",
            evt, who_str, id, dur_ms, g_farm.raposas_fila, g_farm.ovelhas_fila,
            g_farm.fazendeiros_fila, g_farm.raposas_barco, g_farm.ovelhas_barco,
            g_farm.fazendeiros_barco, lado_str(g_farm.barco_lado), g_farm.barco_ocupacao,
            g_farm.raposas_direita, g_farm.ovelhas_direita, g_farm.fazendeiros_direita,
            g_farm.cruzes_feitas, visor_ts_ms());
    } else {
        printf(
            "{\"evt\":\"%s\",\"who\":\"%s\",\"id\":%d,"
            "\"fila\":{\"r\":%d,\"o\":%d,\"f\":%d},"
            "\"barco\":{\"r\":%d,\"o\":%d,\"f\":%d,\"lado\":\"%s\",\"ocupacao\":%d},"
            "\"direita\":{\"r\":%d,\"o\":%d,\"f\":%d},"
            "\"cruzes\":%d,\"ts\":%lld}\n",
            evt, who_str, id, g_farm.raposas_fila, g_farm.ovelhas_fila, g_farm.fazendeiros_fila,
            g_farm.raposas_barco, g_farm.ovelhas_barco, g_farm.fazendeiros_barco,
            lado_str(g_farm.barco_lado), g_farm.barco_ocupacao, g_farm.raposas_direita,
            g_farm.ovelhas_direita, g_farm.fazendeiros_direita, g_farm.cruzes_feitas,
            visor_ts_ms());
    }
    fflush(stdout);
}

static void emit_json(const char *evt, TipoPassageiro who, int id) {
    emit_json_ex(evt, who, id, 0);
}

void visor_emit_chegou(TipoPassageiro tipo, int id) { emit_json("CHEGOU", tipo, id); }

void visor_emit_embarque(TipoPassageiro tipo, int id) { emit_json("EMBARQUE", tipo, id); }

void visor_emit_partida(void) { emit_json_ex("PARTIDA", -1, -1, g_config.boat_speed_ms); }

void visor_emit_atracou(void) { emit_json("ATRACOU", -1, -1); }

void visor_emit_desembarque(TipoPassageiro tipo, int id) { emit_json("DESEMBARQUE", tipo, id); }

void visor_emit_retorno(void) { emit_json_ex("RETORNO", -1, -1, g_config.return_ms); }

void visor_emit_fim(void) { emit_json("FIM", -1, -1); }

void visor_log(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
}

static void sleep_ms(int ms) {
    if (ms > 0) {
        usleep((useconds_t)ms * 1000);
    }
}

/*
 * Simula a viagem do lider: emite JSON para o visualizador Pygame (stdout).
 * Atualiza barco_lado; contadores da margem direita sao aplicados pelo lider em threads.c.
 */
void atravessar_rio(int leader_id, int trip_r, int trip_o, int trip_f) {
    (void)leader_id;
    visor_log("[Lider] Iniciando travessia (%d raposas, %d ovelhas, %d fazendeiros)\n", trip_r,
              trip_o, trip_f);

    visor_emit_partida();
    sleep_ms(g_config.boat_speed_ms);

    g_farm.barco_lado = LADO_DIREITA;
    visor_emit_atracou();
    sleep_ms(g_config.embark_ms);

    int i;
    for (i = 0; i < trip_r; i++) {
        visor_emit_desembarque(TIPO_RAPOSA, -1);
        sleep_ms(g_config.embark_ms);
    }
    for (i = 0; i < trip_o; i++) {
        visor_emit_desembarque(TIPO_OVELHA, -1);
        sleep_ms(g_config.embark_ms);
    }
    for (i = 0; i < trip_f; i++) {
        visor_emit_desembarque(TIPO_FAZENDEIRO, -1);
        sleep_ms(g_config.embark_ms);
    }

    visor_emit_retorno();
    sleep_ms(g_config.return_ms);
    g_farm.barco_lado = LADO_ESQUERDA;

    visor_log("[Lider] Travessia concluida\n");
}
