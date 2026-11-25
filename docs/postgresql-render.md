# Render PostgreSQL configuration and SQLite data review

## Configure the web service

The project uses `dj-database-url` and Psycopg 3 (pinned in `requirements.txt`). In Render, open the existing Webstam web service's **Environment** page and set:

- `DJANGO_ENV` = `production`
- `DJANGO_DEBUG` = `false`
- `DATABASE_URL` = the **Internal Database URL** copied from the existing `webstam` database's Dashboard connection details (database name and username are `webstam`)

Use the internal URL when the Render web service and database are in the same region. Do not paste it into source, this document, `.env.example`, or `render.yaml`. The password must remain inside Render's secret environment-variable storage. Django requires SSL in production and uses a 60-second connection lifetime with connection health checks. Do not create another database resource: this repository has no `render.yaml`, so configure the existing service in the Dashboard.

After setting the variable and deploying, run migrations as a deliberate release step from Render's Shell or a one-off job, after reviewing the target database and backup status. Do not run them from a developer machine against production. Applying schema migrations does not transfer SQLite records.

## Local SQLite data inventory

The checked local `db.sqlite3` remains intact. A read-only inventory found:

- `contact_inquiry`: 1 row (may contain personal data)
- `core_teammember`: 2 rows
- `core_projectcasestudy`: 4 rows
- `core_externalprofile`: 3 rows
- `contact_budgetband`: 5 rows
- `blog_article` and `blog_category`: 0 rows
- `auth_user`: 0 rows
- Other authentication, admin, session, and migration tables are present; zero-row tables were not individually listed.

The contact inquiry is user-submitted data, and the core records may be important deployment content. No data was exported, copied, or loaded into PostgreSQL. Confirm which records are authoritative before planning a transfer.

## Safe transfer plan (approval required)

Before transferring anything, an operator should:

1. Confirm the Render database is the intended target and determine whether it already contains data. Take and verify a Render backup/snapshot; do not overwrite or reset it.
2. Make a protected, access-controlled backup of the local SQLite file and record its checksum. Restrict access because the database contains an inquiry.
3. Decide whether to migrate all records or only approved content. A full fixture can include inquiry personal data, sessions, admin logs, and password hashes; review and exclude data that should not move.
4. Apply schema migrations to an empty, verified target only after the backup/target review. If the existing Render database has application data, reconcile schema and records using a reviewed, database-specific migration plan instead of loading fixtures over it.
5. For approved records, create a reviewed Django data fixture or explicit ETL mapping, inspect counts and relationships without exposing inquiry values, load into a protected staging copy first, and verify counts/referential integrity and application behavior.
6. Schedule any production import with a rollback plan and explicit approval. Do not use `flush`, database recreation, or overwrite-oriented fixture commands on a target that may contain data.
