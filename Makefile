watch:
	poetry run ptw -- --testmon

cover:
	poetry run pytest --cov=formation tests -sq

test:
	poetry run pytest -vv --cov-report xml:cov.xml --cov=formation tests -sq

tox:
	poetry run tox

release:
	ci/release.sh patch

release-minor:
	ci/release.sh minor

release-major:
	ci/release.sh major
