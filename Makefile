init:
	sudo pip3 install -r requirements.txt
test:
	pytest -v --cov=rocks --cov-report html tests
install:
	sudo pip3 install -e .
