import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
summarizings_folder_path = BASE_DIR / "summarizings"


class File:
    def __init__(self, file_name: str, text: str):
        self.file_name = file_name
        self.file_extension = ".txt"
        self.dir_path = summarizings_folder_path
        self.file_path = summarizings_folder_path / f"{self.file_name}{self.file_extension}"
        self.text = text

    def create_dir(self) -> None:
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

    def save(self) -> Path:
        """
        Write text to file.

        Returns:
            Path: path to saved file.
        """
        try:
            self.create_dir()
            with open(self.file_path, "w") as file:  # noqa: FURB103
                file.write(self.text)
                return self.file_path

        except Exception as err:
            raise ValueError("Error while saving file.") from err

    def read(self) -> str:
        """Return text from file."""
        try:
            with open(self.file_path, "r") as file:
                return file.read()
        except Exception as err:
            raise ValueError("Error while reading file.") from err
