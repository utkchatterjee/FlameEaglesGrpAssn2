% ============================================================
% Royal Archive Access Verification
% Resolution Refutation in First-Order Logic
% Run in SWI-Prolog:  ?- [royal_archive_access].  ?- run.
% ============================================================

:- dynamic kb/3.   % kb(Id, Clause, Parents): the clauses known so far

% Step 1: Predicate logic representation
% Predicates : archivist/1, verifies/2, trusted/1, access/2, sealed/1,
%              permitted/2, inspects/2, finds_mark/2, stored_in_archive/1
% Constants  : mira, scroll_7          Variables : X (person), R (record)
% 1. Every archivist who verifies a record is trusted.
% 2. Every trusted person with access to a sealed record may inspect it.
% 3. Anyone who inspects a record and finds a hidden mark in it verifies it.
% 4. Every record stored in the royal archive is sealed.
% 5-8. Facts about scroll_7 and Mira.
% Goal: Mira is trusted.

predicate_logic([
  forall(X, forall(R, implies(and(archivist(X), verifies(X, R)), trusted(X)))),
  forall(X, forall(R, implies(and(trusted(X), and(access(X, R), sealed(R))), permitted(X, R)))),
  forall(X, forall(R, implies(and(inspects(X, R), finds_mark(X, R)), verifies(X, R)))),
  forall(R, implies(stored_in_archive(R), sealed(R))),
  stored_in_archive(scroll_7),
  access(mira, scroll_7),
  and(inspects(mira, scroll_7), finds_mark(mira, scroll_7)),
  archivist(mira)
]).
goal(trusted(mira)).

% Step 2: Negation of goal
% Assume Mira is NOT trusted; we will show this leads to a contradiction
negated_goal(not(trusted(mira))).

% Step 3: Implication removal
% Apply rule: (P -> Q) is equivalent to (not(P) v Q)
no_implications([
  forall(X, forall(R, or(not(and(archivist(X), verifies(X, R))), trusted(X)))),
  forall(X, forall(R, or(not(and(trusted(X), and(access(X, R), sealed(R)))), permitted(X, R)))),
  forall(X, forall(R, or(not(and(inspects(X, R), finds_mark(X, R))), verifies(X, R)))),
  forall(R, or(not(stored_in_archive(R)), sealed(R))),
  stored_in_archive(scroll_7),
  access(mira, scroll_7),
  and(inspects(mira, scroll_7), finds_mark(mira, scroll_7)),
  archivist(mira),
  not(trusted(mira))
]).

% Step 4: Negation movement
% De Morgan: not(A and B) = not(A) or not(B), so negations sit on atoms (NNF)
negation_normal_form([
  forall(X, forall(R, or(or(not(archivist(X)), not(verifies(X, R))), trusted(X)))),
  forall(X, forall(R, or(or(not(trusted(X)), or(not(access(X, R)), not(sealed(R)))), permitted(X, R)))),
  forall(X, forall(R, or(or(not(inspects(X, R)), not(finds_mark(X, R))), verifies(X, R)))),
  forall(R, or(not(stored_in_archive(R)), sealed(R))),
  stored_in_archive(scroll_7),
  access(mira, scroll_7),
  and(inspects(mira, scroll_7), finds_mark(mira, scroll_7)),
  archivist(mira),
  not(trusted(mira))
]).

% Step 5: Standardization
% Every quantifier gets its own variable names (X1,R1 / X2,R2 / ...)
standardized([
  forall(X1, forall(R1, or(or(not(archivist(X1)), not(verifies(X1, R1))), trusted(X1)))),
  forall(X2, forall(R2, or(or(not(trusted(X2)), or(not(access(X2, R2)), not(sealed(R2)))), permitted(X2, R2)))),
  forall(X3, forall(R3, or(or(not(inspects(X3, R3)), not(finds_mark(X3, R3))), verifies(X3, R3)))),
  forall(R4, or(not(stored_in_archive(R4)), sealed(R4))),
  stored_in_archive(scroll_7),
  access(mira, scroll_7),
  and(inspects(mira, scroll_7), finds_mark(mira, scroll_7)),
  archivist(mira),
  not(trusted(mira))
]).

% Step 6: Skolemization
% There are no existential quantifiers, so no Skolem functions are needed
skolemized([
  forall(X1, forall(R1, or(or(not(archivist(X1)), not(verifies(X1, R1))), trusted(X1)))),
  forall(X2, forall(R2, or(or(not(trusted(X2)), or(not(access(X2, R2)), not(sealed(R2)))), permitted(X2, R2)))),
  forall(X3, forall(R3, or(or(not(inspects(X3, R3)), not(finds_mark(X3, R3))), verifies(X3, R3)))),
  forall(R4, or(not(stored_in_archive(R4)), sealed(R4))),
  stored_in_archive(scroll_7),
  access(mira, scroll_7),
  and(inspects(mira, scroll_7), finds_mark(mira, scroll_7)),
  archivist(mira),
  not(trusted(mira))
]).

% Step 7: CNF clauses
% Drop quantifiers (all variables are universal); split the conjunction
% in fact 7 into two unit clauses. Each clause is a list of literals.
cnf_clauses([
  [not(archivist(X1)), not(verifies(X1, R1)), trusted(X1)],                 % rule 1
  [not(trusted(X2)), not(access(X2, R2)), not(sealed(R2)), permitted(X2, R2)], % rule 2
  [not(inspects(X3, R3)), not(finds_mark(X3, R3)), verifies(X3, R3)],       % rule 3
  [not(stored_in_archive(R4)), sealed(R4)],                                 % rule 4
  [stored_in_archive(scroll_7)],                                            % fact 5
  [access(mira, scroll_7)],                                                 % fact 6
  [inspects(mira, scroll_7)],                                               % fact 7a
  [finds_mark(mira, scroll_7)],                                             % fact 7b
  [archivist(mira)],                                                        % fact 8
  [not(trusted(mira))]                                                      % negated goal
]).

% Step 8: Resolution implementation and execution

% Two literals are complementary if one is the negation of the other
% (Prolog unification binds the variables, i.e. it finds the unifier)
complementary(not(Literal), Literal).
complementary(Literal, not(Literal)).

% resolve(+C1, +C2, -Resolvent): resolve two clauses on one complementary pair.
% copy_term renames variables apart so clauses can be reused many times.
resolve(Clause1, Clause2, Resolvent) :-
  copy_term(Clause1, A),
  copy_term(Clause2, B),
  select(LitA, A, RemA),
  select(LitB, B, RemB),
  complementary(LitA, LitB),
  append(RemA, RemB, Combined),
  sort(Combined, Resolvent).         % sort also removes duplicate literals

% Print a clause with variables shown as A, B, C ... instead of _123
show_clause(Clause) :-
  \+ \+ ( copy_term(Clause, C),
          numbervars(C, 0, _),
          write_term(C, [numbervars(true), quoted(true)]) ).

% A resolvent is new if no stored clause is the same up to variable renaming
is_new(Resolvent) :-
  \+ ( kb(_, Existing, _), Existing =@= Resolvent ).

% Load the clauses from Step 7 into the knowledge base kb/3
load_kb :-
  retractall(kb(_, _, _)),
  cnf_clauses(Clauses),
  forall(nth1(I, Clauses, C), assertz(kb(I, C, given))).

% Given-clause loop: take clause J, resolve it with every earlier clause I.
% Stops (by throwing found/1) as soon as the empty clause [] appears.
refute :-
  load_kb,
  catch(given(1), found(Id), print_proof(Id)).

given(J) :-
  (   kb(J, CJ, _)
  ->  J0 is J - 1,
      forall(between(1, J0, I), try_pair(I, J, CJ)),   % every earlier clause I
      J1 is J + 1,
      given(J1)
  ;   writeln('No empty clause could be derived.'), fail
  ).

try_pair(I, J, CJ) :-
  kb(I, CI, _),
  forall(( resolve(CI, CJ, R), is_new(R) ),
         add_resolvent(R, I, J)).

add_resolvent(R, I, J) :-
  (   is_new(R)
  ->  aggregate_all(count, kb(_, _, _), N),
      Id is N + 1,
      assertz(kb(Id, R, from(I, J))),
      (   R == [] -> throw(found(Id)) ; true )
  ;   true
  ).

% Collect only the clauses that the empty clause depends on, in order
ancestors(Id, Set) :-
  kb(Id, _, Src),
  (   Src = from(A, B)
  ->  ancestors(A, SA), ancestors(B, SB),
      append([SA, SB, [Id]], All), sort(All, Set)
  ;   Set = [Id]
  ).

print_proof(EmptyId) :-
  ancestors(EmptyId, Used),
  format('~nClauses used in the proof (numbers refer to Step 7 / resolvent ids):~n'),
  forall(( member(Id, Used), kb(Id, C, given) ),
         ( format('  [~w] ', [Id]), show_clause(C), nl )),
  format('~nResolution steps, in order:~n'),
  forall(( member(Id, Used), kb(Id, C, from(A, B)) ),
         ( kb(A, CA, _), kb(B, CB, _),
           format('~nResolvent [~w] from [~w] and [~w]:~n', [Id, A, B]),
           format('  Clause 1 : '), show_clause(CA), nl,
           format('  Clause 2 : '), show_clause(CB), nl,
           format('  Resolvent: '), show_clause(C), nl )),
  format('~n========================================~n'),
  format('EMPTY CLAUSE DERIVED: [] (Contradiction)~n'),
  format('PROVED: Mira is trusted.~n'),
  format('========================================~n').

run :-
  writeln('=== FIRST-ORDER LOGIC RESOLUTION REFUTATION ==='),

  format('~n--- Step 1: Predicate Logic ---~n'),
  predicate_logic(P), print_list(P),
  goal(G), format('Goal: '), show_clause(G), nl,

  format('~n--- Step 2: Negation of Goal ---~n'),
  negated_goal(NG), show_clause(NG), nl,

  format('~n--- Step 3: Implication Removal ---~n'),
  no_implications(NI), print_list(NI),

  format('~n--- Step 4: Negation Movement ---~n'),
  negation_normal_form(NNF), print_list(NNF),

  format('~n--- Step 5: Standardization ---~n'),
  standardized(S), print_list(S),

  format('~n--- Step 6: Skolemization ---~n'),
  skolemized(SK), print_list(SK),

  format('~n--- Step 7: CNF Clauses ---~n'),
  cnf_clauses(CNF), print_list(CNF),

  format('~n--- Step 8: Resolution Refutation Steps ---~n'),
  refute.

% Print one formula per line
print_list(List) :-
  forall(member(F, List), ( write('  '), show_clause(F), nl )).
