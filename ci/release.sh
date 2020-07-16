## Bump version using poetry and tag version, assumes minor version patch

BUMP_ACTION=${1:-patch} 
echo poetry version $BUMP_ACTION
NEW_VER=$(poetry version | cut -d' ' -f 2)
echo "__version__ = '$NEW_VER'" > hs_formation/__version__.py
git tag "v${NEW_VER}"
git push --tags
run poetry publish --build