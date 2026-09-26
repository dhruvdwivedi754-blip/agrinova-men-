import os
import re
from pathlib import Path

import joblib
from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, session, url_for

try:
    from dotenv import load_dotenv
except ImportError:
    # Keep API-key based features working even when python-dotenv is not installed yet.
    def load_dotenv(path=None, *_args, **_kwargs):
        env_path = Path(path or ".env")
        if not env_path.exists():
            return False
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ.setdefault(key, value)
        return True

BASE_DIR = Path(__file__).resolve().parent


def load_environment_file(env_path):
    if not env_path:
        return False
    path = Path(env_path).expanduser()
    if not path.exists():
        return False
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ[key] = value
        return True
    except Exception:
        return False


ENV_CANDIDATES = [
    Path(os.getenv("AGRINOVA_ENV_FILE", "")).expanduser() if os.getenv("AGRINOVA_ENV_FILE") else None,
    BASE_DIR / ".env",
    BASE_DIR / "my.env",
    BASE_DIR.parent / ".env",
    BASE_DIR.parent / "my.env",
    Path.cwd() / ".env",
    Path.cwd() / "my.env",
]
for env_path in ENV_CANDIDATES:
    if env_path:
        load_environment_file(env_path)

# Support dotenv if available, but do not depend on it for the chatbot to work.
try:
    load_dotenv(BASE_DIR / ".env")
except Exception:
    pass
MODEL_PATH = BASE_DIR / "ml_assets" / "models" / "crop_prediction_model.pkl"
DATA_PATH = BASE_DIR / "ml_assets" / "data" / "crop_advisory_dataset.csv"
SUPPORT_SUBMISSIONS_PATH = BASE_DIR / "ml_assets" / "data" / "support_submissions.csv"

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-development-secret")
app.config["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "")
app.config["GEMINI_MODEL"] = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def load_crop_assets():
    """Load the team model once; keep the rest of the website available if it fails."""
    try:
        model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None
        # Import pandas lazily to avoid blocking the whole app if pandas import is slow
        dataset = None
        if DATA_PATH.exists():
            try:
                import pandas as pd
            except Exception as exc:  # pragma: no cover - runtime/environment issues
                app.logger.warning("pandas unavailable when loading dataset: %s", exc)
                # Fallback: parse the TSV with the standard library so dropdowns still work
                try:
                    import csv
                    rows = []
                    with open(DATA_PATH, encoding="utf-8") as fh:
                        reader = csv.DictReader(fh, delimiter="\t")
                        for r in reader:
                            rows.append({k: (v.strip() if isinstance(v, str) else v) for k, v in r.items()})
                    dataset = rows
                except Exception as exc2:
                    app.logger.warning("Fallback CSV read failed: %s", exc2)
                    dataset = None
            else:
                dataset = pd.read_csv(DATA_PATH, sep="\t")
        return model, dataset
    except Exception as exc:
        app.logger.warning("Crop model unavailable: %s", exc)
        return None, None


crop_model, crop_dataset = load_crop_assets()


def require_login():
    return "username" in session


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/styles.css")
@app.route("/script.js")
@app.route("/style.css")
def legacy_assets():
    # Allows the existing HTML to work while also supporting Flask's /static URLs.
    return send_from_directory(app.static_folder, request.path.lstrip("/"))


@app.route("/images/<path:filename>")
def legacy_images(filename):
    """Serve images referenced by the imported landing page."""
    return send_from_directory(Path(app.static_folder) / "images", filename)


@app.route("/assets/<path:filename>")
def project_assets(filename):
    """Serve the AgriNova image assets used by the landing page."""
    return send_from_directory(BASE_DIR / "assets", filename)


PUBLIC_PAGES = {"index", "login", "signup", "forgotpassword"}
PROTECTED_PAGES = {"home", "crop-advisory", "fertilizer", "chatbot", "support"}


@app.route("/<page>")
@app.route("/<page>.html")
def page(page):
    if page in PROTECTED_PAGES and not require_login():
        return redirect(url_for("page", page="login"))
    if page in PUBLIC_PAGES or page in PROTECTED_PAGES:
        return render_template(f"{page}.html")
    return jsonify({"error": "Page not found"}), 404


@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    mobile = str(data.get("mobile", "")).strip()
    password = str(data.get("password", "")).strip()
    if not all([name, email, mobile, password]) or "@" not in email:
        return jsonify(success=False, message="Enter a name, valid email, phone number, and password."), 400
    # Demo session only. Replace with a database and password hashing before production.
    session.update(username=name, email=email)
    return jsonify(success=True, message="Account created successfully."), 201


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip()
    password = str(data.get("password", "")).strip()
    if not email or not password or "@" not in email:
        return jsonify(success=False, message="Enter a valid email and password."), 400
    session.update(username=email.split("@")[0], email=email)
    return jsonify(success=True, message="Login successful.")


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify(success=True)


@app.route("/api/get-username")
def get_username():
    return jsonify(username=session.get("username", "Farmer"))


@app.route("/api/crop-options")
def crop_options():
    if crop_dataset is None:
        return jsonify(success=False, message="Crop data is unavailable."), 503
    columns = ["State_UT", "Soil_Type", "Temperature_Range_C", "Water_Availability", "Season"]
    options = {}
    # Support both pandas DataFrame and fallback list-of-dicts dataset
    if isinstance(crop_dataset, list):
        for column in columns:
            vals = {str(row.get(column)).strip() for row in (crop_dataset or []) if row.get(column) not in (None, "")}
            options[column] = sorted(v for v in vals if v and v.lower() != 'nan')
    else:
        # pandas DataFrame path
        for column in columns:
            try:
                col_vals = crop_dataset[column].dropna().astype(str).unique()
                options[column] = sorted(col_vals)
            except Exception:
                options[column] = []
    return jsonify(success=True, options=options)


@app.route("/api/crop-recommendation", methods=["POST"])
def crop_recommendation():
    data = request.get_json(silent=True) or {}
    if crop_model is not None:
        payload = {
            "State_UT": str(data.get("state", "")).strip(),
            "Soil_Type": str(data.get("soil", "")).strip(),
            "Temperature_Range_C": str(data.get("temperature", "")).strip(),
            "Water_Availability": str(data.get("water", "")).strip(),
            "Season": str(data.get("season", "")).strip(),
        }
        if not all(payload.values()):
            return jsonify(success=False, message="Complete all crop details."), 400
        try:
            # The saved pipeline accepts a list of dicts (DictVectorizer + classifier)
            crop_pred = crop_model.predict([payload])
            crop = crop_pred[0] if isinstance(crop_pred, (list, tuple)) else crop_pred
            # Unwrap nested sequence results (e.g., array/list inside the first element)
            if hasattr(crop, "__len__") and not isinstance(crop, str):
                try:
                    if len(crop):
                        crop = crop[0]
                except Exception:
                    pass
            crop = str(crop)
            reason, reason_source = get_crop_explanation(crop, payload)
            # Do not save name/phone from crop advisory here — support form handles user contact records.
            return jsonify(
                success=True,
                recommendation=f"Recommended crop: {crop}",
                crop=crop,
                reason=reason,
                reason_source=reason_source,
                source="ML model",
            )
        except Exception as exc:
            app.logger.warning("Crop prediction failed: %s", exc)
    return jsonify(success=True, recommendation=get_crop_fallback(data), source="rule-based fallback")


def get_crop_fallback(data):
    season = str(data.get("season", "")).lower()
    soil = str(data.get("soil", "")).lower()
    water = str(data.get("water", "")).lower()
    if "kharif" in season and "high" in water:
        return "Rice is suitable for high-water Kharif conditions."
    if "black" in soil:
        return "Cotton is a strong option for black soil."
    if "rabi" in season:
        return "Wheat, barley, or pulses are suitable Rabi options."
    return "Consider locally suitable pulses or vegetables, then confirm with an agricultural officer."


def get_crop_explanation(crop, payload):
    """Explain an ML result without claiming the model's internal reasoning."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = (
                "You are an agriculture assistant for Indian farmers. Explain in 2-3 short "
                "bullets why the crop recommendation below is a sensible match for the supplied "
                "conditions. Do not claim access to model internals or guarantee yield. Be practical "
                "and mention that local soil testing and market conditions should be checked.\n\n"
                f"Recommended crop: {crop}\nConditions: {payload}"
            )
            response = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"), contents=prompt
            )
            explanation = (getattr(response, "text", "") or "").strip()
            if explanation:
                return explanation, "Gemini-assisted explanation"
        except Exception as exc:
            app.logger.warning("Gemini crop explanation failed: %s", exc)

    return (
        f"The recommendation matches the selected {payload['Season']} season, "
        f"{payload['Soil_Type']} soil, {payload['Water_Availability'].lower()} water availability, "
        f"and {payload['Temperature_Range_C']} temperature range in {payload['State_UT']}. "
        "Use a local soil test and market information before making a final planting decision."
    ), "Condition-based explanation"


@app.route("/api/fertilizer-recommendation", methods=["POST"])
def fertilizer_recommendation():
    data = request.get_json(silent=True) or {}
    try:
        crop = str(data.get("crop", "")).lower()
        n, p, k = (float(data.get(key, 0)) for key in ("nitrogen", "phosphorus", "potassium"))
        ph = float(data.get("soil_ph", 7))
    except (TypeError, ValueError):
        return jsonify(success=False, message="N, P, K and pH must be numbers."), 400
    organic = str(data.get("organic", "both")).lower()
    advice = []
    if "organic" in organic:
        advice.append("Apply well-decomposed farmyard manure or compost according to a local soil test.")
    else:
        if n < 100: advice.append("Nitrogen is low; split nitrogen application through the growing season.")
        if p < 50: advice.append("Phosphorus is low; incorporate a phosphorus source before sowing.")
        if k < 40: advice.append("Potassium is low; apply a potassium source based on the soil-test recommendation.")
    if ph < 6.5: advice.append(f"Soil is acidic (pH {ph}); discuss liming with a local agricultural officer.")
    elif ph > 7.5: advice.append(f"Soil is alkaline (pH {ph}); use organic matter and get a soil-test-based amendment plan.")
    if not advice: advice.append(f"Nutrients appear balanced for {crop or 'this crop'}; keep testing soil regularly.")
    return jsonify(success=True, recommendation=" ".join(advice))


@app.route("/api/chatbot-response", methods=["POST"])
def chatbot_response():
    message = str((request.get_json(silent=True) or {}).get("message", "")).strip()
    if not message:
        return jsonify(success=False, message="Enter a question."), 400

    reply = gemini_reply(message)
    if not reply:
        reply = rule_based_reply(message)
    return jsonify(success=True, reply=normalize_chat_reply(reply))


def normalize_chat_reply(reply):
    if not reply:
        return "I can help with crops, soil, water, fertilizer, pests, and diseases."

    text = str(reply).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("**", "")
    text = text.strip(" -")
    if not text:
        return "I can help with crops, soil, water, fertilizer, pests, and diseases."
    return text


def gemini_reply(message):
    api_key = (app.config.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")).strip()
    if not api_key:
        app.logger.warning("GEMINI_API_KEY not set; chatbot falling back to rule-based reply")
        return None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = (
            "You are AgriNova, a practical farming assistant for Indian farmers. "
            "Answer in the same language as the user. If the user writes in Hindi, reply in Hindi. "
            "If the user writes in English, reply in English. "
            "Keep the advice short, practical, and specific to Indian farming conditions. "
            "Use 2-4 short bullet points and one brief next step when useful. "
            "Do not invent facts or guarantee yield. "
            "For fertilizer or pesticide advice, remind the user to follow the product label and local agricultural guidance.\n\n"
            f"User: {message}"
        )
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            contents=prompt,
        )
        text = getattr(response, "text", "").strip() or ""
        if text:
            return text
    except Exception as exc:
        app.logger.warning("Gemini request failed: %s", exc)
    return None


def rule_based_reply(message):
    text = message.lower()
    if any(keyword in text for keyword in ["fertilizer", "खाद", "urea", "nitrogen", "phosphorus", "potassium", "nutrient"]):
        return "Use a soil test before fertilizing. Apply nutrients in split doses and follow the product label and local agricultural advice."
    if any(keyword in text for keyword in ["disease", "बीमारी", "pest", "कीड़ा", "fungus", "infected", "leaf spot"]):
        return "Inspect leaves carefully, remove badly infected plant parts safely, improve airflow and drainage, and confirm treatment with a local agricultural officer."
    if any(keyword in text for keyword in ["water", "पानी", "irrigation", "drip"]):
        return "Irrigate based on soil moisture and crop stage. Drip irrigation can reduce waste where suitable."
    if any(keyword in text for keyword in ["soil", "मिट्टी", "ph", "acidity", "alkalinity"]):
        return "Check soil pH and organic matter before making amendments. Local soil testing is the best way to decide what to add."
    if any(keyword in text for keyword in ["crop", "फसल", "seed", "बीज"]):
        return "Choose a crop that matches your local season, soil type, water availability, and market demand. A local agriculture officer can help confirm suitability."
    return "I can help with crops, soil, water, fertilizer, pests, and diseases. For a personalized answer, set GEMINI_API_KEY in .env."


@app.route("/api/submit-support", methods=["POST"])
def submit_support():
    data = request.get_json(silent=True) or {}
    if not all(str(data.get(key, "")).strip() for key in ("name", "phone", "query")):
        return jsonify(success=False, message="All fields are required."), 400
    # Persist support submission to CSV for later review/download
    try:
        import csv
        SUPPORT_SUBMISSIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
        file_exists = SUPPORT_SUBMISSIONS_PATH.exists()
        with open(SUPPORT_SUBMISSIONS_PATH, 'a', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            if not file_exists:
                writer.writerow(["timestamp", "name", "phone", "query", "source"])
            from datetime import datetime
            writer.writerow([datetime.utcnow().isoformat(), str(data.get('name','')).strip(), str(data.get('phone','')).strip(), str(data.get('query','')).strip(), 'support_form'])
    except Exception as exc:
        app.logger.warning('Failed to save support submission: %s', exc)
    return jsonify(success=True, message=f"Thanks {data['name'].strip()}! Your support request has been recorded.")


@app.route("/health")
def health():
    return jsonify(status="ok", crop_model_loaded=crop_model is not None, gemini_configured=bool(os.getenv("GEMINI_API_KEY")))


@app.route('/submissions.csv')
def download_submissions():
    """Serve the CSV of saved crop submissions if it exists."""
    if SUPPORT_SUBMISSIONS_PATH.exists():
        return send_from_directory(SUPPORT_SUBMISSIONS_PATH.parent, SUPPORT_SUBMISSIONS_PATH.name, as_attachment=True)
    return jsonify(success=False, message='No submissions yet.'), 404


@app.route('/submissions.xlsx')
def download_submissions_xlsx():
    """Export the support submissions CSV to an XLSX file and serve it.

    If openpyxl is not installed on the environment, return a helpful error message.
    """
    if not SUPPORT_SUBMISSIONS_PATH.exists():
        return jsonify(success=False, message='No submissions yet.'), 404
    try:
        try:
            from openpyxl import Workbook
        except Exception:
            return jsonify(success=False, message='XLSX export requires openpyxl. Install it in the environment.'), 503

        # Read CSV and write XLSX
        import csv
        wb = Workbook()
        ws = wb.active
        with open(SUPPORT_SUBMISSIONS_PATH, encoding='utf-8', newline='') as fh:
            reader = csv.reader(fh)
            for r in reader:
                ws.append(r)

        xlsx_path = SUPPORT_SUBMISSIONS_PATH.with_suffix('.xlsx')
        wb.save(xlsx_path)
        return send_from_directory(xlsx_path.parent, xlsx_path.name, as_attachment=True)
    except Exception as exc:
        app.logger.warning('Failed to create XLSX: %s', exc)
        return jsonify(success=False, message='Failed to export XLSX.'), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG", "true").lower() == "true")
