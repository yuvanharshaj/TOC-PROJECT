# Regular Expression Analyzer Design and Specification

**Course:** 24CS52 — Theory of Computations | **Assignment:** SET-E Case Study

---

## 1. Overview

The Regular Expression Analyzer ([`src/re_analyzer.py`](file:///c:/Users/yuvan/OneDrive/Documents/5-SEMESTER/PROJECTS/TOC%20PROJECT/src/re_analyzer.py)) extracts five distinct token patterns from log files using Python's standard `re` module. To prevent substring false positives, all patterns employ boundary anchors or zero-width lookaround assertions.

---

## 2. Formal Pattern Definitions

### 1. Date Pattern (DD-MM-YYYY)
```regex
(?<!\d)(?:0[1-9]|[12]\d|3[01])-(?:0[1-9]|1[0-2])-\d{4}(?!\d)
```
- **Boundary Guards:** `(?<!\d)` and `(?!\d)` ensure no adjacent digits prefix or suffix the token.
- **Day Sub-pattern:** `(?:0[1-9]|[12]\d|3[01])` matches days $01\text{--}31$.
- **Month Sub-pattern:** `(?:0[1-9]|1[0-2])` matches months $01\text{--}12$.
- **Year Sub-pattern:** `\d{4}` matches exactly four calendar digits.
- **Documented Limitation:** Does not validate calendar-specific month lengths (e.g., February 31st or leap years).

### 2. Time Pattern (HH:MM)
```regex
(?<!\d)(?:[01]\d|2[0-3]):[0-5]\d(?!\d)
```
- **Boundary Guards:** `(?<!\d)` and `(?!\d)` ensure no adjacent digits.
- **Hour Sub-pattern:** `(?:[01]\d|2[0-3])` matches 24-hour range $00\text{--}23$.
- **Minute Sub-pattern:** `[0-5]\d` matches minute range $00\text{--}59$.

### 3. IPv4 Address Pattern
```regex
(?<![\d.])(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}(?![\d.])
```
- **Boundary Guards:** `(?<![\d.])` and `(?![\d.])` ensure the address is not an embedded component of an invalid multi-octet token like `1.2.3.4.5`.
- **Octet Validation:**
  - `25[0-5]`: Matches $250\text{--}255$.
  - `2[0-4]\d`: Matches $200\text{--}249$.
  - `1\d\d`: Matches $100\text{--}199$.
  - `[1-9]?\d`: Matches $0\text{--}99$.

### 4. ERROR Keyword Pattern
```regex
\bERROR\b
```
- **Word Boundaries:** `\b` asserts that the token is bordered by non-word characters `\W` (or string edges), rejecting `ERRORS`, `XERROR`, and `ERROR_CODE`.

### 5. WARNING Keyword Pattern
```regex
\bWARNING\b
```
- **Word Boundaries:** `\b` asserts that the token is bordered by non-word characters `\W`, rejecting `WARNINGS` and `PREWARNING`.

---

## 3. Results on `data/sample.log`

- **Date:** 26 occurrences
- **Time:** 26 occurrences
- **IPv4 Address:** 10 occurrences
- **ERROR Keyword:** 7 occurrences
- **WARNING Keyword:** 6 occurrences
- **Total Matches:** 75 occurrences across 30 log lines (2,520 characters).

