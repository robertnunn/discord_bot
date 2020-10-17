# Discord Bot

This is a simple discord bot that I made for fun.

## Commands
Prefix commands with a `!` to use them.
1. **liar**: Calls someone a liar!
1. **dice** `dice_str`: Rolls the dice specified by `dice_str`. E.g., `2d6`, `3d8+2`. Supports adding, subtracting, and multiplying values. Modifiers and dice rolls may be chained together, but a dice roll (`XdY`) must come before any modifiers. No spaces in `dice_str`.
    - `-XL` to drop the lowest `X` dice (omitting `X` implies `X=1`)
    - `XdY!` to roll exploding dice
1. **8ball**: Ask the magic 8-ball.
1. **dnd** `num`: If `num` is omitted or 1 > `num` > 100, gets a random adventure from "The Doc Aquatic Brand Random Adventure Table". If `num` is specified, get that specific adventure.
1. **magic20**: Custom version of the magic 8ball, all custom responses.