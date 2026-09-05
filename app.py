
import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd
import math
import time
import json
import calendar
from pathlib import Path
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Fit 88", layout="centered")

GERMANY_TZ = ZoneInfo("Europe/Berlin")

def local_today():
    """Lokales Datum in Deutschland – unabhängig von der Streamlit-Server-Zeitzone."""
    return datetime.now(GERMANY_TZ).date()


st.markdown("""
<style>
.block-container{max-width:760px;padding-top:1.1rem;padding-left:.8rem;padding-right:.8rem;padding-bottom:2rem;}
div[data-testid="stButton"]>button{min-height:52px;font-size:1.05rem;font-weight:700;border-radius:12px;}
div[data-testid="stMetric"]{background:rgba(127,127,127,.08);border-radius:12px;padding:.55rem;}
.stTabs [data-baseweb="tab-list"]{gap:.25rem;flex-wrap:wrap;}
.stTabs [data-baseweb="tab"]{padding-left:.55rem;padding-right:.55rem;}

/* Tagesaufgaben: dunkle Karten, blaue Schrift */
div[data-testid="stCheckbox"]{
    background:#18212f;
    border:1px solid rgba(147,197,253,.22);
    border-radius:12px;
    padding:.70rem .85rem;
    margin:.38rem 0;
}
div[data-testid="stCheckbox"] label{
    width:100%;
}
div[data-testid="stCheckbox"] label p{
    color:#93c5fd !important;
    font-weight:700 !important;
    font-size:1rem !important;
}
div[data-testid="stCheckbox"] svg{
    color:#60a5fa !important;
}
div[data-testid="stCheckbox"]:hover{
    border-color:#60a5fa;
    background:#1d2939;
}

/* Kompakter Trainingsmodus: Bild, Text, Timer und Navigation möglichst in einer Ansicht */
.fit-card{padding:6px 9px;border-radius:11px;background:#18212f;color:#fff;text-align:center;
          margin:2px 0 4px 0;border:1px solid rgba(255,255,255,.12);}
.fit-card .name{font-size:21px;font-weight:800;line-height:1.05;}
.fit-card .amount{font-size:15px;font-weight:700;margin-top:3px;color:#dbeafe;}
.fit-card .cue{font-size:12px;margin-top:3px;color:#e5e7eb;line-height:1.15;}
.compact-note{font-size:.76rem;color:#94a3b8;text-align:center;margin:0 0 .15rem 0;}
div[data-testid="stSelectbox"]{margin-bottom:0;}
div[data-testid="stMetric"]{padding:.25rem!important;}
div[data-testid="stMetric"] label{font-size:.72rem!important;}
div[data-testid="stMetricValue"]{font-size:1rem!important;}
@media (max-width:700px){
  h1{font-size:1.65rem!important} h2{font-size:1.35rem!important} h3{font-size:1.08rem!important}
  .block-container{padding-top:.55rem!important;padding-bottom:1rem!important;}
  div[data-testid="stButton"]>button{min-height:38px;font-size:.86rem;padding:.2rem .35rem;}
  .fit-card .name{font-size:18px}.fit-card .amount{font-size:14px}.fit-card .cue{font-size:11px}
}
</style>
""", unsafe_allow_html=True)



# -------------------------------------------------
# Übungsdarstellung: lokale männliche Bilder bevorzugt
# -------------------------------------------------
# Lege die neuen Bilder in den Ordner "assets_male".
# Die App verwendet sie automatisch. Nur wenn eine Datei fehlt, wird
# vorübergehend auf die freie Exercise-Datenbank zurückgegriffen.
DB_BASE = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises"

EXERCISE_DB = {
    "Kniebeugen": ("Bodyweight_Squat/0.jpg", "Bodyweight_Squat/1.jpg"),
    "Liegestütze": ("Pushups/0.jpg", "Pushups/1.jpg"),
    "Rückwärts-Ausfallschritte": ("Bodyweight_Walking_Lunge/0.jpg", "Bodyweight_Walking_Lunge/1.jpg"),
    "Split Squats": ("Split_Squat_with_Dumbbells/0.jpg", "Split_Squat_with_Dumbbells/1.jpg"),
    "Plank": ("Plank/0.jpg", "Plank/1.jpg"),
    "Seitstütz links": ("Side_Bridge/0.jpg", "Side_Bridge/1.jpg"),
    "Seitstütz rechts": ("Side_Bridge/0.jpg", "Side_Bridge/1.jpg"),
    "Scapular Push-ups": ("Pushups/0.jpg", "Pushups/1.jpg"),
}

MALE_EXERCISE_IMAGES = {
    "Kniebeugen": "assets_male/kniebeugen.png",
    "Liegestütze": "assets_male/liegestuetze.png",
    "Rückwärts-Ausfallschritte": "assets_male/rueckwaerts_ausfallschritte.png",
    "Split Squats": "assets_male/split_squats.png",
    "Reverse Snow Angels": "assets_male/reverse_snow_angels.png",
    "Y-T-W": "assets_male/ytw.png",
    "Bird Dog": "assets_male/bird_dog.png",
    "Glute Bridge": "assets_male/glute_bridge.png",
    "Plank": "assets_male/plank.png",
    "Seitstütz links": "assets_male/seitstuetz.png",
    "Seitstütz rechts": "assets_male/seitstuetz.png",
    "Scapular Push-ups": "assets_male/scapular_pushups.png",
}

EXERCISE_TIPS = {
    "Kniebeugen": "Brust aufrecht · Knie folgen den Fußspitzen · Druck über den ganzen Fuß.",
    "Liegestütze": "Körper bleibt wie ein Brett · Ellenbogen etwa 30–45° zum Oberkörper.",
    "Rückwärts-Ausfallschritte": "Großer Schritt nach hinten · vorderes Knie stabil über dem Fuß.",
    "Split Squats": "Oberkörper aufrecht · kontrolliert senken · vorderes Bein arbeitet.",
    "Reverse Snow Angels": "Bauchlage · Schulterblätter nach hinten/unten · Nacken lang.",
    "Y-T-W": "Arme nur so hoch wie sauber möglich · Schulterblätter aktiv zusammenführen.",
    "Bird Dog": "Becken bleibt ruhig · nicht ins Hohlkreuz · lang statt hoch strecken.",
    "Glute Bridge": "Rippen unten · Gesäß aktiv · nicht aus dem unteren Rücken überstrecken.",
    "Plank": "Bauch und Gesäß fest · Kopf, Rücken und Beine bilden eine Linie.",
    "Seitstütz links": "Hüfte aktiv hochdrücken · Schulter weg vom Ohr.",
    "Seitstütz rechts": "Hüfte aktiv hochdrücken · Schulter weg vom Ohr.",
    "Scapular Push-ups": "Arme gestreckt lassen · Bewegung ausschließlich aus den Schulterblättern.",
}

def show_exercise_animation(name):
    """Kompakte Übungsdarstellung. Lokale männliche PNGs werden bevorzugt."""
    tip = EXERCISE_TIPS.get(
        name, "Langsam, kontrolliert und nur im schmerzfreien Bewegungsbereich ausführen."
    )

    local_path = MALE_EXERCISE_IMAGES.get(name)
    if local_path and Path(local_path).exists():
        # Bei rechter Seite dasselbe Bild spiegeln.
        if name == "Seitstütz rechts":
            from PIL import Image, ImageOps
            img = Image.open(local_path)
            st.image(ImageOps.mirror(img), width=250)
        else:
            st.image(local_path, width=250)
        st.markdown(f'<div class="compact-note"><b>Technik:</b> {tip}</div>', unsafe_allow_html=True)
        return

    pair = EXERCISE_DB.get(name)
    if pair:
        url1 = f"{DB_BASE}/{pair[0]}"
        url2 = f"{DB_BASE}/{pair[1]}"
        mirror = "scaleX(-1)" if name == "Seitstütz rechts" else "scaleX(1)"
        html = f"""
        <style>
          .db-anim {{
            position:relative;height:150px;overflow:hidden;border-radius:12px;background:#111827;
          }}
          .db-anim img {{
            position:absolute;inset:0;width:100%;height:100%;object-fit:contain;
            transform:{mirror};animation-duration:2.8s;animation-iteration-count:infinite;
            animation-timing-function:ease-in-out;
          }}
          .db-a {{animation-name:dbA}} .db-b {{animation-name:dbB}}
          @keyframes dbA {{0%,38%{{opacity:1}}50%,88%{{opacity:0}}100%{{opacity:1}}}}
          @keyframes dbB {{0%,38%{{opacity:0}}50%,88%{{opacity:1}}100%{{opacity:0}}}}
        </style>
        <div class="db-anim">
          <img class="db-a" src="{url1}" alt="{name} Startposition">
          <img class="db-b" src="{url2}" alt="{name} Endposition">
        </div>
        """
        st.components.v1.html(html, height=158)
        st.markdown(f'<div class="compact-note"><b>Technik:</b> {tip}</div>', unsafe_allow_html=True)
        return

    st.info("Für diese Übung fehlt noch das Bild in assets_male.")
    st.caption(f"Technik: {tip}")


# -------------------------------------------------
# Grundeinstellungen
# -------------------------------------------------
START_WEIGHT = 103.0
TARGET_WEIGHT = 90.0

GERMAN_DAYS = {
    0: "Montag", 1: "Dienstag", 2: "Mittwoch", 3: "Donnerstag",
    4: "Freitag", 5: "Samstag", 6: "Sonntag"
}

WEEK_PLAN = {
    "Montag": ("🟦", "Regeneration", "Praxis / Alltag, kein Zusatztraining"),
    "Dienstag": ("💪", "Kraft A + Hund", "4 km Hund + Ganzkörperzirkel + Dehnen"),
    "Mittwoch": ("🏃", "Laufband", "45 Min · 4,4 km/h · 10 % Steigung"),
    "Donnerstag": ("🧍", "Rücken/Core + Hund", "4 km Hund + Rücken/Core + Dehnen"),
    "Freitag": ("💪", "Kraft B + Hund", "4 km Hund + Ganzkörperzirkel + Dehnen"),
    "Samstag": ("🏃", "Laufband", "45 Min · 4,4 km/h · 10 % Steigung"),
    "Sonntag": ("🏃", "Laufband", "45 Min · 4,4 km/h · 10 % Steigung"),
}

# type:
# reps = Wiederholungen, user drückt "Fertig"
# timed = Zeitübung mit Countdown
WORKOUT_A = [
    {"name":"Kniebeugen","amount":"12–15 Wiederholungen","cue":"3 Sek. absenken · 1 Sek. unten halten · kontrolliert hoch","type":"reps"},
    {"name":"Liegestütze","amount":"6–12 Wiederholungen","cue":"Körper gerade · langsam absenken · 1–3 saubere Wiederholungen im Tank lassen","type":"reps"},
    {"name":"Rückwärts-Ausfallschritte","amount":"8 je Bein","cue":"Kontrolliert zurücksetzen · vorderes Knie stabil","type":"reps"},
    {"name":"Reverse Snow Angels","amount":"10–15 Wiederholungen","cue":"Bauchlage · Arme knapp über Boden langsam von Hüfte Richtung Kopf führen","type":"reps"},
    {"name":"Bird Dog","amount":"8–12 je Seite","cue":"Arm und Gegenbein strecken · jeweils 3 Sek. halten","type":"reps"},
    {"name":"Glute Bridge","amount":"15 Wiederholungen","cue":"Oben jeweils 2 Sek. Gesäß kräftig anspannen","type":"reps"},
    {"name":"Plank","amount":"40 Sekunden","cue":"Bauch und Gesäß fest · Körper gerade","type":"timed","seconds":40},
]

WORKOUT_CORE = [
    {"name":"Y-T-W","amount":"5–8 Durchgänge","cue":"Bauchlage · Arme nacheinander als Y, T und W anheben","type":"reps"},
    {"name":"Reverse Snow Angels","amount":"10–15 Wiederholungen","cue":"Ruhig und kontrolliert · Arme knapp über Boden","type":"reps"},
    {"name":"Bird Dog","amount":"8 je Seite","cue":"Jeweils 3 Sek. in Endposition halten","type":"reps"},
    {"name":"Scapular Push-ups","amount":"10–15 Wiederholungen","cue":"Arme gestreckt · nur Schulterblätter bewegen","type":"reps"},
    {"name":"Glute Bridge","amount":"15 Wiederholungen","cue":"Oben 2 Sek. halten","type":"reps"},
    {"name":"Seitstütz links","amount":"25 Sekunden","cue":"Hüfte hoch · Körper gerade","type":"timed","seconds":25},
    {"name":"Seitstütz rechts","amount":"25 Sekunden","cue":"Hüfte hoch · Körper gerade","type":"timed","seconds":25},
]

WORKOUT_B = [
    {"name":"Split Squats","amount":"8–10 je Bein","cue":"Langsam absenken · kontrolliert hoch","type":"reps"},
    {"name":"Liegestütze","amount":"6–12 Wiederholungen","cue":"3 Sek. absenken · sauber hochdrücken","type":"reps"},
    {"name":"Kniebeugen","amount":"12–15 Wiederholungen","cue":"Langsam und kontrolliert","type":"reps"},
    {"name":"Y-T-W","amount":"5–8 Durchgänge","cue":"Schulterblätter aktiv nach hinten/unten führen","type":"reps"},
    {"name":"Bird Dog","amount":"8–12 je Seite","cue":"3 Sek. in Endposition halten","type":"reps"},
    {"name":"Glute Bridge","amount":"15 Wiederholungen","cue":"Oben 2 Sek. halten","type":"reps"},
    {"name":"Seitstütz links","amount":"30 Sekunden","cue":"Hüfte nicht absinken lassen","type":"timed","seconds":30},
    {"name":"Seitstütz rechts","amount":"30 Sekunden","cue":"Hüfte nicht absinken lassen","type":"timed","seconds":30},
]

STRETCH = [
    {"name":"Brustdehnung links","seconds":30,"cue":"Arm am Türrahmen · Oberkörper leicht wegdrehen"},
    {"name":"Brustdehnung rechts","seconds":30,"cue":"Arm am Türrahmen · Oberkörper leicht wegdrehen"},
    {"name":"Lat-/Rückendehnung","seconds":40,"cue":"Hände auf Tisch · Hüfte zurück · Brust Richtung Boden"},
    {"name":"Hüftbeuger links","seconds":30,"cue":"Ausfallschritt · Becken leicht nach vorne"},
    {"name":"Hüftbeuger rechts","seconds":30,"cue":"Ausfallschritt · Becken leicht nach vorne"},
    {"name":"Quadrizeps links","seconds":30,"cue":"Ferse Richtung Gesäß · Knie nebeneinander"},
    {"name":"Quadrizeps rechts","seconds":30,"cue":"Ferse Richtung Gesäß · Knie nebeneinander"},
    {"name":"Wade links","seconds":30,"cue":"Hintere Ferse am Boden"},
    {"name":"Wade rechts","seconds":30,"cue":"Hintere Ferse am Boden"},
    {"name":"Figure-4 Gesäß links","seconds":30,"cue":"Ruhig ziehen · nicht federn"},
    {"name":"Figure-4 Gesäß rechts","seconds":30,"cue":"Ruhig ziehen · nicht federn"},
]

# -------------------------------------------------
# Session state
# -------------------------------------------------
defaults = {
    "active_workout": None,
    "round": 1,
    "exercise_index": 0,
    "phase": "idle",        # idle, exercise, rest, round_rest, stretch, done
    "timer_end": None,
    "stretch_index": 0,
    "rounds_total": 0,
    "exercise_list": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Einmaliger Reset nach diesem Update, damit kein altes Training fälschlich als aktiv erscheint.
APP_STATE_VERSION = "2026-09-05-v6-fixed-nav-ultracompact"
if st.session_state.get("_app_state_version") != APP_STATE_VERSION:
    for k, v in defaults.items():
        st.session_state[k] = v
    st.session_state["_app_state_version"] = APP_STATE_VERSION


# -------------------------------------------------
# Tages-Dashboard / Fortschritt
# -------------------------------------------------
PROGRESS_FILE = Path(".fit_progress.json")

DAILY_TASKS = {
    "Montag": [
        ("projects", "📌 Projekte – 60 Minuten konzentriert arbeiten"),
        ("regeneration", "🟦 Regeneration / kein Zusatztraining"),
        ("meal_16", "🥗 16:00 – Proteinmahlzeit + Gemüse"),
        ("meal_evening", "🍤 19:30–20:00 – Proteinmahlzeit + Gemüse"),
        ("fluids", "💧 Ausreichend trinken"),
    ],
    "Dienstag": [
        ("projects", "📌 Projekte – 60 Minuten konzentriert arbeiten"),
        ("dog", "🐕 4 km mit dem Hund"),
        ("workout", "💪 Kraft A – 3 Zirkel"),
        ("stretch", "🧘 4–5 Min Stretching"),
        ("meal_16", "🥗 16:00 – Proteinmahlzeit + Gemüse"),
        ("meal_evening", "🍤 19:30–20:00 – Proteinmahlzeit + Gemüse"),
        ("fluids", "💧 Ausreichend trinken"),
    ],
    "Mittwoch": [
        ("projects", "📌 Projekte – 60 Minuten konzentriert arbeiten"),
        ("treadmill", "🏃 Laufband – 45 Min · 4,4 km/h · 10 %"),
        ("meal_16", "🥗 16:00 – Proteinmahlzeit + Gemüse"),
        ("meal_evening", "🍤 19:30–20:00 – Proteinmahlzeit + Gemüse"),
        ("fluids", "💧 Ausreichend trinken"),
    ],
    "Donnerstag": [
        ("projects", "📌 Projekte – 60 Minuten konzentriert arbeiten"),
        ("dog", "🐕 4 km mit dem Hund"),
        ("workout", "🧍 Rücken/Core – 2 leichte Zirkel"),
        ("stretch", "🧘 4–5 Min Stretching"),
        ("meal_16", "🥗 16:00 – Proteinmahlzeit + Gemüse"),
        ("meal_evening", "🍤 19:30–20:00 – Proteinmahlzeit + Gemüse"),
        ("fluids", "💧 Ausreichend trinken"),
    ],
    "Freitag": [
        ("projects", "📌 Projekte – 60 Minuten konzentriert arbeiten"),
        ("dog", "🐕 4 km mit dem Hund"),
        ("workout", "💪 Kraft B – 3 Zirkel"),
        ("stretch", "🧘 4–5 Min Stretching"),
        ("meal_16", "🥗 16:00 – Proteinmahlzeit + Gemüse"),
        ("meal_evening", "🍤 19:30–20:00 – Proteinmahlzeit + Gemüse"),
        ("fluids", "💧 Ausreichend trinken"),
    ],
    "Samstag": [
        ("projects", "📌 Projekte – 60 Minuten konzentriert arbeiten"),
        ("treadmill", "🏃 Laufband – 45 Min · 4,4 km/h · 10 %"),
        ("meal_16", "🥗 16:00 – Proteinmahlzeit + Gemüse"),
        ("meal_evening", "🍤 19:30–20:00 – Proteinmahlzeit + Gemüse"),
        ("fluids", "💧 Ausreichend trinken"),
    ],
    "Sonntag": [
        ("projects", "📌 Projekte – 60 Minuten konzentriert arbeiten"),
        ("treadmill", "🏃 Laufband – 45 Min · 4,4 km/h · 10 %"),
        ("weekly_check", "⚖️ Gewicht / Wochencheck dokumentieren"),
        ("meal_16", "🥗 16:00 – Proteinmahlzeit + Gemüse"),
        ("meal_evening", "🍤 19:30–20:00 – Proteinmahlzeit + Gemüse"),
        ("fluids", "💧 Ausreichend trinken"),
    ],
}

def load_progress():
    if "daily_progress" in st.session_state:
        return st.session_state.daily_progress
    data = {}
    try:
        if PROGRESS_FILE.exists():
            data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                data = {}
    except Exception:
        data = {}
    st.session_state.daily_progress = data
    return data


def save_progress(data):
    st.session_state.daily_progress = data
    try:
        PROGRESS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        # Session-State funktioniert auch dann weiter, wenn das Dateisystem nicht beschreibbar ist.
        pass


def set_task(date_key, task_id, value):
    data = load_progress()
    day_data = data.setdefault(date_key, {})
    day_data[task_id] = bool(value)
    save_progress(data)


def render_daily_dashboard(day_name):
    st.markdown("### ✅ Mein Tages-Dashboard")
    st.caption("Aufgaben von heute oder gestern nachtragen und abhaken.")

    today = local_today()
    view = st.radio(
        "Tag auswählen",
        ["Heute", "Gestern"],
        horizontal=True,
        label_visibility="collapsed",
        key="dashboard_day_choice",
    )
    selected_date = today if view == "Heute" else today - timedelta(days=1)
    selected_day_name = GERMAN_DAYS[selected_date.weekday()]
    tasks = DAILY_TASKS.get(selected_day_name, [])
    date_key = selected_date.isoformat()
    saved = load_progress().get(date_key, {})

    if view == "Gestern":
        st.caption(f"Nachtragen für {selected_day_name}, {selected_date.strftime('%d.%m.%Y')}")

    done_count = sum(bool(saved.get(task_id, False)) for task_id, _ in tasks)
    st.metric(f"{view} erledigt", f"{done_count}/{len(tasks)}")

    for task_id, label in tasks:
        key = f"task_{date_key}_{task_id}"
        if key not in st.session_state:
            st.session_state[key] = bool(saved.get(task_id, False))
        value = st.checkbox(label, key=key)
        if bool(saved.get(task_id, False)) != bool(value):
            set_task(date_key, task_id, value)
            saved[task_id] = bool(value)

    new_done_count = sum(bool(st.session_state.get(f"task_{date_key}_{task_id}", False)) for task_id, _ in tasks)
    if tasks and new_done_count == len(tasks):
        st.success(f"🎉 {view} vollständig erledigt!")


def get_treadmill_data(date_key):
    data = load_progress()
    day_data = data.setdefault(date_key, {})
    treadmill = day_data.get("_treadmill", {})
    if not isinstance(treadmill, dict):
        treadmill = {}
    return treadmill


def save_treadmill_data(date_key, minutes, speed):
    data = load_progress()
    day_data = data.setdefault(date_key, {})
    day_data["_treadmill"] = {
        "minutes": int(minutes),
        "speed": float(speed),
    }
    save_progress(data)


def render_treadmill_input(date_value=None, key_prefix="today"):
    if date_value is None:
        date_value = local_today()
    date_key = date_value.isoformat()
    saved = get_treadmill_data(date_key)

    st.markdown("#### 🏃 Laufband")
    c1, c2 = st.columns(2)
    minutes = c1.number_input(
        "Gelaufene Zeit (Minuten)",
        min_value=0,
        max_value=240,
        value=int(saved.get("minutes", 45)),
        step=1,
        key=f"{key_prefix}_treadmill_minutes_{date_key}",
    )
    speed = c2.number_input(
        "Geschwindigkeit (km/h)",
        min_value=0.0,
        max_value=15.0,
        value=float(saved.get("speed", 4.4)),
        step=0.1,
        format="%.1f",
        key=f"{key_prefix}_treadmill_speed_{date_key}",
    )

    distance_m = speed * (minutes / 60.0) * 1000.0
    steps = distance_m * 1.5

    m1, m2, m3 = st.columns(3)
    m1.metric("Zeit", f"{minutes} min")
    m2.metric("Strecke", f"{distance_m:,.0f} m".replace(",", "."))
    m3.metric("Schritte", f"{steps:,.0f}".replace(",", "."))
    st.caption("Berechnung: Strecke = Geschwindigkeit × Zeit; Schritte = Meter × 1,5.")

    previous = (int(saved.get("minutes", 45)), float(saved.get("speed", 4.4)))
    current = (int(minutes), float(speed))
    if current != previous:
        save_treadmill_data(date_key, minutes, speed)

    return minutes, speed, distance_m, steps


def monthly_progress_box():
    st.markdown("### 🎯 Aufgaben im Monat")
    st.caption("Die Häkchen aus dem Tages-Dashboard werden hier zusammengefasst.")

    data = load_progress()
    today = local_today()
    year, month = today.year, today.month
    month_label = datetime.now().strftime("%B %Y")

    # Deutsche Monatsnamen für die Überschrift
    german_months = ["", "Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
    st.markdown(f"#### {german_months[month]} {year}")

    completed_days = 0
    active_days = 0
    completed_tasks = 0
    possible_tasks = 0

    rows = []
    _, last_day = calendar.monthrange(year, month)
    for d in range(1, last_day + 1):
        dt = date(year, month, d)
        if dt > today:
            continue
        day_name = GERMAN_DAYS[dt.weekday()]
        tasks = DAILY_TASKS.get(day_name, [])
        if not tasks:
            continue
        active_days += 1
        possible_tasks += len(tasks)
        saved = data.get(dt.isoformat(), {})
        done = sum(bool(saved.get(task_id, False)) for task_id, _ in tasks)
        completed_tasks += done
        if done == len(tasks):
            completed_days += 1
        rows.append({
            "Datum": dt.strftime("%d.%m."),
            "Tag": day_name[:2],
            "Erledigt": f"{done}/{len(tasks)}",
            "%": round(100 * done / len(tasks)) if tasks else 0,
        })

    c1, c2, c3 = st.columns(3)
    c1.metric("Komplette Tage", f"{completed_days}/{active_days}")
    c2.metric("Aufgaben", f"{completed_tasks}/{possible_tasks}")
    pct = round(100 * completed_tasks / possible_tasks) if possible_tasks else 0
    c3.metric("Monat", f"{pct} %")
    st.progress(pct / 100 if possible_tasks else 0.0)

    if rows:
        # Die letzten 14 Tage reichen auf dem Handy und bleiben übersichtlich.
        st.dataframe(pd.DataFrame(rows[-14:]), use_container_width=True, hide_index=True)
    else:
        st.info("Noch keine Einträge in diesem Monat.")

    st.caption("Hinweis: Auf Streamlit Cloud werden die Häkchen zusätzlich im Session-State gehalten. Nach einem kompletten App-Neustart oder Redeploy kann die lokale Datei zurückgesetzt werden.")

def reset_workout():
    for k, v in defaults.items():
        st.session_state[k] = v

def begin_workout(name, exercises, rounds):
    st.session_state.active_workout = name
    st.session_state.exercise_list = exercises
    st.session_state.rounds_total = rounds
    st.session_state.round = 1
    st.session_state.exercise_index = 0
    st.session_state.phase = "exercise"
    st.session_state.timer_end = None
    st.session_state.stretch_index = 0

def begin_stretching():
    st.session_state.active_workout = "Nur Dehnung"
    st.session_state.exercise_list = []
    st.session_state.rounds_total = 0
    st.session_state.round = 1
    st.session_state.exercise_index = 0
    st.session_state.phase = "stretch"
    st.session_state.timer_end = None
    st.session_state.stretch_index = 0

def jump_to_exercise(index):
    if not st.session_state.exercise_list:
        return
    index = max(0, min(index, len(st.session_state.exercise_list) - 1))
    st.session_state.exercise_index = index
    st.session_state.phase = "exercise"
    st.session_state.timer_end = None

def previous_exercise():
    jump_to_exercise(st.session_state.exercise_index - 1)

def next_exercise_direct():
    jump_to_exercise(st.session_state.exercise_index + 1)

def next_exercise():
    idx = st.session_state.exercise_index
    if idx + 1 < len(st.session_state.exercise_list):
        st.session_state.exercise_index += 1
        st.session_state.phase = "rest"
        st.session_state.timer_end = time.time() + 20
    else:
        if st.session_state.round < st.session_state.rounds_total:
            st.session_state.round += 1
            st.session_state.exercise_index = 0
            st.session_state.phase = "round_rest"
            st.session_state.timer_end = time.time() + 75
        else:
            st.session_state.phase = "stretch"
            st.session_state.stretch_index = 0
            st.session_state.timer_end = None

def start_timed_exercise(seconds):
    st.session_state.timer_end = time.time() + seconds

def render_timer(seconds, label):
    """Kompakter browserseitiger Countdown."""
    html = f"""
    <div style="text-align:center;font-family:Arial,sans-serif;margin:0;padding:0;">
      <div style="font-size:13px;color:#93c5fd;font-weight:700;">{label}</div>
      <div id="timer" style="font-size:44px;font-weight:800;line-height:1;color:#60a5fa;">{seconds}</div>
      <div style="font-size:11px;color:#93c5fd;">Sek.</div>
    </div>
    <script>
      let remaining = {seconds};
      const el = document.getElementById("timer");
      const interval = setInterval(() => {{
        remaining -= 1;
        if (remaining >= 0) el.innerText = remaining;
        if (remaining <= 0) {{
          clearInterval(interval);
          el.innerText = "✓";
        }}
      }}, 1000);
    </script>
    """
    st.components.v1.html(html, height=78)



def stretch_illustration(name):
    """Bevorzugt lokale männliche Dehnungsbilder; SVG bleibt als Fallback."""
    key = name.lower()

    stretch_local = None
    mirror = False
    if "brustdehnung" in key:
        stretch_local = "assets_male/brustdehnung.png"
        mirror = "rechts" in key
    elif "lat-/rückendehnung" in key:
        stretch_local = "assets_male/rueckendehnung.png"
    elif "hüftbeuger" in key:
        stretch_local = "assets_male/hueftbeuger.png"
        mirror = "rechts" in key
    elif "quadrizeps" in key:
        stretch_local = "assets_male/quadrizeps.png"
        mirror = "rechts" in key
    elif "wade" in key:
        stretch_local = "assets_male/wadendehnung.png"
        mirror = "rechts" in key

    if stretch_local and Path(stretch_local).exists():
        if mirror:
            from PIL import Image, ImageOps
            st.image(ImageOps.mirror(Image.open(stretch_local)), width=250)
        else:
            st.image(stretch_local, width=250)
        return

    def wrap(body, label):
        return f"""
        <div style="max-width:500px;margin:4px auto 12px auto;padding:10px;border:1px solid #dbe3ee;border-radius:18px;background:#f8fbff;">
          <svg viewBox="0 0 320 210" width="100%" height="210" xmlns="http://www.w3.org/2000/svg">
            <rect x="1" y="1" width="318" height="208" rx="16" fill="#ffffff" stroke="#e2e8f0"/>
            <line x1="22" y1="180" x2="298" y2="180" stroke="#cbd5e1" stroke-width="3"/>
            {body}
            <text x="160" y="201" text-anchor="middle" font-size="13" fill="#475569">{label}</text>
          </svg>
        </div>
        """

    person = 'stroke="#163a63" stroke-width="7" stroke-linecap="round" fill="none"'
    head = 'fill="#dbeafe" stroke="#163a63" stroke-width="3"'

    if "brustdehnung" in key:
        side = "links" if "links" in key else "rechts"
        xarm = 245 if side == "links" else 75
        body = f'''<line x1="{xarm}" y1="35" x2="{xarm}" y2="170" stroke="#94a3b8" stroke-width="8"/>
          <circle cx="160" cy="55" r="13" {head}/><line x1="160" y1="68" x2="160" y2="122" {person}/>
          <line x1="160" y1="82" x2="{xarm}" y2="82" {person}/><line x1="160" y1="82" x2="125" y2="100" {person}/>
          <line x1="160" y1="122" x2="135" y2="178" {person}/><line x1="160" y1="122" x2="185" y2="178" {person}/>'''
        return wrap(body, f"Brustdehnung {side}: Arm am Türrahmen, Oberkörper wegdrehen")

    if "lat-/rückendehnung" in key:
        body=f'''<line x1="190" y1="92" x2="292" y2="92" stroke="#94a3b8" stroke-width="7"/><line x1="270" y1="92" x2="270" y2="180" stroke="#94a3b8" stroke-width="7"/>
          <circle cx="105" cy="95" r="13" {head}/><line x1="118" y1="99" x2="165" y2="120" {person}/><line x1="165" y1="120" x2="205" y2="92" {person}/>
          <line x1="150" y1="113" x2="190" y2="92" {person}/><line x1="165" y1="120" x2="135" y2="178" {person}/><line x1="165" y1="120" x2="188" y2="178" {person}/>'''
        return wrap(body, "Hände aufstützen · Hüfte zurück · Brust Richtung Boden")

    if "hüftbeuger" in key:
        body=f'''<circle cx="150" cy="48" r="13" {head}/><line x1="150" y1="61" x2="150" y2="112" {person}/>
          <line x1="150" y1="78" x2="120" y2="98" {person}/><line x1="150" y1="78" x2="180" y2="98" {person}/>
          <line x1="150" y1="112" x2="105" y2="135" {person}/><line x1="105" y1="135" x2="80" y2="180" {person}/>
          <line x1="150" y1="112" x2="202" y2="142" {person}/><line x1="202" y1="142" x2="242" y2="180" {person}/>'''
        return wrap(body, "Ausfallschritt · Becken leicht nach vorne schieben")

    if "quadrizeps" in key:
        body=f'''<circle cx="150" cy="45" r="13" {head}/><line x1="150" y1="58" x2="150" y2="118" {person}/>
          <line x1="150" y1="76" x2="120" y2="98" {person}/><line x1="150" y1="76" x2="180" y2="98" {person}/>
          <line x1="150" y1="118" x2="128" y2="180" {person}/><line x1="150" y1="118" x2="188" y2="145" {person}/>
          <line x1="188" y1="145" x2="170" y2="118" {person}/><line x1="180" y1="98" x2="170" y2="118" {person}/>'''
        return wrap(body, "Ferse zum Gesäß · Knie möglichst nebeneinander")

    if "wade" in key:
        body=f'''<line x1="255" y1="30" x2="255" y2="180" stroke="#94a3b8" stroke-width="8"/>
          <circle cx="160" cy="55" r="13" {head}/><line x1="160" y1="68" x2="170" y2="120" {person}/><line x1="165" y1="82" x2="235" y2="82" {person}/>
          <line x1="170" y1="120" x2="210" y2="178" {person}/><line x1="170" y1="120" x2="105" y2="172" {person}/><line x1="105" y1="172" x2="78" y2="180" {person}/>'''
        return wrap(body, "Hinteres Bein gestreckt · hintere Ferse bleibt am Boden")

    if "figure-4" in key:
        body=f'''<circle cx="105" cy="75" r="13" {head}/><line x1="118" y1="82" x2="162" y2="113" {person}/>
          <line x1="162" y1="113" x2="205" y2="145" {person}/><line x1="205" y1="145" x2="242" y2="180" {person}/>
          <line x1="162" y1="113" x2="137" y2="145" {person}/><line x1="137" y1="145" x2="198" y2="145" {person}/>'''
        return wrap(body, "Knöchel auf das andere Knie · Gesäß sanft dehnen")

    return wrap(f'''<circle cx="160" cy="55" r="13" {head}/><line x1="160" y1="68" x2="160" y2="125" {person}/><line x1="160" y1="82" x2="120" y2="105" {person}/><line x1="160" y1="82" x2="200" y2="105" {person}/><line x1="160" y1="125" x2="135" y2="180" {person}/><line x1="160" y1="125" x2="185" y2="180" {person}/>''', name)


def workout_runner():
    phase = st.session_state.phase
    exercises = st.session_state.exercise_list
    n_ex = len(exercises)

    # =========================
    # KRAFT / CORE
    # =========================
    if phase in ["exercise", "rest", "round_rest"] and n_ex:
        # Direkte Navigation soll nicht durch alte Pausenzustände blockiert werden.
        if phase in ["rest", "round_rest"]:
            st.session_state.phase = "exercise"
            st.session_state.timer_end = None

        idx = st.session_state.exercise_index
        ex = exercises[idx]
        ex_no = idx + 1

        # WICHTIG: Key enthält den aktuellen Index.
        # Dadurch springt Streamlit nach "Weiter" nicht wieder auf die alte Auswahl zurück.
        selected_name = st.selectbox(
            "Direkt auswählen",
            [x["name"] for x in exercises],
            index=idx,
            key=f"direct_exercise_{st.session_state.active_workout}_{idx}",
            label_visibility="collapsed",
        )
        selected_index = next(i for i, x in enumerate(exercises) if x["name"] == selected_name)
        if selected_index != idx:
            jump_to_exercise(selected_index)
            st.rerun()

        st.markdown(
            f'<div class="compact-note">Runde {st.session_state.round}/{st.session_state.rounds_total} · '
            f'Übung {ex_no}/{n_ex}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(f"""
        <div class="fit-card">
          <div class="name">{ex['name']}</div>
          <div class="amount">{ex['amount']}</div>
          <div class="cue">{ex['cue']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Bild + Timer/Angabe nebeneinander.
        left, right = st.columns([1.7, 0.75], gap="small")
        with left:
            show_exercise_animation(ex["name"])

        with right:
            if ex["type"] == "timed":
                if st.session_state.timer_end is None:
                    st.markdown(
                        f"<div style='text-align:center;font-size:13px;font-weight:700;margin-top:6px'>"
                        f"⏱ {ex['seconds']} Sek.</div>",
                        unsafe_allow_html=True,
                    )
                    if st.button("▶ START", use_container_width=True, type="primary",
                                 key=f"timer_start_{st.session_state.round}_{idx}"):
                        start_timed_exercise(ex["seconds"])
                        st.rerun()
                else:
                    remaining = max(0, int(st.session_state.timer_end - time.time()))
                    render_timer(remaining, "Timer")
            else:
                st.markdown(
                    f"<div style='text-align:center;margin-top:10px'>"
                    f"<div style='font-size:11px;color:#94a3b8'>Wiederholungen</div>"
                    f"<div style='font-size:17px;font-weight:800'>{ex['amount']}</div></div>",
                    unsafe_allow_html=True,
                )

        # Nur eine kompakte Navigationszeile.
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("⬅ Zurück", use_container_width=True, disabled=(idx == 0),
                         key=f"prev_{st.session_state.round}_{idx}"):
                st.session_state.timer_end = None
                jump_to_exercise(idx - 1)
                st.rerun()

        with b2:
            # "Erledigt" = tatsächlich zur nächsten Übung; am Rundenende nächste Runde / Dehnung.
            if st.button("✅ Erledigt", use_container_width=True, type="primary",
                         key=f"done_{st.session_state.round}_{idx}"):
                st.session_state.timer_end = None
                if idx < n_ex - 1:
                    jump_to_exercise(idx + 1)
                elif st.session_state.round < st.session_state.rounds_total:
                    st.session_state.round += 1
                    jump_to_exercise(0)
                else:
                    begin_stretching()
                st.rerun()

        with b3:
            if idx < n_ex - 1:
                if st.button("Weiter ➡", use_container_width=True,
                             key=f"next_{st.session_state.round}_{idx}"):
                    st.session_state.timer_end = None
                    jump_to_exercise(idx + 1)
                    st.rerun()
            else:
                if st.button("🧘 Dehnung", use_container_width=True,
                             key=f"stretch_{st.session_state.round}_{idx}"):
                    begin_stretching()
                    st.rerun()

        # Dehnung jederzeit direkt erreichbar.
        if idx < n_ex - 1:
            if st.button("🧘 Direkt zur Dehnung", use_container_width=True,
                         key=f"stretch_direct_{st.session_state.round}_{idx}"):
                begin_stretching()
                st.rerun()

    # =========================
    # DEHNUNG
    # =========================
    elif phase == "stretch":
        idx = st.session_state.stretch_index
        if idx >= len(STRETCH):
            st.session_state.phase = "done"
            st.rerun()

        # Auch hier Key mit aktuellem Index -> kein Zurückspringen nach Weiter.
        stretch_name = st.selectbox(
            "Dehnung direkt auswählen",
            [x["name"] for x in STRETCH],
            index=idx,
            key=f"direct_stretch_select_{idx}",
            label_visibility="collapsed",
        )
        new_idx = next(i for i, x in enumerate(STRETCH) if x["name"] == stretch_name)
        if new_idx != idx:
            st.session_state.stretch_index = new_idx
            st.session_state.timer_end = None
            st.rerun()

        idx = st.session_state.stretch_index
        s = STRETCH[idx]

        st.markdown(
            f'<div class="compact-note">Dehnung {idx+1}/{len(STRETCH)}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(f"""
        <div class="fit-card">
          <div class="name">{s['name']}</div>
          <div class="amount">{s['seconds']} Sekunden</div>
          <div class="cue">{s['cue']}</div>
        </div>
        """, unsafe_allow_html=True)

        left, right = st.columns([1.7, 0.75], gap="small")
        with left:
            stretch_illustration(s["name"])
        with right:
            render_timer(s["seconds"], "Dehnung")

        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("⬅ Zurück", use_container_width=True, disabled=(idx == 0),
                         key=f"stretch_prev_{idx}"):
                st.session_state.stretch_index = idx - 1
                st.session_state.timer_end = None
                st.rerun()

        with b2:
            if st.button("✅ Erledigt", use_container_width=True, type="primary",
                         key=f"stretch_done_{idx}"):
                if idx < len(STRETCH) - 1:
                    st.session_state.stretch_index = idx + 1
                else:
                    st.session_state.phase = "done"
                st.session_state.timer_end = None
                st.rerun()

        with b3:
            if idx < len(STRETCH) - 1:
                if st.button("Weiter ➡", use_container_width=True,
                             key=f"stretch_next_{idx}"):
                    st.session_state.stretch_index = idx + 1
                    st.session_state.timer_end = None
                    st.rerun()
            else:
                if st.button("Fertig ✓", use_container_width=True, type="primary",
                             key="stretch_finish"):
                    st.session_state.phase = "done"
                    st.rerun()

    elif phase == "done":
        st.success("🎉 Training / Dehnung geschafft!")
        if st.button("Beenden", use_container_width=True, type="primary"):
            reset_workout()
            st.rerun()

# -------------------------------------------------
# App
# -------------------------------------------------
today_name = GERMAN_DAYS[local_today().weekday()]
icon, typ, summary = WEEK_PLAN[today_name]

# Während eines laufenden Trainings möglichst keinen Platz oberhalb der Übung verbrauchen.
if st.session_state.active_workout:
    st.markdown("### 💪 Fit 88")
else:
    st.title("💪 Fit 88")
    render_daily_dashboard(today_name)
    st.caption("Training ohne Geräte · Wochenplan · Gewicht · Ernährung")
    st.markdown(f"### Heute: {today_name}")
    st.info(f"{icon} **{typ}**  \n{summary}")

tabs = st.tabs(["🏠 Heute", "▶️ Training", "📅 Woche", "🎯 Aufgaben", "⚖️ Gewicht", "🥗 Ernährung"])

with tabs[0]:
    st.markdown("### 🏋️ Training heute")

    if st.session_state.active_workout:
        st.info(f"▶️ Ausgewählt: **{st.session_state.active_workout}**")
        st.caption("Zum Ansehen oder Fortsetzen bitte oben auf „▶️ Training“ tippen.")
        if st.button("⛔ Auswahl zurücksetzen", use_container_width=True, key="today_reset_workout"):
            reset_workout()
            st.rerun()
    elif today_name == "Dienstag":
        st.write("🐕 4 km mit dem Hund → danach Kraft A → Stretching")
        if st.button("▶️ HEUTIGES TRAINING STARTEN", use_container_width=True, type="primary", key="today_train_tuesday"):
            begin_workout("Kraft A", WORKOUT_A, 3)
            st.rerun()
    elif today_name == "Donnerstag":
        st.write("🐕 4 km mit dem Hund → danach Rücken/Core → Stretching")
        if st.button("▶️ HEUTIGES TRAINING STARTEN", use_container_width=True, type="primary", key="today_train_thursday"):
            begin_workout("Rücken/Core", WORKOUT_CORE, 2)
            st.rerun()
    elif today_name == "Freitag":
        st.write("🐕 4 km mit dem Hund → danach Kraft B → Stretching")
        if st.button("▶️ HEUTIGES TRAINING STARTEN", use_container_width=True, type="primary", key="today_train_friday"):
            begin_workout("Kraft B", WORKOUT_B, 3)
            st.rerun()
    elif today_name in ["Mittwoch", "Samstag", "Sonntag"]:
        render_treadmill_input(local_today(), key_prefix="today")
        st.metric("Steigung", "10 %")
        st.write("🏃 Gleichmäßig laufen. Krafttraining kannst du unabhängig davon im Tab „Training“ ansehen.")
    else:
        st.success("🟦 Heute ist Regenerationstag.")
        st.caption("Krafttraining kannst du unabhängig davon im Tab „Training“ ansehen.")

with tabs[1]:
    if st.session_state.active_workout:
        workout_runner()
    else:
        st.markdown("### Training auswählen")
        st.caption("Krafttraining oder Dehnung direkt öffnen.")

        if st.button("🧘 NUR DEHNUNG", use_container_width=True, key="select_stretch_only"):
            begin_stretching()
            st.rerun()

        c1, c2, c3 = st.columns(3)
        with c1:
            choose_a = st.button("Kraft A", use_container_width=True, key="select_workout_a")
        with c2:
            choose_core = st.button("Rücken/Core", use_container_width=True, key="select_workout_core")
        with c3:
            choose_b = st.button("Kraft B", use_container_width=True, key="select_workout_b")

        if choose_a:
            begin_workout("Kraft A", WORKOUT_A, 3)
            st.rerun()
        elif choose_core:
            begin_workout("Rücken/Core", WORKOUT_CORE, 2)
            st.rerun()
        elif choose_b:
            begin_workout("Kraft B", WORKOUT_B, 3)
            st.rerun()

with tabs[2]:
    st.markdown("### Wochenplan")
    for day, (ic, tp, sm) in WEEK_PLAN.items():
        st.markdown(f"**{ic} {day} — {tp}**  \n{sm}")
        st.divider()

with tabs[3]:
    monthly_progress_box()

with tabs[4]:
    st.markdown("### Gewicht & 90-kg-Ziel")
    current_weight = st.number_input("Aktuelles Gewicht", 60.0, 160.0, 103.0, 0.1)
    weekly_loss = st.slider("Planungsannahme kg/Woche", 0.2, 1.5, 0.9, 0.1)

    remaining = max(0.0, current_weight - TARGET_WEIGHT)
    if weekly_loss > 0 and remaining > 0:
        weeks = remaining / weekly_loss
        target_date = local_today() + pd.Timedelta(days=math.ceil(weeks * 7))
        target_text = pd.Timestamp(target_date).strftime("%d.%m.%Y")
    elif remaining == 0:
        target_text = "Ziel erreicht"
    else:
        target_text = "—"

    c1, c2, c3 = st.columns(3)
    c1.metric("Aktuell", f"{current_weight:.1f} kg")
    c2.metric("Noch", f"{remaining:.1f} kg")
    c3.metric("≈ 90 kg", target_text)

    st.caption("Die Prognose ist nur eine lineare Planungshilfe. Wasser, Glykogen und sinkender Energieverbrauch können den tatsächlichen Verlauf verändern.")

    st.markdown("#### Wöchentlicher Check")
    st.number_input("Bauchumfang (cm)", 0.0, 200.0, 0.0, 0.5)
    st.number_input("Max. saubere Liegestütze", 0, 100, 0)
    st.slider("Subjektive Leistungsfähigkeit", 1, 10, 7)

with tabs[5]:
    st.markdown("### Ernährungsrahmen")
    st.markdown("""
**Bis 16:00 Uhr**
- Fasten, sofern es gut vertragen wird
- Wasser / kalorienfreie Getränke

**16:00 Uhr**
- ca. 300 g Hähnchenbrust
- 1 große Schlangengurke / Salat / anderes Gemüse
- 1 EL Olivenöl

**19:30–20:00 Uhr**
- ca. 300 g Garnelen
- Gemüse / zweite Gurke
- 2 Eier oder eine andere Proteinquelle

**Ziel**
- grob 150–170 g Protein/Tag
- ausreichende Flüssigkeit
- bei sehr kohlenhydratarmer Kost auf Elektrolyte und Mikronährstoffe achten
""")
    st.warning("Bei einer dauerhaft sehr niedrigen Kalorienzufuhr ist Protein allein kein vollständiger Schutz vor Muskel- oder Nährstoffverlust. Kreislauf, Leistungsfähigkeit und ggf. Laborwerte sollten mitbeachtet werden.")

st.divider()
st.caption("Progression: Wird eine Übung leicht, lieber langsamer oder anspruchsvoller ausführen statt unbegrenzt Wiederholungen hinzuzufügen.")
