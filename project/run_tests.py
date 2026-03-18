import unittest

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover("tests")

    with open("unittest_results.log", "w") as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        runner.run(suite)
