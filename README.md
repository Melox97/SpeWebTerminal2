# SPE Web Terminal 2

SPE Web Terminal 2 è un progetto **open source e indipendente**
che fornisce un backend HTTP per il controllo remoto di amplificatori lineari SPE Expert.

Il progetto è sviluppato come iniziativa **non ufficiale**,
con l’obiettivo di realizzare un sistema semplice, stabile e multipiattaforma,
basato su una separazione chiara dei componenti.

## Operational notes

This project writes local runtime logs under `./log/` for troubleshooting.  

When called, the endpoint:
- creates a snapshot of the current runtime log
- saves it locally under the `log/` directory
- returns the path of the generated snapshot

Example response:
```json
{
  "saved": true,
  "path": "log/snapshot-YYYYMMDD-HHMMSS.log"
}

The `log/` directory is intentionally excluded from version control.
