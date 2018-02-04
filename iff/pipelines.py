# -*- coding: utf-8 -*-
from datetime import datetime
import json
from scrapy.exporters import XmlItemExporter
from pentabarf import PentabarfParser

class PentabarfXmlExportPipeline(object):
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

    def open_spider(self, spider):
        self.conference = PentabarfParser.Conference(
                'IFF2018', city='Valencia',
                start=datetime(2018, 3, 5), end=datetime(2018, 3, 9))
        self.days = {}

    def close_spider(self, spider):
        personid = 0
        eventid = 0
        speakers = []
        for d, rooms in self.days.items():
            print(d)
            pday = PentabarfParser.Day(d)
            for r, events in rooms.items():
                print(r)
                proom = PentabarfParser.Room(r)
                for e in events:
                    print(e)
                    pevent = PentabarfParser.Event(eventid)
                    eventid += 1
                    pevent.conf_url = e.get('conf_url')
                    pevent.date = e.get('start')
                    pevent.start = e.get('start').strftime("%H:%M")
                    pevent.duration = e.get('duration')
                    pevent.track = e.get('track')
                    pevent.level = e.get('level')
                    pevent.title = e.get('title')
                    pevent.description = e.get('description')
                    print(pevent)
                    p = e.get('person')
                    speakers.append({"id": personid, "name": p})
                    pperson = PentabarfParser.Person(personid, p)
                    personid += 1
                    pevent.add_person(pperson)
                    proom.add_event(pevent)
                pday.add_room(proom)
            self.conference.add_day(pday)
        xml = self.conference.generate().decode('utf-8')
        self.file = open('pentabarf_schedule.xml', 'w')
        self.file.write(xml)
        self.file.close()
        self.file = open('pentabarf_speakers.json', 'w')
        self.file.write(json.dumps(speakers, indent=2))
        self.file.close()


    def _exporter_for_item(self, item):
        day = item['date']
        room = item['room']
        if self.days.get(day) is None:
            self.days[day] = {room: [item]}
        elif self.days[day].get(room) is None:
            self.days[day][room] = [item]
        else:
            self.days[day][room].append(item)

    def process_item(self, item, spider):
        self._exporter_for_item(item)
        return item
