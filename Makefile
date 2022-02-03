imports:
	autoflake --remove-all-unused-imports --in-place --recursive ./
	isort ./

lint:
	flake8 ./
