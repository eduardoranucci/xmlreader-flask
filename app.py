from flask import Flask, render_template, request, send_file
from parser import parser_nfe
from datetime import datetime
from io import BytesIO
import pandas as pd

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        if "xml_files" not in request.files:
            return "Nenhum arquivo enviado!", 400
        
        files = request.files.getlist("xml_files")
        xml_type = request.form.get("xml_type")
        
        data = []
        for file in files:
            if file.filename.endswith(".xml"):
                try:
                    if xml_type == "nfe":
                        data.append(parser_nfe(file.read()))
                except Exception as e:
                    print(f"Erro no arquivo {file.filename}: {e}")

        if data:
            df = pd.DataFrame(data)
            excel_buffer = BytesIO()
            df.to_excel(excel_buffer, index=False, engine="openpyxl")
            excel_buffer.seek(0)
            
            timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
            return send_file(
                excel_buffer,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=f"relatorio_{timestamp}.xlsx"
            )
        else:
            return "Nenhum dado válido encontrado!", 400
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)