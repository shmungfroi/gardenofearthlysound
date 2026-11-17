# The Garden of Earthly Sounds

A map of art music from 800 to today, by Justin Ossher (Rose Bay Secondary College).

Eight **spires** (families of music) grow from **the commons**: folk song, dance and work song. The commons is the central spire, rising from a single **seed** at the origin, with **roots** fanning out to every spire. **Storeys** (periods) rise from the ground at 800 to today at the top. **Minarets** are genres, and **lanterns** are the 213 forms, joined by 563 **links**.

## Use it
- **Move:** drag, scroll or pinch.
- **Levels:** step Garden › Spire › Storey › Lantern with **+** and **−**, the ladder or the breadcrumb.
- **Keys:** the arrow keys move to the next spire or storey; `/` searches.
- **Search:** find a lantern, see its whole web of links, then click it to open its card.

## Build
Requirements: Python 3 with Pillow, and Node.

```
./build.sh
```

The script:
1. Exports `src/data.json` from `gx_data.js`.
2. Lays out the map and checks that no name touches another name or point (`src/build.py`).
3. Packs the page into `index.html` (`src/pack.py`, with `src/template.html`).

Display names that need special handling are in `src/names.json`.

The lantern card (`card.js`) follows the Garden's card: notices, Listen (recordings, scores, Spotify), Learning music, Answer like an analyst, the NSW syllabus panel for teachers, Learning about music, Connections with reasons, and Sources.

## Design
- **Spires:** each family has its own jewel colour.
- **Everything else:** text, links, lanterns and the frame use gold, red, green and ivory on warm black.
- **Type:** Outfit (names) and Poiret One (display), both under the SIL Open Font License.

**Live:** https://shmungfroi.github.io/thegardenofearthlysounds/

The earlier painted, zoomable Garden is kept in [theoldgardenofearthlysounds](https://github.com/shmungfroi/theoldgardenofearthlysounds) (branch `painted-garden`).
