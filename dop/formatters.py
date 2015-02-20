
class AttributeFormatter:
    def __init__(self, attribute_name_of_extractor, **styles):
        self._styles = styles

        if hasattr(attribute_name_of_extractor, '__call__'):
            self.extract_value = attribute_name_of_extractor
        else:
            self.extract_value = lambda d: getattr(d, attribute_name_of_extractor)

    def format(self, d, style):
        effective_style = self._styles[style] if style in self._styles else '{}'
        return effective_style.format(self.extract_value(d))


class ObjectFormatter:
    def __init__(self, **attribute_formatters):
        self._formatter_map = attribute_formatters
        self.attributes = attribute_formatters.keys()

    def unknown_attributes(self, attribute_names):
        return [name for name in attribute_names if name not in self._formatter_map]

    def format_attribute(self, d, attribute_name, style_name):
        return self._formatter_map[attribute_name].format(d, style_name)

    def format(self, d, attribute_names, style_name):
        return [self.format_attribute(d, n, style_name) for n in attribute_names]


droplet_formatter = ObjectFormatter(
    id=AttributeFormatter('id', table='{0:8}'),
    name=AttributeFormatter('name', table='{0:>12}'),
    ip=AttributeFormatter('ip_address', table='{0:15}'),
    ipv6=AttributeFormatter('ip_v6_address', table='{0:39}'),
    status=AttributeFormatter('status', table='{0:6}'),
    private_ip=AttributeFormatter('private_ip_address', table='{0:15}'),
    size=AttributeFormatter('size_slug', table='{0:5}'),
    region=AttributeFormatter(lambda d: d.region['slug'], table='{0:4}'),
    image=AttributeFormatter(lambda d: d.image['slug'], table='{0:16}')
)
