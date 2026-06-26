"""E2E test for Attendance System"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))

from openpyxl import Workbook
import requests

BASE = 'http://127.0.0.1:5100'
s = requests.Session()

# Login first (system now requires auth)
s.post(f'{BASE}/login', data={'username': 'admin', 'password': 'admin123'})

ok = total = 0

def check(name, cond):
    global ok, total
    total += 1
    if cond:
        ok += 1
        print(f'  ✓ {name}')
    else:
        print(f'  ✗ {name}')

# 1. Add shift
r = s.post(f'{BASE}/shifts/save', data={
    'name': '白班', 'shift_start': '09:00', 'shift_end': '18:00',
    'late_minutes': 15, 'early_leave_minutes': 15
})
check('Add shift', '班次已新增' in r.text)

# 2. Add location
r = s.post(f'{BASE}/locations/save', data={'name': '主楼', 'keywords': '主楼,大厅'})
check('Add location', '地点已新增' in r.text)

# 3. Add employees
r = s.post(f'{BASE}/employees/save', data={'employee_id': 'EMP001', 'name': '张三', 'shift_id': '1'})
check('Add emp1', '员工已新增' in r.text)
r = s.post(f'{BASE}/employees/save', data={'employee_id': 'EMP002', 'name': '李四', 'shift_id': '1'})
check('Add emp2', '员工已新增' in r.text)

# 4. Generate test Excel
wb = Workbook()
ws = wb.active
ws.append(['姓名', '工号', '日期', '打卡时间', '打卡地点'])
ws.append(['张三', 'EMP001', '2026-06-15', '2026-06-15 08:55:00', '主楼'])
ws.append(['张三', 'EMP001', '2026-06-15', '2026-06-15 18:02:00', '主楼'])
ws.append(['张三', 'EMP001', '2026-06-16', '2026-06-16 09:20:00', '主楼'])
ws.append(['张三', 'EMP001', '2026-06-16', '2026-06-16 18:05:00', '主楼'])
ws.append(['李四', 'EMP002', '2026-06-15', '2026-06-15 08:58:00', '大厅'])
ws.append(['李四', 'EMP002', '2026-06-16', '2026-06-16 09:01:00', '大厅'])

tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
wb.save(tmp.name)

# 5. Import
with open(tmp.name, 'rb') as f:
    r = s.post(f'{BASE}/import/upload', files={'file': f})
check('Import data', '导入记录' in r.text or '统计天数' in r.text)
os.unlink(tmp.name)

# 6. Check attendance
r = s.get(f'{BASE}/attendance?month=2026-06')
check('Attendance shows Zhang San', '张三' in r.text)

# 7. Check anomalies
r = s.get(f'{BASE}/anomalies')
check('Anomalies page loaded', r.status_code == 200)
check('Late detected', '迟到' in r.text)

# 8. Check statistics
r = s.get(f'{BASE}/statistics?month=2026-06')
check('Statistics page loaded', r.status_code == 200)

# 9. Verify specific attendance data via the API
r = s.get(f'{BASE}/attendance?month=2026-06')
# Zhang San on 6/15 should be normal (08:55 < 09:15)
# Zhang San on 6/16 should be late (09:20 > 09:15)
# Li Si on 6/16 should be no_punch_out (only 1 punch)
check('Normal day mark', '✓' in r.text)
check('Late day mark', '迟' in r.text)
check('Missing punch mark', '↓' in r.text)

# 10. Download template
r = s.get(f'{BASE}/import/template')
check('Download template', r.status_code == 200 and r.headers.get('content-type', '').startswith('application'))

# 11. Add remark on anomaly
r = s.get(f'{BASE}/anomalies')
# Find first anomaly ID and try to save remark
import re
ids = re.findall(r'/anomalies/(\d+)/remark', r.text)
if ids:
    aid = ids[0]
    r = s.post(f'{BASE}/anomalies/{aid}/remark', data={'clerk_remark': '已确认，事假补卡'})
    check('Save remark', '备注已保存' in r.text)

print(f'\n=== {ok}/{total} tests passed ===')
