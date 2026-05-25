#ifndef THREADS_H
#define THREADS_H

#include "farm.h"

typedef struct {
    int id;
    TipoPassageiro tipo;
} PassageiroArg;

void *passageiro_thread(void *arg);

#endif
