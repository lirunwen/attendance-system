from extensions import db
from datetime import date, time, datetime
from sqlalchemy import Time, Date, DateTime, Boolean, Text

class Shift(db.Model):
    __tablename__ = 'shifts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    shift_start = db.Column(Time, nullable=False)
    shift_end = db.Column(Time, nullable=False)
    late_minutes = db.Column(db.Integer, default=15)
    early_leave_minutes = db.Column(db.Integer, default=15)
    is_active = db.Column(Boolean, default=True)

    def __repr__(self):
        return f'<Shift {self.name}>'

    def shift_start_str(self):
        return self.shift_start.strftime('%H:%M') if self.shift_start else ''

    def shift_end_str(self):
        return self.shift_end.strftime('%H:%M') if self.shift_end else ''


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    keywords = db.Column(db.String(256), default='')
    is_active = db.Column(Boolean, default=True)

    def __repr__(self):
        return f'<Location {self.name}>'


class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)
    shift_id = db.Column(db.Integer, db.ForeignKey('shifts.id'), nullable=True)
    is_active = db.Column(Boolean, default=True)

    shift = db.relationship('Shift', backref='employees')

    def __repr__(self):
        return f'<Employee {self.name}({self.employee_id})>'


class Record(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(32), nullable=False, index=True)
    employee_name = db.Column(db.String(64), nullable=False)
    date = db.Column(Date, nullable=False, index=True)
    punch_time = db.Column(DateTime, nullable=False)
    location_raw = db.Column(db.String(256), default='')
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    import_batch = db.Column(db.String(32), default='')

    location = db.relationship('Location', backref='records')

    def __repr__(self):
        return f'<Record {self.employee_name} {self.date} {self.punch_time}>'


class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(32), db.ForeignKey('employees.employee_id'), nullable=False, index=True)
    employee_name = db.Column(db.String(64), nullable=False)
    date = db.Column(Date, nullable=False, index=True)
    shift_id = db.Column(db.Integer, db.ForeignKey('shifts.id'), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    punch_in = db.Column(DateTime, nullable=True)
    punch_out = db.Column(DateTime, nullable=True)
    status = db.Column(db.String(32), default='normal')
    is_anomaly = db.Column(Boolean, default=False)
    clerk_remark = db.Column(Text, default='')

    shift = db.relationship('Shift', backref='attendances')
    employee = db.relationship('Employee', backref='attendances')
    location = db.relationship('Location', backref='attendances')

    __table_args__ = (
        db.UniqueConstraint('employee_id', 'date', name='uq_employee_date'),
    )

    def __repr__(self):
        return f'<Attendance {self.employee_name} {self.date} {self.status}>'
