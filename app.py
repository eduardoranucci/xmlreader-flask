from flask import Flask, render_template, request, send_file, session
from utils import merge_parsed_data, generate_excel
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = "session-key" # Chave secreta para poder utilizar session

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        if "xml_files" not in request.files:
            return render_template("error.html", msg="Nenhum arquivo enviado!"), 400

        files = request.files.getlist("xml_files")
        xml_type = request.form.get("xml_type")
        
        try:
            data = merge_parsed_data(files, xml_type)
        except Exception as e:
            return render_template("error.html", msg=str(e)), 500

        if data:
            session["parsed_data"] = json.dumps(data)
            return render_template("results.html", data=data)
        else:
            return render_template("error.html", msg="Nenhum dado válido encontrado!"), 400

    session.pop("parsed_data", None)
    return render_template("index.html")

@app.route("/export", methods=["POST"])
def export():
    if "parsed_data" not in session:
        return render_template("error.html", msg="Nenhum dado para exportar!"), 400

    data = json.loads(session["parsed_data"])
    excel_buffer = generate_excel(data)
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    return send_file(
        excel_buffer,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"relatorio_{timestamp}.xlsx"
    )

if __name__ == "__main__":
    app.run(debug=True)