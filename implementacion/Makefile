#---------------------------- Sección de declaraciones ----------------------------

CFLAGS=-g -Wall -Wextra -Wpedantic -I./includes
BFLAGS=
# BFLAGS=-t #-t = permite debuggear y ver trazas

HEADERS=./includes/Codigo.hpp ./includes/Atributos.hpp
SOURCES=./src/parser.cpp ./src/main.cpp ./src/tokens.cpp ./src/Codigo.cpp

CPP = g++
LEX = flex
YACC = bison

TESTS=tests

#---------------------------- Sección de reglas para construir y compilar ----------------------------

.PHONY: all clean

all: parser

clean:
	$(RM) ./src/parser.cpp ./includes/parser.hpp ./bin/parser ./src/tokens.cpp

#Tasks para BISON
parser.cpp: ./$(YACC)/parser.y $(HEADERS)
	$(YACC) $(BFLAGS) -d -o $@ $<
	mv ./parser.cpp ./src/
	mv ./parser.hpp ./includes/

parser.hpp: parser.cpp

#Tasks para LEX
tokens.cpp: ./$(LEX)/tokens.l parser.hpp $(HEADERS)
	$(LEX) -o $@ $< ./includes/parser.hpp
	mv $@ ./src/

#Tasks para el programa principal
parser: parser.cpp tokens.cpp $(SOURCES) $(HEADERS)
	$(CPP) $(CFLAGS) -o $@ ./src/*.cpp
	mv $@ ./bin/
