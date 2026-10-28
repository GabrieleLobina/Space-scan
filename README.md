# Space Scan — Mission Intelligence

Dashboard: https://gabrielelobina.github.io/Space-scan/

## Features
Timeline NASA Artemis e SpaceX; countdown solo per date con orario noto; schede hardware con milestone documentate; schemi SVG; notizie NASA e Spaceflight News API; registro delle nuove notizie.

## Affidabilità
Le missioni Artemis sono basate su fonti NASA. I calendari SpaceX possono cambiare. Le informazioni sulla produzione Starship provenienti da newlaunch.space sono di terze parti, non conferme ufficiali. Le immagini sono illustrative e non certificano lo stato di costruzione. Le milestone e i lanci in `data.json` sono uno snapshot editoriale, non ancora aggiornato automaticamente.

## Aggiornamento automatico
Il workflow `.github/workflows/update.yml` aggiorna **news e registro delle nuove notizie**, non i calendari dei lanci o le milestone hardware. Orario 06:00 UTC (07:00 CET / 08:00 CEST). Avvio manuale da Actions. Per errori di push: Settings → Actions → General → Workflow permissions → Read and write permissions.

## GitHub Pages
Settings → Pages → Deploy from a branch → main → /(root).

## Roadmap
Integrazione API per calendario lanci, fotografie ufficiali con crediti, aggiornamento verificato delle milestone, storico delle variazioni delle date.
