# Deterministic Finite Automaton (DFA) Design for Keyword `ERROR`

**Course:** 24CS52 — Theory of Computations | **Assignment:** SET-E Case Study

---

## 1. Formal 5-Tuple Mathematical Formulation

$$M = (Q, \Sigma, \delta, q_0, F)$$

1. **State Set $Q = \{q_0, q_1, q_2, q_3, q_4, q_5, q_{\text{word}}\}$**:
   - $q_0$: Initial / Word Boundary State.
   - $q_1$: Matched prefix `'E'` at a valid left boundary.
   - $q_2$: Matched prefix `'ER'`.
   - $q_3$: Matched prefix `'ERR'`.
   - $q_4$: Matched prefix `'ERRO'`.
   - $q_5$: Candidate `'ERROR'` recognized; awaiting right boundary confirmation.
   - $q_{\text{word}}$: Inside-Word Trap State. Absorbs word characters until reset by a delimiter.

2. **Input Alphabet Equivalence Classes ($\Sigma$)**:
   - $C_E = \{ \mathtt{'E'} \}$
   - $C_R = \{ \mathtt{'R'} \}$
   - $C_O = \{ \mathtt{'O'} \}$
   - $C_{\text{other\_word}} = \{ \mathtt{'a'}\text{--}\mathtt{'z'}, \mathtt{'A'}\text{--}\mathtt{'Z'}, \mathtt{'0'}\text{--}\mathtt{'9'}, \mathtt{'\_'} \} \setminus \{ \mathtt{'E'}, \mathtt{'R'}, \mathtt{'O'} \}$
   - $C_{\text{non\_word}} = \Sigma \setminus \text{WordChars}$

3. **Start State:** $q_0$

4. **Accepting Condition ($F$):**
   In state $q_5$, if the subsequent symbol $c \in C_{\text{non\_word}}$ or at $\text{EOF}$, the match is emitted and the automaton transitions to $q_0$. If $c \in \text{WordChars}$, the automaton enters $q_{\text{word}}$ without match emission.

---

## 2. Complete Transition Table ($\delta$)

```text
+-------------------+------------+------------+------------+--------------------+-------------------+
| Current State     | Input: 'E' | Input: 'R' | Input: 'O' | Other Word Char    | Non-Word Char     |
+-------------------+------------+------------+------------+--------------------+-------------------+
| q0 (Boundary)     | q1         | q_word     | q_word     | q_word             | q0                |
| q1 (Saw 'E')      | q_word     | q2         | q_word     | q_word             | q0                |
| q2 (Saw 'ER')     | q_word     | q3         | q_word     | q_word             | q0                |
| q3 (Saw 'ERR')    | q_word     | q_word     | q4         | q_word             | q0                |
| q4 (Saw 'ERRO')   | q_word     | q5         | q_word     | q_word             | q0                |
| q5 (Saw 'ERROR')  | q_word     | q_word     | q_word     | q_word             | q0 [EMIT MATCH]   |
| q_word (Trap)     | q_word     | q_word     | q_word     | q_word             | q0                |
+-------------------+------------+------------+------------+--------------------+-------------------+
```

---

## 3. State-Transition Diagram

```mermaid
stateDiagram-v2
    [*] --> q0
    
    q0 --> q0: Non-Word Char
    q0 --> q1: 'E' (record start offset)
    q0 --> q_word: 'R', 'O', OtherWord
    
    q1 --> q2: 'R'
    q1 --> q0: Non-Word Char
    q1 --> q_word: 'E', 'O', OtherWord
    
    q2 --> q3: 'R'
    q2 --> q0: Non-Word Char
    q2 --> q_word: 'E', 'O', OtherWord
    
    q3 --> q4: 'O'
    q3 --> q0: Non-Word Char
    q3 --> q_word: 'E', 'R', OtherWord
    
    q4 --> q5: 'R'
    q4 --> q0: Non-Word Char
    q4 --> q_word: 'E', 'O', OtherWord
    
    q5 --> q0: Non-Word Char / EOF [EMIT MATCH]
    q5 --> q_word: Word Char (ERRORS, etc.)
    
    q_word --> q_word: Any Word Char
    q_word --> q0: Non-Word Char
```

---

## 4. Graphviz DOT Representation

```dot
digraph DFA_Error_Scanner {
    rankdir=LR;
    node [shape=circle, fontname="Helvetica"];
    
    q0 [label="q0\n(Start/Boundary)", peripheries=1];
    q1 [label="q1\n('E')"];
    q2 [label="q2\n('ER')"];
    q3 [label="q3\n('ERR')"];
    q4 [label="q4\n('ERRO')"];
    q5 [label="q5\n('ERROR')", peripheries=2];
    q_word [label="q_word\n(Trap)"];
    
    q0 -> q0 [label="Non-Word"];
    q0 -> q1 [label="'E'"];
    q0 -> q_word [label="'R','O',OtherWord"];
    
    q1 -> q2 [label="'R'"];
    q1 -> q0 [label="Non-Word"];
    q1 -> q_word [label="'E','O',OtherWord"];
    
    q2 -> q3 [label="'R'"];
    q2 -> q0 [label="Non-Word"];
    q2 -> q_word [label="'E','O',OtherWord"];
    
    q3 -> q4 [label="'O'"];
    q3 -> q0 [label="Non-Word"];
    q3 -> q_word [label="'E','R',OtherWord"];
    
    q4 -> q5 [label="'R'"];
    q4 -> q0 [label="Non-Word"];
    q4 -> q_word [label="'E','O',OtherWord"];
    
    q5 -> q0 [label="Non-Word / EOF\n[EMIT]"];
    q5 -> q_word [label="WordChar"];
    
    q_word -> q_word [label="WordChar"];
    q_word -> q0 [label="Non-Word"];
}
```

