# Commands
Prefix commands with a `!`

1. **steam** `{cmd}` `{arg}`: Provides administrative utilities for anything to do with steam. `cmd` currently only recognizes `register` with the `arg` being your steam id.
    1. `steam register {arg}`: controls steam ID registration/removal
        1. `steam register {steam_id}`: register your steam ID with the bot
        1. `steam register remove`: delete your steam ID from the bot
        1. `steam register list`: list all the users in the server that the bot has steam IDs for
1. **gic**: If you're in a voice channel with more than one person who has a steam id on file and a public steam profile, this will create a list of multiplayer games that you all have in common. It also includes a separate table for games which at least one person has that are Remote Play Together (RPT).