import json


class Settings(object):
    filename: str
    overlay_frequency = None
    CLASSES: dict
    size_text = None

    def __repr__(self):
        return 'overlay_frequency: ' + str(self.overlay_frequency) + '\n' + \
               'size_text: ' + str(self.size_text) + '\n' + \
               '\n'.join('%s: %s' % (k, v) for k, v in self.CLASSES.items())

    def __init__(self, filename):
        self.filename = filename

    def getClassFromName(self, name: str):
        for dct in self.CLASSES:
            if dct['name'] == name:
                return dct

    def default(self):
        self.overlay_frequency = 1
        self.size_text = 0.8
        self.CLASSES = [{"name": "background", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "aeroplane", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "bicycle", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "bird", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "boat", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "bottle", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "bus", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "car", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "cat", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "chair", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "cow", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "diningtable", "border_size": 2, "text_size": 2, "color": [0, 0, 0],
                         "confidence": 0.8, "enabled": True},
                        {"name": "dog", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "horse", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "motorbike", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "persone", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "pottedplant", "border_size": 2, "text_size": 2, "color": [0, 0, 0],
                         "confidence": 0.8, "enabled": True},
                        {"name": "sheep", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "sofa", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "train", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True},
                        {"name": "tvmonitor", "border_size": 2, "text_size": 2, "color": [0, 0, 0], "confidence": 0.8,
                         "enabled": True}]

    def save_json(self):
        dct = {"overlay_frequency": self.overlay_frequency,
               "size_text": self.size_text,
               "CLASSES": self.CLASSES}
        with open(self.filename, 'w') as outfile:
            json.dump(dct, outfile, indent=4)

    def load_json(self):
        with open(self.filename) as f:
            data = json.load(f)
        self.overlay_frequency = data.get('overlay_frequency')
        self.size_text = data.get('size_text')
        self.CLASSES = data.get('CLASSES')


if __name__ == '__main__':
    s = Settings('settings.json')
    s.default()
    # s.save_json()
    print({key['name']: 0 for key in s.CLASSES})
