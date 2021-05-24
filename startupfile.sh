#! /bin/bash

rm -rf data/*.gif
git pull "https://github.com/EclipseDiscordBot/EclipseDiscordBot.git" --allow-unrelated-histories
python main.py