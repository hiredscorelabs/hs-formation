set +x 
## Bump version using poetry and tag version, assumes minor version patch

BUMP_ACTION=${1:-patch} 
TARGET_REMOTE=${2:-origin}
OLD_VER=$(poetry version | cut -d' ' -f 2)
poetry version $BUMP_ACTION
NEW_VER=$(poetry version | cut -d' ' -f 2)
echo "__version__ = '$NEW_VER'" > hs_formation/__version__.py
sed "s/version = \"${OLD_VER}\"/version = \"${NEW_VER}\"/g" pyproject.toml | tee pyproject.toml
git commit -am"[CI] bump version from ${OLD_VER} to ${NEW_VER}"
git tag "v${NEW_VER}"
git push $TARGET_REMOTE && git push --tags
poetry run publish --build