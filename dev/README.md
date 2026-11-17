# Developer tools

- `run_tests.sh` runs the 13 regression suites (every one should print `errors []`).
- `tests/glossaudit.py` opens every card (lanterns, composers, events) on desktop and phone, clicks every highlighted term and element chip, and reports any box that covers text or spills out of the card (should report 0 problems).
- The other scripts in `tests/` take screenshots used when reviewing a change (grass, stars, journey sheet, research challenge).
- `serve.py PORT DIR` is the small local web server the suites use.

Build first with `./build.sh` (it must report 0 name clashes).
