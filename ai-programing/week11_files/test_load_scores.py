import pytest
from load_scores import load_scores


def test_정상_파일을_읽는다(tmp_path):
    p = tmp_path / "normal.csv"
    p.write_text("이름,점수\n김철수,85\n이영희,92\n박민수,78\n", encoding="utf-8")

    kept, skipped = load_scores(p)

    assert kept == [("김철수", 85), ("이영희", 92), ("박민수", 78)]
    assert skipped == []


def test_빈_줄은_건너뛴다(tmp_path):
    p = tmp_path / "blank_lines.csv"
    p.write_text("이름,점수\n김철수,85\n\n이영희,92\n\n", encoding="utf-8")

    kept, skipped = load_scores(p)

    assert kept == [("김철수", 85), ("이영희", 92)]
    assert skipped == []


def test_이름에_쉼표가_있어도_읽는다(tmp_path):
    p = tmp_path / "comma_name.csv"
    p.write_text('이름,점수\n"Kim, Chulsoo",90\n', encoding="utf-8")

    kept, skipped = load_scores(p)

    assert kept == [("Kim, Chulsoo", 90)]
    assert skipped == []


def test_없는_파일이면_오류가_난다(tmp_path):
    missing = tmp_path / "no_such_file.csv"

    with pytest.raises(FileNotFoundError):
        load_scores(missing)


def test_헤더만_있으면_빈_결과(tmp_path):
    p = tmp_path / "header_only.csv"
    p.write_text("이름,점수\n", encoding="utf-8")

    kept, skipped = load_scores(p)

    assert (kept, skipped) == ([], [])


def test_점수가_비어_있으면_건너뛰기_기록(tmp_path):
    p = tmp_path / "empty_score.csv"
    p.write_text("이름,점수\n이영희,\n", encoding="utf-8")

    kept, skipped = load_scores(p)

    assert kept == []
    assert skipped == [(2, "이영희,", "점수가 비어 있음")]


def test_같은_이름도_모두_보존한다(tmp_path):
    p = tmp_path / "duplicate_names.csv"
    p.write_text("이름,점수\n김민수,85\n김민수,92\n", encoding="utf-8")

    kept, skipped = load_scores(p)

    assert kept == [("김민수", 85), ("김민수", 92)]
    assert skipped == []


@pytest.mark.parametrize(
    "score, valid",
    [
        (-1, False),
        (0, True),
        (1, True),
        (99, True),
        (100, True),
        (101, False),
    ],
)
def test_점수_경계값(tmp_path, score, valid):
    p = tmp_path / "boundary.csv"
    p.write_text(f"이름,점수\n홍길동,{score}\n", encoding="utf-8")

    kept, skipped = load_scores(p)

    assert (len(kept) == 1) == valid
    if valid:
        assert kept == [("홍길동", score)]
        assert skipped == []
    else:
        assert kept == []
        assert skipped == [(2, f"홍길동,{score}", "점수가 0~100 밖")]


def test_누락_분기_건너뛰기_기록(tmp_path):
    p = tmp_path / "invalid_rows.csv"
    p.write_text(
        "이름,점수\n"
        ",85\n"
        "이영희,abc\n"
        "박민수,90,추가열\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(p)

    assert kept == []
    assert skipped == [
        (2, ",85", "이름이 비어 있음"),
        (3, "이영희,abc", "점수가 정수가 아님"),
        (4, "박민수,90,추가열", "열 개수가 2가 아님"),
    ]
   

