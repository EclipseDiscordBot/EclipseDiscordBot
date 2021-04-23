sudo apt install tree
tree $GITHUB_WORKSPACE
python "$GITHUB_WORKSPACE/scripts/python_scripts/increment_version.py"