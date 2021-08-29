#!/usr/bin/env python3
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from flask import Flask, render_template
import os
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
import jinja2

from casconv import Cas2Wav, Cas2Bin, Cas2WavStream

app = Flask(__name__)

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


@app.route('/')
def main(self):
    template_values = {
        "titulo" : "CasUtils"
    }
    template = jinja_environment.get_template('index.html')
    return template.render(template_values)

@app.route()
class CasProcessor(webapp2.RequestHandler):
    def post(self):
        arquivo = BytesIO(bytearray(self.request.get("arquivo")))        
        gap = self.request.get("gap") == "gap"
        samples_per_second = int(self.request.get("sr"))
        stmono = self.request.get("stereo") == "stereo"
        bits = int(self.request.get("bps"))
        with Cas2WavStream(tem_gap = gap, sps = samples_per_second, stereo = stmono, bps = bits) as saida:
            if gap:
                todos_blocos = Cas2Bin("").read_blocos(arquivo)
                saida.write_todos_blocos(todos_blocos)
            else:
                saida.write(arquivo.read())
            saida.update()
            saida.stream.seek(0)
            x = saida.stream.read()
            self.response.headers.add_header('content-type','application/octet-stream')
            self.response.headers.add_header('content-disposition', 'attachment', filename='output.zip')
            out = BytesIO()
            with ZipFile(out,"w",ZIP_DEFLATED) as zip:
                zip.writestr("output.wav",x)
            out.seek(0)
            self.response.out.write(out.read())
        

#with Cas2WavStream(nome_saida, tem_gap = gap, sps = sps, stereo = (chan == 2), bps = bits) as saida:
#    saida.write_todos_blocos(todos_blocos)
#    x = saida.stream.readall()
#    print len(x)
        
