# dhvxml2cup

## Übersicht

Ein python-Skript, dass Geländedaten des DHV im XML-Format in das SeeYou Wegpunkte-Format (.cup) umwandelt.
Zusätzlich kann eine .txt-Datei erstellt werden, die Details der Gelände enthält. Diese können z.B. in XCSoar verwendet werden.

Die Geländedaten lassen sich [hier](https://www.dhv.de/web/piloteninfos/gelaende-luftraum-natur/fluggelaendeflugbetrieb/gelaendedaten/gelaendedaten-download) herunterladen.

## Verwendung

```
dhvxml2cup [-d] -o outputName xmldatei
```

Mit `-o outputName` wird der Name der zu erzeugenden Datei(en) (ohne Endung) angegeben. Die Datei mit den Geländedaten muss am Schluss angegeben werden.
Optional kann der Schalter `-d` bzw. `--detail` übergeben werden, dann wird die .txt-Datei mit den Geländedetails zusätzlich erstellt.
