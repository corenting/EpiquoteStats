# EpiquoteStats

This script can be used to obtain a local SQL copy of the quotes database of [Epiquote](https://epiquote.fr/).

The database will be saved as a SQLite database, but it can be easily modified to save to any database supported by SQLAlchemy.

As an example, a `get_authors_count()` function is provided to get the people having the most quotes.
