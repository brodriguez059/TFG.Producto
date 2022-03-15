%option yylineno
%option nounput

%{
 #include <string>
 #include <iostream>
 #include <vector>
 using namespace std;
 #include "Atributos.hpp"
 #include "parser.hpp"

 #define TOKEN(t) yylval.str = new string(yytext, yyleng) ; return t

 extern "C" int yywrap() { return(1) ; }

%}

%%

"option"                                    TOKEN(ROPTION);

"in"                                        TOKEN(RIN);

"count"                                     TOKEN(RCOUNT);

"state"                                     TOKEN(RSTATE);

"Metric"                                    TOKEN(RMETRIC);

"Event"                                     TOKEN(REVENT);

"Stop"                                      TOKEN(RSTOP);

"{"                                         TOKEN(TLBRACE);

"}"                                         TOKEN(TRBRACE);

"("                                         TOKEN(TLPAREN);

")"                                         TOKEN(TRPAREN);

","                                         TOKEN(TCOMMA);

"."                                         TOKEN(TDOT);

":"                                         TOKEN(TDOUBLEDOT);

"%"                                         TOKEN(TPERCENT);

"="                                         TOKEN(TASSIG);

"+"                                         TOKEN(TPLUS);

"-"                                         TOKEN(TMINUS);

"*"                                         TOKEN(TMUL);

"**"                                        TOKEN(TPOW);

"/"                                         TOKEN(TDIV);

"//"                                        TOKEN(TINTDIV);

">"                                         TOKEN(TCGT);

"<"                                         TOKEN(TCLT);

">="                                        TOKEN(TCGE);

"<="                                        TOKEN(TCLE);

"=="                                        TOKEN(TCEQ);

"/="                                        TOKEN(TCNE);

.                                           { cout << "Token desconocido: " << yytext << endl; yyterminate();}

%%

/* C++ code */