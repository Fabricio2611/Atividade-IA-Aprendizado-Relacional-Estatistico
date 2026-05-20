
% ------------------------------------------------------------
% Fatos: transacao_entre(Origem, Destino, Valor).
% ------------------------------------------------------------
transacao_entre(joao, ana, 1500).
transacao_entre(ana, carlos, 800).
transacao_entre(carlos, daniel, 50).
transacao_entre(maria, joao, 300).
transacao_entre(beatriz, maria, 700).
transacao_entre(lucas, ana, 1200).
transacao_entre(renata, lucas, 450).
transacao_entre(paulo, beatriz, 220).
transacao_entre(sofia, paulo, 900).
transacao_entre(marcos, sofia, 120).
transacao_entre(laura, renata, 650).
transacao_entre(rafael, laura, 340).
transacao_entre(fernanda, rafael, 210).
transacao_entre(gabriel, fernanda, 890).
transacao_entre(isabela, gabriel, 100).
transacao_entre(henrique, isabela, 410).

% ------------------------------------------------------------
% Histórico clássico de inadimplência.
% ------------------------------------------------------------
inadimplente(daniel).
inadimplente(carlos).
inadimplente(rafael).

% ------------------------------------------------------------
% Conexão não direcionada: se A transacionou com B, há ligação entre eles.
% ------------------------------------------------------------
conectado_direto(X, Y) :- transacao_entre(X, Y, _).
conectado_direto(X, Y) :- transacao_entre(Y, X, _).

% ------------------------------------------------------------
% Caminho recursivo sem ciclos.
% caminho(Origem, Destino, Visitados, Grau).
% ------------------------------------------------------------
caminho(X, Y, _, 1) :-
    conectado_direto(X, Y).

caminho(X, Y, Visitados, Grau) :-
    conectado_direto(X, Z),
    Z \= Y,
    \+ member(Z, Visitados),
    caminho(Z, Y, [Z|Visitados], GrauAnterior),
    Grau is GrauAnterior + 1.

% ------------------------------------------------------------
% risco_conexao(X, Y, Grau)
% Calcula o menor grau de proximidade entre X e Y.
% ------------------------------------------------------------
risco_conexao(X, Y, Grau) :-
    setof(G, caminho(X, Y, [X], G), Graus),
    Graus = [Grau|_].

% ------------------------------------------------------------
% risco_com_inadimplente(Cliente, Inadimplente, Grau)
% Retorna a menor conexão do cliente com qualquer inadimplente conhecido.
% ------------------------------------------------------------
risco_com_inadimplente(Cliente, PessoaRisco, Grau) :-
    inadimplente(PessoaRisco),
    Cliente \= PessoaRisco,
    risco_conexao(Cliente, PessoaRisco, Grau).
