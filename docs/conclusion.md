# Case Study Conclusion

**Course:** 24CS52 — Theory of Computations | **Assignment:** SET-E Case Study

---

## 1. Summary of Achievements

This case study successfully demonstrated both the practical utility and formal theoretical foundations of pattern matching in system log analysis:
1. **Regular Expressions:** Formulated five robust regular expressions incorporating zero-width assertions (`(?<!\dots)`, `(?!\dots)`, `\b`) to eliminate false substring matches in semi-structured text.
2. **Deterministic Finite Automata:** Formally designed an equivalent 7-state DFA $M = (Q, \Sigma, \delta, q_0, F)$ over five alphabet equivalence classes to recognize the whole-word keyword `ERROR` without using regular expression libraries.
3. **100% Spatial Parity:** Both implementations were evaluated against a 30-entry benchmark dataset (`data/sample.log`, 2,520 bytes) and achieved identical results: extracting 7 occurrences of `ERROR` with identical zero-based spans $[start:end)$ and 1-based line/column coordinates.
4. **Empirical Benchmarking:** A 1,000-iteration benchmark grounded the complexity comparison in measurable performance, elucidating the performance characteristics of native C extension libraries versus interpreted Python virtual machine loops.
5. **Automated Verification:** Verified system correctness across 21 unit test methods and 28 subtests without a single failure.

---

## 2. Theoretical Reflections

- **Equivalence of Formalisms:** The experimental results demonstrate Kleene's theorem in practice: regular expressions and finite automata possess equivalent expressive power for regular languages.
- **Engineering Trade-offs:**
  - Regular expressions provide declarative expressiveness and development agility for complex token grammars (such as IPv4 addresses and timestamps).
  - Deterministic Finite Automata provide complete mathematical transparency, bounded linear traversal, and a model directly transferable to hardware or low-level lexical scanners.

---

## 3. Academic Compliance

All deliverables adhere strictly to the 24CS52 Theory of Computations course syllabus, SET-E guidelines, and Bloom's Taxonomy Level 3 & 4 (Apply, Analyze, and Evaluate) requirements.

