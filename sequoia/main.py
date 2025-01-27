"""Runs an experiment, which consist in applying a Method to a Setting.
"""
import sequoia.methods
from sequoia.methods import get_all_methods
from sequoia.settings import all_settings
from sequoia.utils import get_logger
from sequoia.experiments import Experiment

logger = get_logger(__file__)

def main():
    logger.debug("Registered Settings: \n" + "\n".join(
        f"- {setting.get_name()}: {setting} ({setting.get_path_to_source_file()})" for setting in all_settings
    ))
    logger.debug("Registered Methods: \n" + "\n".join(
        f"- {method.get_full_name()}: {method} ({method.get_path_to_source_file()})" for method in get_all_methods()
    ))

    return Experiment.main()


if __name__ == "__main__":
    main()
