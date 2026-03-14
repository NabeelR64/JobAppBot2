## 2024-05-14 - SQLAlchemy Memory Bottleneck on N+1 / notin_
**Learning:** In SQLAlchemy, passing a massive list of IDs to `notin_` after fetching them into memory with `.all()` causes N+1 problems and excessive memory use. This is O(N) in the application.
**Action:** Use a subquery directly inside `notin_` (e.g., `db.query(SwipeAction.job_posting_id)...`) to push the computation to the database.
