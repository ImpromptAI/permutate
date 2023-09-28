from permutate.runner import Runner


def test_batch_job():
    runner = Runner()
    runner.start(
        "tests/files/plugin_test.yaml",
        output_directory="tests/files/output/",
        save_to_csv=False,
    )
