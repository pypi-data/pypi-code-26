from powerschool_alchemy.db import create_session
from powerschool_alchemy.models import Section, CalendarDay, CC, CycleDay
sess = create_session()
my_section = sess.query(Section).filter(Section.id==149618).first()

section_cal_days = sess \
            .query(CalendarDay, CycleDay.letter) \
            .join(CycleDay) \
            .filter(
                CalendarDay.school_id==my_section.school_id, 
                CalendarDay.date_value >= my_section.date_enrolled, 
                CalendarDay.date_value < my_section.date_left,
                CycleDay.letter.in_(
                    list(map(lambda x: x.cycle_day_letter, my_section.section_meetings)))) \
            .all()
print(section_cal_days)