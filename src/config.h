#ifndef CONFIG_H
#define CONFIG_H

typedef struct {
    int raposas;
    int ovelhas;
    int fazendeiros;
    double lambda_raposa;
    double lambda_ovelha;
    double lambda_fazendeiro;
    unsigned int seed;
    int boat_speed_ms;
    int embark_ms;
    int return_ms;
    int max_travessias_completas;
    int no_vis;
} SimConfig;

#define DEFAULT_RAPOSAS 6
#define DEFAULT_OVELHAS 9
#define DEFAULT_FAZENDEIROS 3
#define DEFAULT_LAMBDA_RAPOSA 0.5
#define DEFAULT_LAMBDA_OVELHA 0.4
#define DEFAULT_LAMBDA_FAZENDEIRO 0.3
#define DEFAULT_SEED 42u
#define DEFAULT_BOAT_SPEED_MS 1200
#define DEFAULT_EMBARK_MS 200
#define DEFAULT_RETURN_MS 800
#define DEFAULT_MAX_TRAVESSIAS_COMPLETAS 0

static inline void config_init_defaults(SimConfig *cfg) {
    cfg->raposas = DEFAULT_RAPOSAS;
    cfg->ovelhas = DEFAULT_OVELHAS;
    cfg->fazendeiros = DEFAULT_FAZENDEIROS;
    cfg->lambda_raposa = DEFAULT_LAMBDA_RAPOSA;
    cfg->lambda_ovelha = DEFAULT_LAMBDA_OVELHA;
    cfg->lambda_fazendeiro = DEFAULT_LAMBDA_FAZENDEIRO;
    cfg->seed = DEFAULT_SEED;
    cfg->boat_speed_ms = DEFAULT_BOAT_SPEED_MS;
    cfg->embark_ms = DEFAULT_EMBARK_MS;
    cfg->return_ms = DEFAULT_RETURN_MS;
    cfg->max_travessias_completas = DEFAULT_MAX_TRAVESSIAS_COMPLETAS;
    cfg->no_vis = 0;
}

#endif
