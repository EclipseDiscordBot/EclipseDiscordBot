echo "Initializing Bot now..."
echo "Pulling from GitHub..."
git reset --hard HEAD
git pull "https://github.com/EclipseDiscordBot/EclipseDiscordBot.git" --allow-unrelated-histories
git checkout master
git commit -F notes.txt
echo "Pulling and Merging successful "
echo "Installing deps"
pip install -r requirements.txt
echo "Done installing deps!"
python main.py