
develop2:
	./tools/make-virtualenv2.sh


develop3:
	./tools/make-virtualenv3.sh


clean:
	git clean -dfxn | grep 'Would remove' | awk '{print $3}' | grep -v -e '^.idea' -e '^.cache' | xargs rm -rf


check:
	flake8 ./pybake --ignore E501


test:
	pytest ./tests/ -vvv --junitxml=./reports/unittest-results.xml


test2: develop2 check
	pytest ./tests/ -vvv --junitxml=./reports/unittest-results.xml


test3: develop3 check
	pytest ./tests/ -vvv --junitxml=./reports/unittest-results.xml


to_pypi_test: test2 test3
	python setup.py register -r pypitest
	python setup.py sdist upload -r pypitest


to_pypi_live: test2 test3
	python setup.py register -r pypi
	python setup.py sdist upload -r pypi
