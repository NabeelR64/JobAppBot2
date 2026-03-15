## 2024-05-24 - N+1 Issue and In-Memory Filtering in `get_recommendations`
**Learning:** Found O(N) application memory usage and inefficient massive SQL queries in `backend/app/api/jobs.py` where a large list of swiped IDs is fetched into application memory and passed to `.notin_()`.
**Action:** In SQLAlchemy, use subqueries directly by passing a query object to `notin_()` instead of evaluating queries and fetching large lists of IDs.
