# -*- coding: utf-8 -*-
#
# muesli/web/api/v1/tutorialEndpoint.py
#
# This file is part of MUESLI.
#
# Copyright (C) 2018, Philipp Göldner  <goeldner (at) stud.uni-heidelberg.de>
#                     Christian Heusel <christian (at) heusel.eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from marshmallow.exceptions import ValidationError
from sqlalchemy.orm import joinedload
from cornice.resource import resource, view

from muesli import models
from muesli.web import context
from muesli.web.api.v1 import allowed_attributes


@resource(collection_path='/tutorials',
          path='/tutorials/{tutorial_id}',
          factory=context.TutorialEndpointContext,)
class Tutorial(object):
    def __init__(self, request, context=None):
        self.request = request
        self.db = request.db

    @view(permission='viewOverview')
    def collection_get(self):  # TODO nur authenticated
        """
        ---
        get:
          security:
            - Bearer: [read]
          tags:
            - "v1"
          summary: "return all tutorials"
          description: ""
          operationId: "tutorial_collection_get"
          produces:
            - "application/json"
          responses:
            200:
              description: "response for 200 code"
              schema:
                $ref: "#/definitions/CollectionTutorial"
        """
        tutorials = self.request.user.tutorials.options(joinedload(models.Tutorial.tutor), joinedload(models.Tutorial.lecture))
        schema = models.TutorialSchema(many=True, only=allowed_attributes.collection_tutorial())
        return schema.dump(tutorials)

    def get(self):  # TODO Check if part of tutorial or allowed to view
        """
        ---
        get:
          security:
            - Bearer: [read]
          tags:
            - "v1"
          summary: "return a specific tutorial"
          description: ""
          operationId: "tutorial_get"
          produces:
            - "application/json"
          responses:
            200:
              description: "response for 200 code"
              schema:
                $ref: "#/definitions/Tutorial"
        """
        tutorial = self.request.user.tutorials.options(joinedload(models.Tutorial.tutor), joinedload(models.Tutorial.lecture)).filter(models.Tutorial.id==self.request.matchdict['tutorial_id']).one()
        exa = tutorial.lecture.exams.filter((models.Exam.results_hidden==False)|(models.Exam.results_hidden==None))
        if True:  # TODO CHECK IF TUTOR/ASSISTANT
            tut_schema = models.TutorialSchema()
        else:
            tut_schema = models.TutorialSchema(only=allowed_attributes.tutorial())
        exam_schema = models.ExamSchema(many=True, only=["id", "name"])

        result = tut_schema.dump(tutorial)
        result.update({"exams": exam_schema.dump(exa)})
        return result

    def collection_post(self):
        schema = models.TutorialSchema()
        schema.context['session'] = self.request.db
        try:
            result = schema.load(self.request.json_body)
        except ValidationError as e:
            self.request.errors.add('body', 'fail', e.messages)
        else:
            tutorial = models.Tutorial(**result)
            self.db.add(tutorial)
            self.db.commit()
            return {'result': 'ok', 'created': schema.dump(tutorial)}