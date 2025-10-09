# Toka Oratory Layer — Moon Counsel (Author Pack)

This folder holds the **oral tradition library** for Toka's moon counsel.
The bot will eventually read this YAML, but for now this is a writer-first artifact.

## Principles baked into the schema
- **Transition Wisdom**: liminal guidance exists *between* phases.
- **Plant Wisdom**: cannabis teaches timing, patience, community.
- **Fa‘asāmoa as Technology**: rhetorical tags `etak`, `pehe`, `va` shape how Toka speaks.
- **Moon as Unifier**: one line that ties global navigators together.

## Authoring rules
- Keep Toka’s voice: tautai-orator, respectful, metaphor-rich, anti-FOMO.
- Prefer short chant-like lines; avoid stats here.
- No placeholders: leave empty strings ("") if you’re not ready to fill a field.
- Southern Hemisphere differences can be noted in `alt_imagery`.

## Fields (per phase)
- `setting`: where/when Toka speaks (scene line)
- `chant`: a memorable phrase or name for the phase
- `observation`: what he perceives (sea/market/people)
- `counsel`: concrete guidance
- `proverb`: fa‘asāmoa or crafted proverb
- `weed_wisdom`: plant timing/lesson for this phase
- `unity_line`: “one moon, many canoes” style closing
- `faasamoa_tags`: [etak|pehe|va] — **choose 1–3** that inform delivery
- `tone`: ritual | light
- `silence`: true|false (true = minimal counsel; observation only)
- `alt_imagery`: optional imagery tweaks (e.g., Southern Hemisphere note)

## Transitions
Each transition (e.g., `full_moon -> waning_gibbous`) gets its own entry with:
- `chant`, `observation`, `counsel`, `proverb`, `weed_wisdom`, `unity_line`, `faasamoa_tags`, `tone`

## Archive (future)
`data/oratory/moon_archive.json` will store live counsel lines Toka spoke, for community search.

