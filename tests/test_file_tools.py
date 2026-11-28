import pytest

from tools.file_tools import create_list_files
from utils.path_utils import check_is_valid_path

@pytest.mark.parametrize(("invalid_path","file_required"), [("does_not_exist",False),
                          ("/etc", False),
                          ("../modules", False),
                          ("modules.c", True)])
def test_check_is_valid_path_returns_false(tmp_path, invalid_path, file_required):
    success, reason=check_is_valid_path(invalid_path, tmp_path, file_required)

    assert success is False
    assert isinstance(reason, str)
    assert len(reason)>0

def test_list_files_returns_files(list_files_tool):

    result = list_files_tool(".")

    assert isinstance(result, str)

    assert "main.c" in result
    assert "device.cpp" in result
    assert "device.h" in result


def test_list_files_finds_nested_files(list_files_tool):

    result = list_files_tool(".")

    assert "network.c" in result


def test_list_files_returns_sorted_results(list_files_tool):

    result = list_files_tool(".")

    filenames = result.splitlines()

    assert filenames == sorted(filenames)


def test_list_files_empty_directory(
    tmp_path
):

    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    list_files = create_list_files(str(empty_dir))

    result = list_files(".")

    assert result == ""

@pytest.mark.parametrize("invalid_path",
                         ["does_not_exist",
                          "/etc",
                          "../modules",
                          "modules.c"])
def test_list_files_invalid_path(list_files_tool, invalid_path):

    result = list_files_tool(invalid_path)

    assert isinstance(result, str)
    assert len(result)>0

    # Tighten this assertion using the exact error
    # returned by check_is_valid_path().

@pytest.mark.parametrize(("invalid_path", "start", "end"),
                         [
                             ("etc", 1, None),
                             ("../opt", 1, 25),
                             ("/os", 25, 2),
                             ("module", 2, 53),
                             ("module.c", 1, 25)
                         ])
def test_read_files_invalid_paths(read_file_tool, invalid_path, start, end):
    result=read_file_tool(invalid_path, start, end)
    print(result)
    assert isinstance(result, str)
    assert len(result)>0