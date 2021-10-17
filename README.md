# new-world-gear-bot
 bot for storing discord user's new world builds

## Required Libraries:
  1. Python
  2. discord.py
  3. dotenv
  4. gspread
  5. oauth2client
  6. validators

## Commands:

```!gear``` - check the gear of [target], which defaults to author.
> Usage: `!gear [target]`

```!update``` - Update the author's information, optional [field].
> Usage: `!windows [field]`
> 
> Valid [field] parameters:
> - ign, lvl, gs, primary, secondary, img
> 
> Valid [primary] and [secondary] parameters:
>   - fire staff, life staff, ice gauntlet, bow, musket, rapier, sword, hammer, great axe, spear, hatchet

```!help``` - Returns link for commands, and invite link.
