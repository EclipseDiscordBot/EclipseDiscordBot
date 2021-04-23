if [ $author == 'satyamedh' ] || [ $author == 'zapd0s' ]
then
  exit 0
else
  python "$GITHUB_WORKSPACE/scripts/python_scripts/increment_version.py"
  git add $GITHUB_WORKSPACE/constants/version.txt
  git commit -m "Bumped version"
  git push
fi

