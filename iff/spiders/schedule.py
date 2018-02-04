# -*- coding: utf-8 -*-
from datetime import datetime, date, time, timedelta
import scrapy


class ScheduleSpider(scrapy.Spider):
    name = 'schedule'
    allowed_domains = ['platform.internetfreedomfestival.org']
    start_urls = ['https://platform.internetfreedomfestival.org/en/IFF2018/public/schedule/custom/']

    def parse(self, response):
        # for session in response.css('a.no_link_effect'):
        #     yield {
        #         'title': session.css('h5.session_titles::text').extract_first(),
        #         'url': session.css('::attr(href)').extract_first()
        #     }
        for session in response.css('a.no_link_effect::attr(href)'):
            # print('following session')
            yield response.follow(session, self.parse_session)
        for n in response.xpath('//input[@name="day"]'):
            next_page = response.urljoin('?day=' + n.xpath('@value').extract_first())
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_session(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first().strip()
        d = {}
        d['conf_url'] = response.url
        d['title'] = extract_with_css('h1.session_title::text')
        d['description'] = ''
        for info in response.css('div.session_info'):
            texts = info.css('::text').extract()
            k = texts[0]
            if len(texts) == 2:
                v = texts[1]
            elif len(texts) == 1:
                d['description'] += k
            k = k.strip()
            v = v.strip()
            # print(k, v)
            if k == 'Date:':
                d['date'] = datetime.strptime(v, "%A, %B  %d, %Y")
                # print(d['date'])
                day = int(d['date'].strftime("%d"))
            elif k == 'Skill Level:':
                d['level'] = v
            elif k == 'Format:':
                d['track'] = v
            elif k == 'Time:':
                start, _, end, pm = v.split()
                starth, startm = start.split(':')
                endh, endm = end.split(':')
                if pm == 'PM':
                    if int(starth) < 12:
                        starth = 12 + int(starth)
                    if int(endh) < 12:
                        endh = 12 + int(endh)
                d['start'] = datetime(2018, 3, day, int(starth), int(startm))
                enddt = datetime(2018, 3, day, int(endh), int(endm))
                duration = enddt - d['start']
                d['duration'] = ":".join(str(duration).split(':')[:2])
            elif k == 'Room:':
                d['room'] = v
            # elif k == 'Notes:':
            #     d['slides_url'] = v
            elif k == 'Presenter:':
                d['person'] = v
        # print(d)
        yield d
