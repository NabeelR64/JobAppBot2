## 2024-05-24 - [SQLAlchemy N+1 Query Fix]
**Learning:** Evaluated queries fetching large lists of IDs into application memory for filtering via `IN` clauses result in massive SQL queries and O(N) application memory usage. Using SQLAlchemy subqueries is a cleaner and much more performant pattern.
**Action:** Always prefer passing query objects directly to `notin_()` or `in_()` in SQLAlchemy to execute the filtering directly within the database engine via subqueries.
