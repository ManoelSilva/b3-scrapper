from extractor import B3Extractor

extractor = B3Extractor()


def handle(event, context):
    return extractor.extract()


if __name__ == '__main__':
    handle(None, None)
