sudo apt install tree
echo "Here starts tree"
tree /home
echo "here ends tree"
python "$GITHUB_WORKSPACE/scripts/python_scripts/increment_version.py"