from datetime import datetime, timedelta, time as dtime
from models import Attendance, Record, Shift, Employee
from extensions import db


def build_attendance_for_date(emp_id, target_date):
    """对某个员工某天的打卡记录计算考勤"""
    from collections import defaultdict

    records = Record.query.filter_by(employee_id=emp_id, date=target_date).order_by(Record.punch_time).all()
    if not records:
        return None

    # 获取员工信息
    emp = Employee.query.filter_by(employee_id=emp_id).first()
    if not emp:
        return None

    # 确定班次：员工自定义班次 → 第一条记录匹配时间段 → 默认白班
    shift = None
    if emp.shift_id:
        shift = Shift.query.get(emp.shift_id)
    if not shift:
        # 尝试根据打卡时间推断班次
        shifts = Shift.query.filter_by(is_active=True).order_by(Shift.id).all()
        if shifts:
            shift = shifts[0]  # 取第一个有效班次
        else:
            # 默认白班
            class DefaultShift:
                name = '默认'
                shift_start = dtime(9, 0)
                shift_end = dtime(18, 0)
                late_minutes = 15
                early_leave_minutes = 15
                id = None
            shift = DefaultShift()

    # 首条 = 上班卡, 末条 = 下班卡
    punch_in = records[0].punch_time
    punch_out = records[-1].punch_time if len(records) > 1 else None

    # 确定地点（取次数最多的地点）
    loc_counts = defaultdict(int)
    loc_id = None
    for r in records:
        if r.location_id:
            loc_counts[r.location_id] += 1
    if loc_counts:
        loc_id = max(loc_counts, key=loc_counts.get)

    # 判断状态
    status = 'normal'
    is_anomaly = False

    # 构建参考时间
    ref_start = datetime.combine(target_date, shift.shift_start)
    ref_end = datetime.combine(target_date, shift.shift_end)

    # 如果是夜班（结束时间在开始之后且跨午夜），下班参考+1天
    if shift.shift_start and shift.shift_end and shift.shift_end <= shift.shift_start:
        ref_end = ref_end + timedelta(days=1)
        if punch_out and punch_out < ref_start:
            ref_start = ref_start - timedelta(days=1)

    has_punch_in = punch_in is not None
    has_punch_out = punch_out is not None

    if not has_punch_in and not has_punch_out:
        status = 'absent'
        is_anomaly = True
    elif not has_punch_in:
        status = 'no_punch_in'
        is_anomaly = True
    elif not has_punch_out:
        status = 'no_punch_out'
        is_anomaly = True
    else:
        late_by = (punch_in - ref_start).total_seconds() / 60 - shift.late_minutes
        early_by = (ref_end - punch_out).total_seconds() / 60 - shift.early_leave_minutes

        is_late = late_by > 0
        is_early = early_by > 0

        if is_late and is_early:
            status = 'both'
            is_anomaly = True
        elif is_late:
            status = 'late'
            is_anomaly = True
        elif is_early:
            status = 'early_leave'
            is_anomaly = True

    # 更新或创建 Attendance 记录
    att = Attendance.query.filter_by(employee_id=emp_id, date=target_date).first()
    if att:
        att.punch_in = punch_in
        att.punch_out = punch_out
        att.shift_id = shift.id if hasattr(shift, 'id') else None
        att.location_id = loc_id
        att.status = status
        att.is_anomaly = is_anomaly
    else:
        att = Attendance(
            employee_id=emp_id,
            employee_name=records[0].employee_name,
            date=target_date,
            shift_id=shift.id if hasattr(shift, 'id') else None,
            location_id=loc_id,
            punch_in=punch_in,
            punch_out=punch_out,
            status=status,
            is_anomaly=is_anomaly,
        )
        db.session.add(att)

    db.session.commit()
    return att


def recalc_all(batch=None):
    """重新计算所有打卡记录（可按批次）"""
    if batch:
        records = Record.query.filter_by(import_batch=batch).all()
    else:
        records = Record.query.all()

    date_emp_set = set()
    for r in records:
        date_emp_set.add((r.employee_id, r.date))

    results = []
    for emp_id, d in sorted(date_emp_set):
        att = build_attendance_for_date(emp_id, d)
        if att:
            results.append(att)
    return results
