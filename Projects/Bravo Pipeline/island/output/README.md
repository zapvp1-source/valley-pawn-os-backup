# Island — output/

CSV outputs from island handlers land here, following the same naming convention as prod:

```
<date>_<STORE>_<report>.csv
<from>_to_<to>_<STORE>_<report>.csv
```

This folder is intentionally separate from `Bravo Data Extraction/output/`. Island consumers must read from here. Prod consumers must continue reading from prod. No crossing.
