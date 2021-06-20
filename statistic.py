import pickle
import datetime


# data : ((과목명, (강의명, 시작일자, 종료일자, P/F), ...), ...)

def get_percent(elem: int, total: int) -> float: return elem / total * 100


def pass_rate_of_total(data: tuple) -> tuple:
    pf_total = tuple(j[3] for i in data for j in i[1:])
    num_of_all = len(pf_total)
    num_of_pass = len(tuple(i for i in pf_total if i == 'P'))
    return num_of_all, num_of_pass, get_percent(num_of_pass, num_of_all)


def pass_rate_by_subjects(data: tuple) -> dict:
    pf_total = {i[0]: tuple(j[3] for j in i[1:]) for i in data}
    num_of_all_and_pass = {k: (len(v), len(tuple(j for j in v if j == 'P'))) for k, v in pf_total.items()}
    return {k: v + (get_percent(v[1], v[0]),) for k, v in num_of_all_and_pass.items()}


def get_untaken_lectures(data: tuple) -> tuple:
    now = datetime.datetime.now()
    utk_lectures = {i[0]: tuple(j[::2] for j in i[1:] if j[1] <= now <= j[2] and j[3] == 'F') for i in data}
    insert_subject_into_each = sum((tuple((k,) + i for i in v) for k, v in utk_lectures.items() if v), ())
    return tuple(sorted(insert_subject_into_each, key=lambda x: x[-1]))
