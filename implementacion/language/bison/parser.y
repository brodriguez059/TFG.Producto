/*Verbose error messages*/
%define parse.error verbose

%{
   #include <stdio.h>
   #include <iostream>
   #include <vector>
   #include <string>

   using namespace std;

   extern int yylex();
   extern int yylineno;
   extern char *yytext;

   int errores = 0;

   void yyerror (const char *msg) {
     printf("Línea %d: %s. Causado al leer el símbolo '%s'\n", yylineno, msg, yytext) ;
     errores++;
   }
   #include "Atributos.hpp"


   /*-------------Sección de variables globales-------------*/
   int i; // Para iterar

   /*-------------Fin sección de variables globales-------------*/
%}

%union {
    string *str ;
    int number ;
}

%token <str> ROPTION
%token <str> RIN, RCOUNT, RSTATE
%token <str> RMETRIC, REVENT, RSTOP

%token <str> TLBRACE, TRBRACE
%token <str> TLPAREN, TRPAREN
%token <str> TPERCENT
%token <str> TCOMMA, TDOT, TDOUBLEDOT
%token <str> TASSIG
%token <str> TPLUS, TMINUS, TMUL, TPOW, TDIV, TINTDIV
%token <str> TCGT, TCLT, TCGE, TCLE, TCEQ, TCNE

%%

// Grammar section

%%

// C++ code section