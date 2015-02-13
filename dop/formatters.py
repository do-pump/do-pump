
class DropletAttributeFormatter:
    def __init__(self, name, value_of_attribute=None, line_entry_format='{}', table_cell_format='{}'):
        self.name = name

        self.format = format
        self.line_entry_format = line_entry_format
        self.table_cell_format = table_cell_format

        if not value_of_attribute:
            self.extract_value = lambda d: getattr(d, name)
        elif hasattr(value_of_attribute, '__call__'):
            self.extract_value = value_of_attribute
        else:
            self.extract_value = lambda d: getattr(d, value_of_attribute)

    def format_table_cell(self, d):
        return self.table_cell_format.format(self.extract_value(d))

    def format_line_entry(self, d):
        return self.line_entry_format.format(self.extract_value(d))


class DropletFormatter:
    def __init__(self, *attribute_formatters):
        self.attribute_fomrmatters = attribute_formatters
        self.attribute_formatter_map = {f.name: f for f in attribute_formatters}
        self.known_attributes = [f.name for f in attribute_formatters]

    def unknown_attributes(self, attribute_names):
        return [name for name in attribute_names if name not in self.attribute_formatter_map]

    def format_line_entry(self, d, attribute_name):
        return self.attribute_formatter_map[attribute_name].format_line_entry(d)

    def format_line(self, d, attribute_names):
        return [self.format_line_entry(d, n) for n in attribute_names]

    def format_table_cell(self, d, attribute_name):
        return self.attribute_formatter_map[attribute_name].format_table_cell(d)

    def format_table_row(self, d, attribute_names):
        return [self.format_table_cell(d, n) for n in attribute_names]


droplet_formatter = DropletFormatter(
    DropletAttributeFormatter('id', table_cell_format='{0:8}'),
    DropletAttributeFormatter('name', table_cell_format='{0:>12}'),
    DropletAttributeFormatter('ip', 'ip_address', table_cell_format='{0:15}'),
    DropletAttributeFormatter('ipv6', 'ip_v6_address', table_cell_format='{0:39}'),
    DropletAttributeFormatter('status', table_cell_format='{0:6}'),
    DropletAttributeFormatter('private_ip', 'private_ip_address', table_cell_format='{0:15}'),
    DropletAttributeFormatter('size', 'size_slug', table_cell_format='{0:5}'),
    DropletAttributeFormatter('region', lambda d: d.region['slug'], table_cell_format='{0:4}'),
    DropletAttributeFormatter('image', lambda d: d.image['slug'], table_cell_format='{0:16}')
)
