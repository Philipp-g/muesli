# -*- coding: utf-8 -*-
#
# api_tools/sample_requests.py
#
# This file is part of MUESLI.
#
# Copyright (C) 2018, Philipp Göldner  <pgoeldner (at) stud.uni-heidelberg.de>
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

import requests

from api_tools.header import authenticate
from api_tools import MUESLI_URL

def get(endpoint, header):
    endpoint = MUESLI_URL + endpoint
    r = requests.get(endpoint, headers=header)
    print(r.json())

def put(endpoint, header):
    endpoint = MUESLI_URL + endpoint
    lecture = '{"term": 20181, "name": "Irgendwas", "lecturer": "Ich auch"}'
    r = requests.get(endpoint, lecture, headers=header)
    print(r.json())

def main():
    headers = authenticate('admin@muesli.org', 'adminpassword', save=True)
    # headers = authenticate('test@test.de', '1234')
    endpoint = "/api/v1/whoami"
    get(endpoint, headers)


if __name__ == "__main__":
    main()