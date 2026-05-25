#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "farm.h"
#include "threads.h"
#include "visor_ipc.h"

static void print_usage(const char *prog) {
    fprintf(stderr,
            "Uso: %s [opcoes]\n"
            "  --raposas N           Numero de raposas (default %d)\n"
            "  --ovelhas N           Numero de ovelhas (default %d)\n"
            "  --fazendeiros N       Numero de fazendeiros (default %d)\n"
            "  --lambda-raposa F     Taxa de chegada raposas (default %.1f)\n"
            "  --lambda-ovelha F     Taxa de chegada ovelhas (default %.1f)\n"
            "  --lambda-fazendeiro F Taxa de chegada fazendeiros (default %.1f)\n"
            "  --seed N              Semente aleatoria (default %u)\n"
            "  --boat-speed-ms N     Duracao da travessia em ms (default %d)\n"
            "  --embark-ms N         Pausa entre embarques/desembarques (default %d)\n"
            "  --return-ms N         Duracao do retorno vazio (default %d)\n"
            "  --max-cruzes N        Limite de viagens (0=sem limite, default %d)\n"
            "  --no-vis              Desliga JSON no stdout (logs em stderr)\n",
            prog, DEFAULT_RAPOSAS, DEFAULT_OVELHAS, DEFAULT_FAZENDEIROS, DEFAULT_LAMBDA_RAPOSA,
            DEFAULT_LAMBDA_OVELHA, DEFAULT_LAMBDA_FAZENDEIRO, DEFAULT_SEED, DEFAULT_BOAT_SPEED_MS,
            DEFAULT_EMBARK_MS, DEFAULT_RETURN_MS, DEFAULT_MAX_CRUZES);
}

static int parse_args(int argc, char **argv, SimConfig *cfg) {
    static struct option long_opts[] = {
        {"raposas", required_argument, 0, 'r'},
        {"ovelhas", required_argument, 0, 'o'},
        {"fazendeiros", required_argument, 0, 'f'},
        {"lambda-raposa", required_argument, 0, 1000},
        {"lambda-ovelha", required_argument, 0, 1001},
        {"lambda-fazendeiro", required_argument, 0, 1002},
        {"seed", required_argument, 0, 's'},
        {"boat-speed-ms", required_argument, 0, 1003},
        {"embark-ms", required_argument, 0, 1004},
        {"return-ms", required_argument, 0, 1005},
        {"max-cruzes", required_argument, 0, 1006},
        {"no-vis", no_argument, 0, 1007},
        {"help", no_argument, 0, 'h'},
        {0, 0, 0, 0},
    };

    int opt;
    while ((opt = getopt_long(argc, argv, "", long_opts, NULL)) != -1) {
        switch (opt) {
        case 'r':
            cfg->raposas = atoi(optarg);
            break;
        case 'o':
            cfg->ovelhas = atoi(optarg);
            break;
        case 'f':
            cfg->fazendeiros = atoi(optarg);
            break;
        case 1000:
            cfg->lambda_raposa = atof(optarg);
            break;
        case 1001:
            cfg->lambda_ovelha = atof(optarg);
            break;
        case 1002:
            cfg->lambda_fazendeiro = atof(optarg);
            break;
        case 's':
            cfg->seed = (unsigned int)strtoul(optarg, NULL, 10);
            break;
        case 1003:
            cfg->boat_speed_ms = atoi(optarg);
            break;
        case 1004:
            cfg->embark_ms = atoi(optarg);
            break;
        case 1005:
            cfg->return_ms = atoi(optarg);
            break;
        case 1006:
            cfg->max_cruzes = atoi(optarg);
            break;
        case 1007:
            cfg->no_vis = 1;
            break;
        case 'h':
            print_usage(argv[0]);
            return 0;
        default:
            print_usage(argv[0]);
            return -1;
        }
    }
    return 1;
}

int main(int argc, char **argv) {
    SimConfig cfg;
    config_init_defaults(&cfg);

    int parsed = parse_args(argc, argv, &cfg);
    if (parsed <= 0) {
        return parsed == 0 ? 0 : 1;
    }

    if (cfg.raposas < 0 || cfg.ovelhas < 0 || cfg.fazendeiros < 0) {
        fprintf(stderr, "Contagens devem ser >= 0\n");
        return 1;
    }

    srand(cfg.seed);
    farm_init(&cfg);

    int total = cfg.raposas + cfg.ovelhas + cfg.fazendeiros;
    pthread_t *threads = calloc((size_t)total, sizeof(pthread_t));
    if (!threads) {
        perror("calloc");
        return 1;
    }

    visor_log("Iniciando simulacao: %d raposas, %d ovelhas, %d fazendeiros (seed=%u)\n",
              cfg.raposas, cfg.ovelhas, cfg.fazendeiros, cfg.seed);

    int next_id = 0;
    int t;
    for (t = 0; t < cfg.raposas; t++) {
        PassageiroArg *arg = malloc(sizeof(PassageiroArg));
        arg->id = next_id++;
        arg->tipo = TIPO_RAPOSA;
        pthread_create(&threads[t], NULL, passageiro_thread, arg);
    }
    int offset = cfg.raposas;
    for (t = 0; t < cfg.ovelhas; t++) {
        PassageiroArg *arg = malloc(sizeof(PassageiroArg));
        arg->id = next_id++;
        arg->tipo = TIPO_OVELHA;
        pthread_create(&threads[offset + t], NULL, passageiro_thread, arg);
    }
    offset += cfg.ovelhas;
    for (t = 0; t < cfg.fazendeiros; t++) {
        PassageiroArg *arg = malloc(sizeof(PassageiroArg));
        arg->id = next_id++;
        arg->tipo = TIPO_FAZENDEIRO;
        pthread_create(&threads[offset + t], NULL, passageiro_thread, arg);
    }

    for (t = 0; t < total; t++) {
        pthread_join(threads[t], NULL);
    }

    visor_log("Simulacao finalizada. Cruzes: %d\n", g_farm.cruzes_feitas);
    if (!cfg.no_vis) {
        visor_emit_fim();
    }

    free(threads);
    return 0;
}
