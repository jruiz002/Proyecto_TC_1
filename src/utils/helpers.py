def WriteToFile(filename: str, content: str):
    with open(filename, 'w', encoding='utf-8') as _file:
        _file.write(content)

    return f'File "{filename}" created!'
