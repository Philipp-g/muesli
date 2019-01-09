from cornice.resource import resource, view
from muesli import models
from muesli.web import context

from sqlalchemy import inspect
from sqlalchemy.orm import exc, joinedload, undefer
from sqlalchemy.sql.expression import desc
from marshmallow.exceptions import ValidationError


@resource(collection_path='/api/lectures',
          path='/api/lectures/{lecture_id}',
          factory=context.GeneralContext,
          permission='view')  # TODO Api specific permission
class Lecture(object):
    """A greeting endpoint.

    ---
    x-extension: value
    get:
        description: some description
        responses:
            200:
                description: response for 200 code
                schema:
                    $ref: #/definitions/LectureSchema
    """
    def __init__(self, request, context=None):
        self.request = request
        self.db = request.db

    def collection_get(self):
        """A greeting endpoint.

        ---
        x-extension: value
        get:
            description: some description
            responses:
                200:
                    description: response for 200 code
                    schema:
                        $ref: #/definitions/BarBodySchema
        """
        lectures = (
            self.db.query(models.Lecture)
            .order_by(desc(models.Lecture.term), models.Lecture.name)
            .options(joinedload(models.Lecture.assistants))
            .filter(models.Lecture.is_visible == True) # noqa
            .all()
        )
        filter_params = {}
        return_data = []
        for key, value in self.request.params.items():
            filter_params[key] = value
            # print("(" + key + ", " + value + ")")
        allowed_attr_lecture = ['id', 'name', 'lecturer', 'assistants', 'term']
        if filter_params:
            filtered_keys = {}
            print("params:", filter_params)
            for key,value in filter_params.items():
                if key in allowed_attr_lecture:
                    filtered_keys[key] = value
            print("filtered:", filtered_keys)
            schema = models.LectureSchema(many=True, only=list(filtered_keys))
            data = schema.dump(lectures)
            for key, val in filtered_keys.items():
                print(key)
                print(value)
                for lecture in data:
                    if value:
                        if lecture[key] == int(value):
                            return_data.append(lecture)
                    else:
                        if lecture[key]:
                            return_data.append(lecture)
        else:
            schema = models.LectureSchema(many=True, only=allowed_attr_lecture)
            return_data = schema.dump(lectures)
        return return_data

    def get(self):
        """A greeting endpoint.

        ---
        x-extension: value
        get:
            description: some description
            responses:
                200:
                    description: response for 200 code
                    schema:
                        $ref: #/definitions/BarBodySchema
        """
        lecture_id = self.request.matchdict['lecture_id']
        lecture = self.db.query(models.Lecture).options(undefer('tutorials.student_count'), joinedload(models.Lecture.assistants), joinedload(models.Lecture.tutorials)).get(lecture_id)
        # TODO What are these?
        times = lecture.prepareTimePreferences(user=self.request.user)
        subscribed = self.request.user.id in [s.id for s in lecture.students]
        allowed_attr_lecture = [
            'id',
            'name',
            'lecturer',
            'assistants',
            'term',
            'url',
            'tutorials',
        ]

        schema = models.LectureSchema(only=allowed_attr_lecture)
        return {'lecture': schema.dump(lecture),
                'subscribed': subscribed,
                'times': times}

    @view(permission='put')  # TODO API specific permission
    def put(self):
        lecture_id = self.request.matchdict['lecture_id']
        lecture = self.db.query(models.Lecture).options(undefer('tutorials.student_count'), joinedload(models.Lecture.assistants)).get(lecture_id)
        schema = models.LectureSchema()
        # attatch db session to schema so it can be used during validation
        schema.context['session'] = self.request.db
        try:
            result = schema.load(self.request.json_body, partial=True)
        except ValidationError as e:
            self.request.errors.add('body', 'fail', e.messages)
        else:
            for k, v in result.items():
                setattr(lecture, k, v)
                # TODO do we need to catch this exception?
            try:
                self.db.commit()
            except exc.SQLAlchemyError:
                # TODO better exception
                self.db.rollback()
            else:
                return {'result': 'ok', 'update': self.get()}

    @view(permission='post')  # TODO API specific permission
    def collection_post(self):
        schema = models.LectureSchema()
        schema.context['session'] = self.request.db
        try:
            result = schema.load(self.request.json_body)
        except ValidationError as e:
            self.request.errors.add('body', 'fail', e.messages)
        else:
            lecture = models.Lecture(**result)
            self.db.add(lecture)
            self.db.commit()
            return {'result': 'ok', 'created': schema.dump(lecture)}
