"""Packs the five made-up athletes into src/data.js for the prototype page.

Calendars: Annie's is the existing capstone file (personas/annie/calendar.csv) with an Id added to
each workout. The other four are written here from compact specs and saved as calendar.csv in their
persona folders. Every other file (memory, plan, Garmin-style exports) is read from personas/<name>/.
Every name, event and number is fictional. Run:  python3 -I make_data.py
"""
import csv
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CAPSTONE = os.path.abspath(os.path.join(HERE, '..', '..'))
HEAD = ['Id', 'Name', 'Start', 'End', 'Type', 'Recurring', 'Notes']


def at(md, hm):
    return '2026-%s %s' % (md, hm)


class Cal:
    def __init__(self):
        self.rows = []

    def ev(self, name, start, end, typ, rec='', notes='', id=''):
        self.rows.append([id, name, start, end, typ, rec, notes])

    def days(self, mds, name, t1, t2, typ, rec='', notes=''):
        for md in mds:
            self.ev(name, at(md, t1), at(md, t2), typ, rec, notes)

    def workout(self, prefix, md, t1, t2, name, notes=''):
        self.ev(name, at(md, t1), at(md, t2), 'Workout', 'Plan', notes, '%s-%s' % (prefix, md.replace('-', '')))

    def csv(self):
        rows = sorted(self.rows, key=lambda r: (r[2], r[3]))
        out = io.StringIO()
        writer = csv.writer(out, lineterminator='\n')
        writer.writerow(HEAD)
        writer.writerows(rows)
        return out.getvalue().strip('\n')


def annie():
    cal = Cal()
    with open(os.path.join(CAPSTONE, 'personas', 'annie', 'calendar.csv'), newline='') as handle:
        for row in csv.DictReader(handle):
            ident = ''
            if row['Type'] == 'Workout':
                ident = 'A-' + row['Start'][5:10].replace('-', '')
            cal.ev(row['Name'], row['Start'], row['End'], row['Type'], row['Recurring'], row['Notes'], ident)
    return cal


def greg():
    cal = Cal()
    weekdays = ['10-05', '10-06', '10-07', '10-08', '10-09', '10-12', '10-13', '10-14', '10-15', '10-16']
    cal.days(weekdays, 'Work (from home)', '07:30', '16:00', 'Work', 'Weekdays')
    cal.days(['10-06', '10-08', '10-13', '10-15'], "Drive kids to activities", '17:00', '19:00', 'Family', 'Tue, Thu')
    cal.days(['10-10', '10-17'], 'Family lunch', '12:30', '14:00', 'Family', 'Saturdays')
    cal.days(['10-11', '10-18'], 'Groceries', '10:00', '11:00', 'Family', 'Sundays')
    for week in (('10-06', '10-07', '10-08', '10-09', '10-10', '10-11', 'Ride: Long 3 h', '10:00'),
                 ('10-13', '10-14', '10-15', '10-16', '10-17', '10-18', 'Ride: Long 3 h 15 min', '10:15')):
        tue, wed, thu, fri, sat, sun, long_name, long_end = week
        cal.workout('G', tue, '06:00', '07:00', 'Ride: Intervals 60 min', 'Indoor trainer. See plan for intervals.')
        cal.workout('G', wed, '05:45', '06:35', 'YMCA: Strength A', 'See plan for sets.')
        cal.workout('G', thu, '06:00', '07:15', 'Ride: Endurance 75 min', 'Zone 2, steady.')
        cal.workout('G', fri, '05:45', '06:35', 'YMCA: Strength B', 'See plan for sets.')
        cal.workout('G', sat, '07:00', long_end, long_name, 'Key session.')
        cal.workout('G', sun, '08:00', '08:45', 'Ride: Recovery spin 45 min (optional)', 'Very easy.')
    return cal


def dora():
    cal = Cal()
    cal.days(['10-05', '10-06', '10-07', '10-08', '10-09'], 'Work', '08:30', '17:00', 'Work', 'Weekdays')
    sessions = {
        'Mon': ('06:00', '07:15', 'Gym: Olympic lifting + back squat'),
        'Tue': ('06:00', '07:00', 'Gym: Metcon + rowing intervals'),
        'Wed': ('06:00', '07:00', 'Gym: Gymnastics + accessories'),
        'Thu': ('06:00', '07:15', 'Gym: Heavy deadlift + press + sled'),
        'Fri': ('06:00', '07:00', 'Gym: Competition-style workout'),
        'Sat': ('08:00', '09:00', 'Gym: Long aerobic + skill'),
    }
    plan = [('10-05', 'Mon'), ('10-06', 'Tue'), ('10-07', 'Wed'), ('10-08', 'Thu'), ('10-09', 'Fri'), ('10-10', 'Sat'),
            ('10-12', 'Mon'), ('10-13', 'Tue'), ('10-14', 'Wed'), ('10-15', 'Thu'), ('10-16', 'Fri'), ('10-17', 'Sat'),
            ('10-19', 'Mon'), ('10-20', 'Tue'), ('10-21', 'Wed'), ('10-22', 'Thu'), ('10-23', 'Fri'), ('10-24', 'Sat')]
    for md, day in plan:
        t1, t2, name = sessions[day]
        note = 'Planned before the trip was booked.' if '10-10' <= md <= '10-23' else ''
        cal.workout('D', md, t1, t2, name, note)
    cal.ev('Flights: home to Hanoi (via Seoul)', at('10-10', '06:30'), at('10-11', '21:00'), 'Travel', '',
           'About 22 h door to door. Vietnam is 14 hours ahead of home. Times are local at each end.')
    cal.ev('Family: Hanoi Old Quarter and food tour', at('10-12', '08:30'), at('10-12', '20:00'), 'Family')
    cal.ev('Family: Ha Long Bay day trip', at('10-13', '07:00'), at('10-13', '20:00'), 'Family', '', 'Bus pickup at the hotel at 7:00 am.')
    cal.ev('Family: museums and water puppet show', at('10-14', '08:30'), at('10-14', '20:00'), 'Family')
    cal.ev('Flight: Hanoi to Da Nang, drive to Hoi An', at('10-15', '07:00'), at('10-15', '13:00'), 'Travel', '', 'Leave the hotel at 7:00 am.')
    cal.ev('Family: Hoi An old town', at('10-15', '15:00'), at('10-15', '20:00'), 'Family')
    cal.ev('Family: cooking class and beach', at('10-16', '08:30'), at('10-16', '20:00'), 'Family')
    cal.ev('Family: My Son day trip', at('10-17', '08:30'), at('10-17', '19:00'), 'Family')
    cal.ev('Family: lantern evening', at('10-18', '16:00'), at('10-18', '21:00'), 'Family')
    cal.ev('Flight: Da Nang to Ho Chi Minh City', at('10-19', '07:00'), at('10-19', '12:30'), 'Travel', '', 'Leave the hotel at 7:00 am.')
    cal.ev('Family: city afternoon', at('10-19', '14:00'), at('10-19', '20:00'), 'Family')
    cal.ev('Family: Cu Chi tunnels', at('10-20', '08:30'), at('10-20', '18:00'), 'Family')
    cal.ev('Family: Mekong Delta day trip', at('10-21', '07:30'), at('10-21', '19:00'), 'Family', '', 'Bus pickup at 7:30 am.')
    cal.ev('Family: markets and farewell dinner', at('10-22', '08:30'), at('10-22', '21:00'), 'Family')
    cal.ev('Flights: Ho Chi Minh City to home (via Seoul)', at('10-23', '07:30'), at('10-23', '18:00'), 'Travel', '',
           'About 22 h door to door. Times are local at each end.')
    cal.ev('Family: unpack and groceries', at('10-24', '10:00'), at('10-24', '12:00'), 'Family')
    return cal


def marcus():
    cal = Cal()
    cal.days(['10-05', '10-06', '10-07', '10-08', '10-09'], 'Work (office)', '08:00', '17:00', 'Work', 'Weekdays', 'Includes commute')
    cal.workout('M', '10-05', '06:00', '06:45', 'Swim: 2,400 yd', 'Pool.')
    cal.workout('M', '10-06', '18:00', '19:00', 'Bike: Intervals 60 min', 'Trainer.')
    cal.workout('M', '10-07', '05:45', '06:40', 'Run: Tempo 6.5 mi', 'See plan for pace.')
    cal.workout('M', '10-08', '06:00', '07:00', 'Swim + strength 60 min', 'Pool, then core.')
    cal.workout('M', '10-09', '06:00', '06:40', 'Bike: Easy spin 40 min', '')
    cal.workout('M', '10-10', '07:00', '08:55', 'Run: Long 12 mi', 'Keep on Saturday morning.')
    cal.workout('M', '10-11', '07:00', '09:55', 'Brick: Ride 2 h 30 min + run 3 mi', 'Key session.')
    cal.ev('Dinner with friends', at('10-09', '19:00'), at('10-09', '21:30'), 'Family')
    cal.ev("Kids' swim lesson", at('10-10', '10:00'), at('10-10', '11:00'), 'Family', 'Saturdays')
    cal.ev('Family brunch', at('10-11', '11:00'), at('10-11', '12:30'), 'Family')
    return cal


def leo():
    cal = Cal()
    cal.days(['10-05', '10-06', '10-08', '10-09'], 'Launch: APAC customer calls', '05:30', '07:00', 'Work', 'Launch week')
    cal.ev('Launch: APAC customer calls', at('10-07', '05:30'), at('10-07', '06:40'), 'Work', 'Launch week')
    cal.days(['10-05', '10-06', '10-07', '10-08', '10-09'], 'Launch: war room', '07:00', '22:30', 'Work', 'Launch week')
    cal.ev('Training window (20 min)', at('10-07', '06:40'), at('10-07', '07:00'), 'Availability', '', 'Held by Leo. One of two training windows this week.')
    cal.ev('Launch: on-call handover', at('10-10', '06:00'), at('10-10', '07:30'), 'Work', 'Launch week')
    cal.ev('Training window (20 min)', at('10-10', '07:30'), at('10-10', '07:50'), 'Availability', '', 'Held by Leo. One of two training windows this week.')
    cal.ev('Launch: support rotation', at('10-10', '07:50'), at('10-10', '22:00'), 'Work', 'Launch week')
    cal.ev('Launch: on call and retro', at('10-11', '06:00'), at('10-11', '22:30'), 'Work', 'Launch week')
    cal.workout('L', '10-05', '06:30', '07:30', 'Gym: Strength A', 'Trap-bar deadlift day.')
    cal.workout('L', '10-06', '06:30', '07:15', 'Run: Intervals 45 min', 'See plan for reps.')
    cal.workout('L', '10-08', '19:00', '19:50', 'Run: Easy 50 min', '')
    cal.workout('L', '10-09', '06:30', '07:30', 'Gym: Strength B', '')
    cal.workout('L', '10-11', '08:00', '09:15', 'Run: Long 75 min', '')
    return cal


FILES = ['memory.md', 'workout-plan.md', 'garmin-activities.csv', 'garmin-daily-wellness.csv']


def main():
    data = {}
    for name, build in (('annie', annie), ('greg', greg), ('dora', dora), ('marcus', marcus), ('leo', leo)):
        folder = os.path.join(CAPSTONE, 'personas', name)
        text = build().csv()
        if name != 'annie':
            with open(os.path.join(folder, 'calendar.csv'), 'w') as handle:
                handle.write(text + '\n')
        files = {'calendar.csv': text}
        for file in FILES:
            with open(os.path.join(folder, file)) as handle:
                files[file.replace('garmin-daily-wellness', 'garmin-wellness')] = handle.read().strip('\n')
        data[name] = files
        print('%-7s calendar rows: %d' % (name, text.count('\n')))
    lines = ['// Made-up athlete files, one set per athlete. Built by make_data.py from capstone/personas; edit those, not this.',
             'var PERSONA_FILES = ' + json.dumps(data, indent=1, ensure_ascii=False) + ';', '']
    with open(os.path.join(HERE, 'data.js'), 'w') as handle:
        handle.write('\n'.join(lines))


main()
