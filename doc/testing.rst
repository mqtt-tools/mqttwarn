#######################
The mqttwarn test suite
#######################

Testing mqttwarn is not rocket science at all.


***************
Getting started
***************
Run tests::

    make test


.. note::

    For running specific tests, please follow the pytest documentation at
    `Specifying tests / selecting tests <https://docs.pytest.org/en/latest/usage.html#specifying-tests-selecting-tests>`_.


*************
Code coverage
*************
Run tests::

    make test-coverage

Display code coverage results::

    open .pytest_results/htmlcov/index.html
