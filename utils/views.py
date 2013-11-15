from braces.views import JSONResponseMixin
from django.db.models.query import QuerySet

__author__ = 'joel'

# TODO Refactor this to be an proper view based off some other model class
class JSONListResponseMixin(JSONResponseMixin):
    render_object = None #Name of thing to get from context object

    def render_to_response(self, context):
        contents = {}
        if self.render_object:
            if isinstance(context[self.render_object], QuerySet):
                contents[self.render_object] = list(context[self.render_object])
            else:
                contents[self.render_object] = context[self.render_object]
        return self.render_json_response(contents)