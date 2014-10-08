import html

def make_element(name,value, **attrs):
    keyvals = [' %s="%s"' % item for item in attrs.items()]
    attr_str =' '.join(keyvals)
    element = '<{name}{attrs}>{value}</{name}>'.format(
            name=name,
            attrs=attr_str,
            value=html.cgi.escape(value))
    return element

a = make_element('item', 'Albatross',size='large',quantity=6,style='width:90px')
print a
