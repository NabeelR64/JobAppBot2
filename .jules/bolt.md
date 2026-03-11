## 2024-03-11 - [Backend] Optimizing SQLAlchemy `notin_` Evaluation Memory Bottleneck
**Learning:** Evaluated SQLAlchemy queries passed to `notin_` (e.g. fetching a large list of IDs) cause massive SQL queries with huge IN clauses and O(N) application memory usage, which is a bottleneck when dealing with high-volume actions like job swipes.
**Action:** Always use SQLAlchemy subqueries directly (passing a query object instead of a list) when filtering against potentially large sets of IDs in `notin_` to prevent out-of-memory errors and improve query performance.
