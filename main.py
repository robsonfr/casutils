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
from flask import Flask, render_template, request, send_file
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO

from casconv import Cas2Bin, Cas2WavStream

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html', titulo="CasUtils")

@app.route('/convert', methods=['GET', 'POST'])
def post():
    f = request.files["arquivo"]
    b=bytearray(f.read())
    arquivo = BytesIO(b)
    print(len(b))
    gap = request.form.get("gap","") == "gap"
    samples_per_second = int(request.form["sr"])
    stmono = request.form.get("stereo","") == "stereo"
    bits = int(request.form["bps"])
    with Cas2WavStream(tem_gap = gap, sps = samples_per_second, stereo = stmono, bps = bits) as saida:
        if gap:
            todos_blocos = Cas2Bin("").read_blocos(arquivo)
            saida.write_todos_blocos(todos_blocos)
        else:
            saida.write(arquivo.read())
        saida.update()
        saida.stream.seek(0)
        x = saida.stream.read()
        out = BytesIO()
        with ZipFile(out,"w",ZIP_DEFLATED) as zip:
            zip.writestr("output.wav",x)
        out.seek(0)
        return send_file(out, mimetype='application/octet-stream', as_attachment=True, download_name='output.zip')
        