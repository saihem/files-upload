import collections
import json


class JsonFormMixin:
    cleaned_data = {}

    @property
    def cleaned_json(self):
        return {
            k: self.json_value(v)
            for k, v in self.cleaned_data.items()
        }

    def json_value(self, v):
        if not isinstance(v, str) and isinstance(v, collections.Iterable):
            cleaned_v = [self.json_value(i) for i in v]
        else:
            try:
                cleaned_v = json.dumps(v)
            except (TypeError, ValueError):
                cleaned_v = str(v)
        return cleaned_v
