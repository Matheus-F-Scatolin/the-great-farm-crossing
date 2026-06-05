CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -pthread -Isrc
LDFLAGS = -lm
TARGET = farm_crossing
SRCS = src/main.c src/farm.c src/threads.c src/visor_ipc.c
OBJS = $(SRCS:.c=.o)

.PHONY: all clean run

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $(OBJS) $(LDFLAGS)

src/%.o: src/%.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

run: all
	./run.sh

