echo "Initializing Bot now..."
echo "Installing deps"
pip install -r requirements.txt
echo "Pulling from GitHub..."
git reset --hard HEAD
git pull "https://github.com/EclipseDiscordBot/EclipseDiscordBot.git" --allow-unrelated-histories
git commit -F notes.txt
echo "Pulling and Merging successful "
python main.py