
import pytest

from pathlib import Path

from tools.file_tools import (
    create_list_files,
    create_read_file
)


@pytest.fixture
def sample_codebase(tmp_path):

    root = tmp_path / "codebase"
    root.mkdir()

    (root / "main.c").write_text(
        "int main() {\n"
        "    return 0;\n"
        "}\n"
    )

    (root / "device.cpp").write_text(
        "class Device {\n"
        "public:\n"
        "    void start();\n"
        "};\n"
    )

    (root / "device.h").write_text(
        "#define MAX_DEVICES 10\n"
    )

    nested = root / "modules"
    nested.mkdir()

    (nested / "network.c").write_text(
        "void connect() {}\n"
    )

    return root


@pytest.fixture
def list_files_tool(sample_codebase):

    return create_list_files(str(sample_codebase))


@pytest.fixture
def read_file_tool(sample_codebase):

    return create_read_file(
        str(sample_codebase),
        max_lines=200
    )