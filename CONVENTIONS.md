# Code Conventions

> This file contains general guidelines and thumb rules.  
> Violating them is not a crime

## 1. General rules

1. Readability comes first. Optimizations applied later.
2. Follow **KISS** (keep it simple) and **DRY** (don’t repeat yourself), but balanced. Sometimes repeating is okay.
3. Public functions and new modules should have type annotations and docstrings.

## 2. File structure

1. Put configuration-like constants and settings at the start of the file(projectroom3.py is good example)
2. Import ordering: standard library -> other packages -> local modules
3. Each module should have concise responsibility

## 3. Functions and classes

1. Function does **one** specific job.
2. Classes model entities (nouns), methods express actions (verbs).
3. If a function has many parameters, consider grouping them into a class or config object.
4. Internal(support functions) start with `_`.

## 4. Naming

1. Naming should be meaningful and self-explanatory: only well-known abbreviations.
2. Constants — `UPPER_CASE`, funcs and variables — `snake_case`, classes — `CamelCase`.
3. Module and package names should be short, lowercase, meaningful.

## 5. Testing

1. New modules and functions must be covered with tests.  

> If the functionality is experimental, focus on integration tests first(how it works with other parts of code). Unit tests can follow once the API stabilizes.

2. Each test is separated and tests one aspect.
3. Names of test can be long. Including 'what is tested' and 'condition' is encouraged.

## 6. Git and code review

1. Each commit should represent a meaningful step (fix, refactor, feature part). Use `-m '<your message>'` flag with commit.

> Small commits(literally one line) are fine if they are logical  
> You can see commit as snapshot of your work. After few coding hours it is usual to push 5 commits at once about one feature.

2. Don't add or commit temporary files, API-tokens or IDE settings. They are either personal or sensitive.  
Use .gitignore file for it.

3. Before `push`: run `pre-commit` and `pytest`.
