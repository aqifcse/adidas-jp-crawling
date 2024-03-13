def retrieve_row_column_values(size_chart_string):
    rows = size_chart_string.split('\n')
    row_column_values = {}
    for row in rows:
        cells = row.split('\t')
        for cell in cells:
            parts = cell.split(':')
            if len(parts) == 2:
                position, value = parts[0].strip(), parts[1].strip()
                row_column_values[position] = value
    return row_column_values

# Example usage
size_chart_string = """(S, M): 10\t(L, XL): 20\n(M, S): 15\t(XL, L): 25"""
values = retrieve_row_column_values(size_chart_string)
print(values)