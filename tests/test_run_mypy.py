import os
import pytest
from mypy import api
from typing import List, Tuple, TypedDict


class Expect(TypedDict):
    normal: str
    error: str
    exit_status: int


case_directory = os.path.join(os.path.dirname(__file__), "cases")

cases: List[Tuple[str, Expect]] = [
    (
        "from_readme.py",
        Expect(
            normal="""
                error: Key 'awesome' missing for TypedDict "FooSchema" 
                note: Revealed type is 'TypedDict('FooSchema', {'title'?: builtins.str, 'awesome': builtins.int})'
                error: TypedDict "FooSchema" has no key 'description'
                error: Argument 2 has incompatible type "None"; expected "int"
            """,
            error="""""",
            exit_status=1,
        ),
    )
]


@pytest.mark.parametrize("case_file, expected", cases)
def test_this(case_file: str, expected: Expect):
    normal_report, error_report, exit_status = api.run(
        [os.path.join(case_directory, case_file)]
    )
    for line in expected["normal"].strip().splitlines():
        assert line.strip() in normal_report
    for line in expected["error"].strip().splitlines():
        assert line.strip() in error_report
    assert exit_status == expected["exit_status"]
