# -*- coding: utf-8 -*-
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# tree = ET.ElementTree(file="/home/lotaku/Desktop/test_Loc.xml")
tree = ET.ElementTree(file="LocList.xml")
# root =tree.getroot()

from collections import OrderedDict

# 可以考虑改用iter提高性能
def get_city():
    COUNTRY_CHOICES = []
    STATE_CHOICES_MAP = OrderedDict()
    CITY_CHOICES_MAP = OrderedDict()
    REGION_CHOICES_MAP = OrderedDict()
    countries = tree.findall('CountryRegion',)
    for country in countries:
        country_code = country.attrib["Code"]
        COUNTRY_CHOICES.append((country.attrib["Code"], country.attrib['Name']))
        states = country.findall('State')
        STATE_CHOICES = []
        for state in states:
            try:
                state_code = state.attrib["Code"]
                code = state.attrib["Code"]
                name = state.attrib['Name']
                STATE_CHOICES.append((code, name))
            except KeyError as e:
                #该国家没有state了，以City代替，也是最后一级了
                cities = state.findall('City')
                for city in cities:
                    code = city.attrib["Code"]
                    name = city.attrib['Name']
                    STATE_CHOICES.append((code, name))
                break

            cities = state.findall('City')
            city_list = []
            for city in cities:
                city_code = city.attrib["Code"]
                code = city.attrib["Code"]
                name = city.attrib['Name']
                city_list.append((code,name))

                regions = city.findall('Region')
                region_list = []
                for region in regions:
                    region_code = region.attrib["Code"]
                    code = region.attrib["Code"][4:]
                    if code[-1] != "0" and code[-2] == "0":
                        # print code," ",code[-1]," ",code[-2],"new:"
                        code = code.strip('0')
                    if code[-1] == "0" and code[-2] == "0":
                        code = "0"
                    name = region.attrib['Name']
                    region_list.append((code,name))
                if len(region_list):
                    REGION_CHOICES_MAP_KEY = '%s:%s:%s' % (country_code, state_code, city_code  )
                    REGION_CHOICES_MAP[REGION_CHOICES_MAP_KEY] = region_list
            if len(city_list):
                CITY_CHOICES_MAP_KEY = '%s:%s' % (country_code, state_code)
                CITY_CHOICES_MAP[CITY_CHOICES_MAP_KEY] = city_list

        if len(STATE_CHOICES):
            STATE_CHOICES_MAP[country.attrib["Code"]] = STATE_CHOICES

    # print CITY_CHOICES_MAP
    print REGION_CHOICES_MAP

    header_str ='''# -*- coding: utf-8 -*-
"""
    ISO3166 http://en.wikipedia.org/wiki/ISO_3166
"""
'''
    with open('new_address.py','w') as f:
        f.write(header_str)

        f.write("COUNTRY_CHOICES = (\n")
        for t in COUNTRY_CHOICES:
            str = '     (\'%s\',u\'%s\'),\n'% (t[0],t[1])
            f.write(str.encode('utf-8'))

        f.write("),\n")


        #写入国家：城市
        f.write("STATE_CHOICES_MAP = {\n")
        for country,states in STATE_CHOICES_MAP.items():
            # print t
            country_str ='  \'%s\': (\n' % country
            f.write(country_str.encode('utf-8'))

            for state in states:
                state_str = '      (\'%s\',u\'%s\'),\n'% (state[0],state[1])
                f.write(state_str.encode('utf-8'))

            country_end = '),\n'
            f.write(country_end.encode('utf-8'))
            # f.write("="*99+"\n")
        f.write("}\n")

        #写入 '国家：城市' : ( ('区code'，'区name'))
        f.write("CITY_CHOICES_MAP = {\n")
        for country_state,cities in CITY_CHOICES_MAP.items():
            country_state_str ='  \'%s\': (\n' % country_state
            f.write(country_state_str.encode('utf-8'))

            for city in cities:
                city_str = '      (\'%s\',u\'%s\'),\n'% (city[0],city[1])
                f.write(city_str.encode('utf-8'))

            country_state_end = '),\n'
            f.write(country_state_end.encode('utf-8'))
            # f.write("="*99+"\n")
        f.write("}\n")


        #写入 '国家：省：城市' : ( ('区code'，'区name'))
        f.write("REGION_CHOICES_MAP = {\n")
        for country_state,cities in REGION_CHOICES_MAP.items():
            country_state_str ='  \'%s\': (\n' % country_state
            f.write(country_state_str.encode('utf-8'))

            for city in cities:
                city_str = '      (\'%s\',u\'%s\'),\n'% (city[0],city[1])
                f.write(city_str.encode('utf-8'))

            country_state_end = '),\n'
            f.write(country_state_end.encode('utf-8'))
            # f.write("="*99+"\n")
        f.write("}\n")

get_city()
