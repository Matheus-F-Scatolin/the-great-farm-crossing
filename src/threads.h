#ifndef THREADS_H
#define THREADS_H

#include "farm.h"

/* Argumento passado para cada thread criada em main.c (alocado no heap). */
typedef struct {
    int id;              /* Identificador unico do passageiro.                */
    TipoPassageiro tipo; /* Raposa, ovelha ou fazendeiro.                     */
} PassageiroArg;

/* Ciclo de vida completo de um passageiro (chegada -> fila -> embarque -> travessia). */
void *passageiro_thread(void *arg);

#endif
