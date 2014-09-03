# -*- coding: utf-8 -*-
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# tree = ET.ElementTree(file="/home/lotaku/Desktop/test_Loc.xml")
tree = ET.ElementTree(file="LocList.xml")
# root =tree.getroot()

from collections import OrderedDict

# print tuple(COUNTRY_CHOICES)

#解析国家
def get_county():
    COUNTRY_CHOICES = []
    for child_of_root in tree.iter(tag='CountryRegion'):
        COUNTRY_CHOICES.append((child_of_root.attrib['Code'],child_of_root.attrib['Name']))

    with open('new_address.py','w') as f:
        f.write("COUNTRY_CHOICES = (\n")
        for t in COUNTRY_CHOICES:
            str = '     (\'%s\',u\'%s\'),\n'% (t[0],t[1])
            f.write(str.encode('utf-8'))

        f.write("),\n")

        # #写入国家：城市
        # f.write("STATE_CHOICES_MAP = {\n")
        # for country,states in STATE_CHOICES_MAP.items():
        #     # print t
        #     country_str ='  \'%s\': (\n' % country
        #     f.write(country_str.encode('utf-8'))
        #
        #     for state in states:
        #         state_str = '      (\'%s\',u\'%s\'),\n'% (state[0],state[1])
        #         f.write(state_str.encode('utf-8'))
        #
        #     country_end = '),\n'
        #     f.write(country_end.encode('utf-8'))
        #     # f.write("="*99+"\n")
        # f.write("}\n")



# get_county()
# STATE_CHOICEeS_MAP = {
#     '1': (
#         ('11', u'北京'),
#         ('12', u'天津'),
#         ('13', u'河北'),
#         ('14', u'山西'),

def get_province():
    COUNTRY_CHOICES = []
    STATE_CHOICES_MAP = OrderedDict()
    countries = tree.findall('CountryRegion',)
    for country in countries:
        COUNTRY_CHOICES.append((country.attrib["Code"], country.attrib['Name']))
        states = country.findall('State')
        STATE_CHOICES = []
        for state in states:
            try:
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


        STATE_CHOICES_MAP[country.attrib["Code"]] = STATE_CHOICES
    header_str ='''# -*- coding: utf-8 -*-
"""
    ISO3166 http://en.wikipedia.org/wiki/ISO_3166
"""
'''
    with open('new_address.py','w') as f:
        f.write(header_str)
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
        f.write("}")


# get_province()
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
            # cities = state.findall('City')
            # for city in cities:
            #     regions = city.findall('Region')

    # print dir(STATE_CHOICES_MAP)
    # for node in tree.iter():
    #     country_nodes = tree.find('/', '')
        # print county.tag, county.attrib
        # state_list = []
        # county_code = ''
        # if node.tag == 'CountryRegion':
        #     # print node.attrib['Code'],node.attrib['Name']
        #     if county_code != node.attrib['Code']:
        #         county_code = node.attrib['Code']
        # if node.tag == 'State':
        #     # print node.attrib['Code'],node.attrib['Name']
        #     state_list.append((node.attrib['Code'],node.attrib['Name']))

        # if node.tag == 'City':
        #     print node.attrib['Code'],node.attrib['Name']
        # if node.tag == 'Region':
        #     print node.attrib['Code'],node.attrib['Name']



    #     county_code = county.attrib['Code']
    #
    #     city_list = []
    #     for city in tree.iterfind('CountryRegion/State'):
    #
    #         # print type(city.attrib)
    #
    #         city_code = city.attrib.get('Code','')
    #         city_name = city.attrib.get('Name','')
    #         city_tuple = (city_code, city_name)
    #         city_list.append(city_tuple)
    #
    #     STATE_CHOICES_MAP[county_code]=city_list
    #
    # # print STATE_CHOICES_MAP
    # for k,v in STATE_CHOICES_MAP.items():
    #     print k,v

    # with open('new_address.py','w') as f:
    #     for k,v in STATE_CHOICES_MAP.items():
    #         str = '(\'%s\',u\'%s\'),\n'% (t[0],t[1])
    #         f.write(str.encode('utf-8'))





# for child_of_root in tree.iterfind('CountryRegion/State'):
#     print child_of_root.tag,child_of_root.attrib

