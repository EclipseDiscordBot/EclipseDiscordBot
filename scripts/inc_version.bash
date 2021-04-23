sudo apt install tree
echo "Here starts tree"
tree $GITHUB_WORKSPACE
echo "here ends tree"
python "$GITHUB_WORKSPACE/scripts/python_scripts/increment_version.py"