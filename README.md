# Space Scan

Dashboard statica dedicata a NASA Artemis e SpaceX, con illustrazioni SVG, timeline e feed news.

## Pubblicazione
In **Settings → Pages**, selezionare **Deploy from a branch**, branch **main**, cartella **/(root)**.

## Aggiornamenti
Il workflow **Daily space news refresh** aggiorna il feed ogni giorno alle 06:00 UTC (07:00 CET / 08:00 CEST), e può essere avviato manualmente da Actions. In caso di errori di scrittura abilitare **Settings → Actions → General → Workflow permissions → Read and write permissions**.

Le notizie provengono dal feed NASA e da Spaceflight News API. Le milestone `artemis` e `spacex` nel file `data.json` vanno aggiunte solo con date e fonti verificate. I disegni SVG sono schematici, non documentano lo stato effettivo di costruzione.
