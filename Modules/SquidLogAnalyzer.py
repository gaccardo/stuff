#!/usr/bin/evn python
# -*- coding: utf-8 -*-


class Squid(object):  # lint:ok

    def __init__(self, accesslog):
        self.accesslog = accesslog

    def __readAccessLog(self):
        pointer = open(self.accesslog, 'r')
        ac_buffer = pointer.readlines()
        pointer.close()

        return ac_buffer

    def __getSources(self, ac_buffer):
        sources = list()

        for line in ac_buffer:
            line = line.split(' ')
            line = [i for i in line if i]
            source = line[2]
            sources.append(source)

        return sources

    def __sourceExists(self, sources, ip):
        if ip in sources:
            return True

        return False

    def __makeUniqueSources(self, sources):
        unique = list()

        for source in sources:
            if not self.__sourceExists(sources, source):
                unique.append(source)

        return unique

    def __getRequestsByIP(self, ac_buffer, sources, ip):
        if self.__sourceExists(sources, ip):
            requests = list()

            for line in ac_buffer:
                line2 = line.split(' ')
                line2 = [i for i in line2 if i]
                source = line2[2]

                if source == ip:
                    requests.append(line)

            return requests

    def __bandwidthPerIPHits(self, ac_buffer, sources, ip):
        band_hits = 0
        band_miss = 0
        cont_hits = 0
        cont_miss = 0
        requests = self.__getRequestsByIP(ac_buffer, sources, ip)

        if requests is not None:
            for request in requests:
                request = request.split(' ')
                request = [i for i in request if i]

                if request[3] == 'TCP_MISS/304':
                    band_miss += int(request[1])
                    cont_miss += 1
                else:
                    band_hits += int(request[1])
                    cont_hits += 1

        total = cont_hits + cont_miss

        if total <= 0:
            band_miss = 0
            band_hits = 0
            m_unit = 'B'
            h_unit = 'B'
            cont_miss = 0
            cont_hits = 0
            percent_miss = 0
            percent_hits = 0
        else:
            percent_miss = float((cont_miss * 100) / total)
            percent_hits = float((cont_hits * 100) / total)

        if band_miss <= 10000000:
            m_unit = 'B'
        elif band_miss > 10000000 and band_miss <= 1000000000:
            band_miss = float(band_miss) / 1024 / 1024
            m_unit = 'MB'
        elif band_miss > 1000000000:
            band_miss = float(band_miss) / 1024 / 1024 / 1024
            m_unit = 'GB'

        if band_hits <= 10000000:
            h_unit = 'B'
        elif band_hits > 10000000 and band_hits <= 1000000000:
            band_hits = float(band_hits) / 1024 / 1024
            h_unit = 'MB'
        elif band_hits > 1000000000:
            band_hits = float(band_hits) / 1024 / 1024 / 1024
            h_unit = 'GB'

        return {'hitscount': cont_hits, 'misscount': cont_miss,
                'bandwidthhits': band_hits, 'bandwidthmiss': band_miss,
                'percenthits':"%%%.2f" % percent_hits,
                'percentmiss':"%%%.2f" % percent_miss, 'miss_unit':m_unit,
                'hits_unit':h_unit, 'requests':total }

    def __bandwidthPerIP(self, ac_buffer, sources, ip):
        bandwidth = 0
        requests = self.__getRequestsByIP(ac_buffer, sources, ip)

        if requests is not None:
            for request in requests:
                request = request.split(' ')
                request = [i for i in request if i]
                request = request[1]
                bandwidth += int(request)
        else:
            return {'count': "%.2f" % 0, 'unit': 'B'}

        if bandwidth <= 10000000:
            bandwidth = {'count': "%.2f" % float(bandwidth), 'unit': 'B'}
        elif bandwidth > 10000000 and bandwidth <= 1000000000:
            bandwidth = {'count': "%.2f" % (float(bandwidth) / 1024 / 1024),
                         'unit': 'MB'}
        elif bandwidth > 1000000000:
            bandwidth = {'count': "%.2f" % (float(bandwidth)
                                            / 1024 / 1024 / 1024),
                         'unit': 'GB'}

        return bandwidth

    def run(self):
        ac_buffer = self.__readAccessLog()
        sources = self.__getSources(ac_buffer)
        #bandwidth = self.__bandwidthPerIP(ac_buffer, sources, '10.2.10.12')
        bandwidth = self.__bandwidthPerIPHits(ac_buffer, sources, '10.2.40.20')

        print bandwidth


if __name__ == '__main__':
    squid = Squid('access.log')
    squid.run()
