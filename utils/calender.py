from calendar import LocaleHTMLCalendar
from itertools import groupby
from django.utils.datetime_safe import date
from openebs2.settings import CALENDAR_LOCALE


class CountCalendar(LocaleHTMLCalendar):

    def __init__(self, items):
        super(CountCalendar, self).__init__(0, CALENDAR_LOCALE)
        self.counts = self.group_by_day(items)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            day_date = date(self.year, self.month, day)
            if date.today() == day_date:
                cssclass += ' today'
            if day_date in self.counts:
                cssclass += ' filled'
                body = ['<ul>']
                for item in self.counts[day_date]:
                    body.append('<li>')
                    body.append(str(item['dcount']))
                    body.append('</li>')
                body.append('</ul>')
                return self.day_cell(cssclass, '<span class="day">%d</span> %s' % (day, ''.join(body)))
            return self.day_cell(cssclass, '<span class="day">%d</span>' % day)
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month, **kwargs):
        self.year, self.month = year, month
        return super(CountCalendar, self).formatmonth(year, month)

    def group_by_day(self, items):
        field = lambda item: item['date']
        return dict(
            [(day, list(items)) for day, items in groupby(items, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)
