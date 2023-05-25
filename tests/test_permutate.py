from permutate.main import permutate


def test_batch_job():
    permutate("tests/files/plugin_test.yaml", save_to_csv=False)
