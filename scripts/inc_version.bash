if [ $author == 'satyamedh' ] || [ $author == 'zapd0s' ]
then
  exit 0
else
  python "$GITHUB_WORKSPACE/scripts/python_scripts/increment_version.py"
fi

