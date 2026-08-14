
import streamlit as st
from datetime import date, datetime
import pandas as pd
import math
import time
import json
import calendar
from pathlib import Path

st.set_page_config(page_title="Fit bis 90 kg", page_icon="💪", layout="centered")

st.markdown("""
<style>
.block-container{max-width:760px;padding-top:1.1rem;padding-left:.8rem;padding-right:.8rem;padding-bottom:2rem;}
div[data-testid="stButton"]>button{min-height:52px;font-size:1.05rem;font-weight:700;border-radius:12px;}
div[data-testid="stMetric"]{background:rgba(127,127,127,.08);border-radius:12px;padding:.55rem;}
.stTabs [data-baseweb="tab-list"]{gap:.25rem;flex-wrap:wrap;}
.stTabs [data-baseweb="tab"]{padding-left:.55rem;padding-right:.55rem;}
@media (max-width:700px){h1{font-size:1.8rem!important}h2{font-size:1.45rem!important}h3{font-size:1.2rem!important}}
</style>
""", unsafe_allow_html=True)


# Übungsbilder aus dem lokalen assets-Ordner
EXERCISE_IMAGES = {
    "Kniebeugen": "assets/kniebeugen.png",
    "Liegestütze": "assets/liegestuetze.png",
    "Rückwärts-Ausfallschritte": "assets/ausfallschritte.png",
    "Split Squats": "assets/split_squats.png",
    "Reverse Snow Angels": "assets/reverse_snow_angels.png",
    "Y-T-W": "assets/ytw.png",
    "Bird Dog": "assets/bird_dog.png",
    "Glute Bridge": "assets/glute_bridge.png",
    "Plank": "assets/plank.png",
    "Scapular Push-ups": "assets/scapular_pushups.png",
    "Seitstütz links": "assets/seitstuetz.png",
    "Seitstütz rechts": "assets/seitstuetz.png",
}

def show_exercise_image(name):
    image_path = EXERCISE_IMAGES.get(name)
    if image_path and Path(image_path).exists():
        st.image(image_path, use_container_width=True)
        if name == "Rückwärts-Ausfallschritte":
            st.caption("Bild zeigt das Ausfallschritt-Prinzip; in Ihrem Programm wird der Schritt nach hinten ausgeführt.")

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
    st.caption("Alles, was heute zählt – einfach abhaken.")

    tasks = DAILY_TASKS.get(day_name, [])
    date_key = date.today().isoformat()
    saved = load_progress().get(date_key, {})

    done_count = sum(bool(saved.get(task_id, False)) for task_id, _ in tasks)
    total = max(1, len(tasks))
    st.progress(done_count / total)

    c1, c2 = st.columns([2, 1])
    c1.metric("Heute erledigt", f"{done_count}/{len(tasks)}")
    c2.metric("Fortschritt", f"{round(done_count / total * 100)} %")

    for task_id, label in tasks:
        key = f"task_{date_key}_{task_id}"
        # Ein gespeicherter Wert wird nur beim ersten Auftauchen des Widgets gesetzt.
        if key not in st.session_state:
            st.session_state[key] = bool(saved.get(task_id, False))
        value = st.checkbox(label, key=key)
        if bool(saved.get(task_id, False)) != bool(value):
            set_task(date_key, task_id, value)
            saved[task_id] = bool(value)

    new_done_count = sum(bool(st.session_state.get(f"task_{date_key}_{task_id}", False)) for task_id, _ in tasks)
    if tasks and new_done_count == len(tasks):
        st.success("🎉 Tagesziel vollständig erledigt!")


def monthly_progress_box():
    st.markdown("### 🎯 Aufgaben & Monatsfortschritt")
    st.caption("Die Häkchen aus dem Tages-Dashboard werden hier zusammengefasst.")

    data = load_progress()
    today = date.today()
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
    # Browserseitiger Countdown, ohne zusätzliche Pakete
    html = f"""
    <div style="text-align:center;font-family:Arial,sans-serif;">
      <div style="font-size:18px;margin-bottom:6px;">{label}</div>
      <div id="timer" style="font-size:64px;font-weight:700;line-height:1.1;">{seconds}</div>
      <div style="font-size:15px;margin-top:6px;">Sekunden</div>
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
    st.components.v1.html(html, height=130)



def exercise_animation(name):
    """Körpernähere 2-Phasen-Animation mit Technik-Hinweis."""
    key = name.lower()

    tips = {
        "kniebeugen": "Brust aufrecht · Knie folgen den Fußspitzen · Druck über den ganzen Fuß.",
        "liegestütze": "Körper bleibt wie ein Brett · Ellenbogen ca. 30–45° zum Oberkörper.",
        "rückwärts-ausfallschritte": "Großer Schritt nach hinten · vorderes Knie stabil über dem Fuß.",
        "split squats": "Oberkörper aufrecht · kontrolliert senken · vorderes Bein arbeitet.",
        "reverse snow angels": "Bauchlage · Schulterblätter nach hinten/unten · Nacken lang.",
        "y-t-w": "Arme nur so hoch wie sauber möglich · Schulterblätter aktiv zusammenführen.",
        "bird dog": "Becken bleibt ruhig · nicht ins Hohlkreuz · lang statt hoch strecken.",
        "glute bridge": "Rippen unten · Gesäß aktiv · nicht aus dem unteren Rücken überstrecken.",
        "plank": "Bauch und Gesäß fest · Kopf, Rücken und Beine bilden eine Linie.",
        "seitstütz links": "Hüfte aktiv hochdrücken · Schulter weg vom Ohr.",
        "seitstütz rechts": "Hüfte aktiv hochdrücken · Schulter weg vom Ohr.",
        "scapular push-ups": "Arme bleiben gestreckt · Bewegung kommt nur aus den Schulterblättern.",
    }

    def svg(body, label):
        return f"""
        <svg viewBox="0 0 260 170" width="100%" height="170" xmlns="http://www.w3.org/2000/svg">
          <rect x="1" y="1" width="258" height="168" rx="18" fill="#ffffff" stroke="#d9dee5"/>
          <line x1="18" y1="146" x2="242" y2="146" stroke="#c4cad2" stroke-width="3"/>
          <text x="130" y="162" text-anchor="middle" font-size="12" fill="#69717c">{label}</text>
          {body}
        </svg>
        """

    # neutral body helpers
    if "kniebeuge" in key:
        f1 = svg("""
          <circle cx="130" cy="34" r="11" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="130" y1="45" x2="130" y2="88" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="130" y1="58" x2="98" y2="72" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="58" x2="162" y2="72" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="88" x2="109" y2="116" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="109" y1="116" x2="101" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="130" y1="88" x2="151" y2="116" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="151" y1="116" x2="159" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
        """, "Start")
        f2 = svg("""
          <circle cx="130" cy="49" r="11" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="130" y1="60" x2="130" y2="96" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="130" y1="70" x2="92" y2="80" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="70" x2="168" y2="80" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="96" x2="96" y2="101" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="96" y1="101" x2="84" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="130" y1="96" x2="164" y2="101" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="164" y1="101" x2="176" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <path d="M130 64 C130 74 130 84 130 94" stroke="#5f6b7a" stroke-width="2" fill="none"/>
        """, "Tiefposition")

    elif "liegest" in key:
        f1 = svg("""
          <circle cx="62" cy="72" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="72" y1="76" x2="128" y2="91" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="128" y1="91" x2="183" y2="108" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="95" y1="82" x2="87" y2="128" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="121" y1="89" x2="111" y2="130" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="183" y1="108" x2="207" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
        """, "Oben")
        f2 = svg("""
          <circle cx="65" cy="111" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="75" y1="112" x2="132" y2="115" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="132" y1="115" x2="185" y2="121" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="99" y1="114" x2="80" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="122" y1="115" x2="108" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="185" y1="121" x2="207" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
        """, "Unten")

    elif "ausfallschritt" in key or "split squat" in key:
        f1 = svg("""
          <circle cx="126" cy="34" r="11" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="126" y1="45" x2="126" y2="88" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="126" y1="58" x2="98" y2="74" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="126" y1="58" x2="154" y2="74" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="126" y1="88" x2="86" y2="111" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="86" y1="111" x2="70" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="126" y1="88" x2="169" y2="116" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="169" y1="116" x2="193" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
        """, "Ausgang")
        f2 = svg("""
          <circle cx="126" cy="49" r="11" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="126" y1="60" x2="126" y2="97" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="126" y1="70" x2="99" y2="84" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="126" y1="70" x2="153" y2="84" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="126" y1="97" x2="91" y2="100" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="91" y1="100" x2="71" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="126" y1="97" x2="166" y2="126" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="166" y1="126" x2="194" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
        """, "Tiefposition")

    elif "glute bridge" in key:
        f1 = svg("""
          <circle cx="57" cy="119" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="67" y1="121" x2="116" y2="128" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="116" y1="128" x2="159" y2="127" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="159" y1="127" x2="182" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="116" y1="128" x2="98" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
        """, "Unten")
        f2 = svg("""
          <circle cx="57" cy="119" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="67" y1="119" x2="114" y2="89" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="114" y1="89" x2="159" y2="103" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="159" y1="103" x2="182" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="114" y1="89" x2="99" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
        """, "Oben")

    elif "bird dog" in key:
        f1 = svg("""
          <circle cx="88" cy="77" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="98" y1="80" x2="137" y2="93" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="108" y1="83" x2="84" y2="128" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="128" y1="90" x2="115" y2="143" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="137" y1="93" x2="164" y2="143" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="108" y1="83" x2="80" y2="72" stroke="#222" stroke-width="6" stroke-linecap="round"/>
        """, "Vierfüßler")
        f2 = svg("""
          <circle cx="90" cy="83" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="100" y1="86" x2="138" y2="92" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="107" y1="87" x2="53" y2="61" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="126" y1="90" x2="115" y2="143" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="138" y1="92" x2="205" y2="73" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="107" y1="87" x2="91" y2="143" stroke="#222" stroke-width="6" stroke-linecap="round"/>
        """, "Strecken")

    elif "snow angel" in key:
        f1 = svg("""
          <circle cx="130" cy="40" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="130" y1="50" x2="130" y2="106" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="130" y1="67" x2="93" y2="99" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="67" x2="167" y2="99" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="106" x2="111" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="106" x2="149" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
        """, "Arme tief")
        f2 = svg("""
          <circle cx="130" cy="40" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="130" y1="50" x2="130" y2="106" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="130" y1="67" x2="78" y2="42" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="67" x2="182" y2="42" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="106" x2="111" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="106" x2="149" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
        """, "Arme hoch")

    elif "y-t-w" in key:
        f1 = svg("""
          <circle cx="130" cy="40" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="130" y1="50" x2="130" y2="106" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="130" y1="66" x2="82" y2="42" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="66" x2="178" y2="42" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="106" x2="111" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="106" x2="149" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
        """, "Y")
        f2 = svg("""
          <circle cx="130" cy="40" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="130" y1="50" x2="130" y2="106" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="130" y1="66" x2="78" y2="66" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="66" x2="182" y2="66" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="106" x2="111" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="106" x2="149" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
        """, "T / danach W")

    elif "seitstütz" in key:
        f1 = svg("""
          <circle cx="66" cy="100" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="76" y1="103" x2="132" y2="112" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="132" y1="112" x2="186" y2="122" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="94" y1="106" x2="82" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="186" y1="122" x2="207" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
        """, "Start")
        f2 = svg("""
          <circle cx="66" cy="82" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="76" y1="86" x2="132" y2="98" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="132" y1="98" x2="186" y2="111" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="94" y1="90" x2="82" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="186" y1="111" x2="207" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
        """, "Hüfte hoch")

    elif "plank" in key:
        f1 = svg("""
          <circle cx="64" cy="98" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="74" y1="101" x2="132" y2="112" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="132" y1="112" x2="189" y2="124" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="99" y1="106" x2="86" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="189" y1="124" x2="210" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
        """, "Nicht einsacken")
        f2 = svg("""
          <circle cx="64" cy="83" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="74" y1="86" x2="132" y2="98" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="132" y1="98" x2="189" y2="111" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="99" y1="91" x2="86" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="189" y1="111" x2="210" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
        """, "Saubere Linie")

    elif "scapular" in key:
        f1 = svg("""
          <circle cx="64" cy="83" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="74" y1="86" x2="132" y2="98" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="132" y1="98" x2="189" y2="111" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="99" y1="91" x2="86" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="189" y1="111" x2="210" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <path d="M99 91 Q116 77 133 95" fill="none" stroke="#7a8490" stroke-width="3"/>
        """, "Schulterblätter zusammen")
        f2 = svg("""
          <circle cx="64" cy="83" r="10" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="74" y1="86" x2="132" y2="98" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="132" y1="98" x2="189" y2="111" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="99" y1="91" x2="86" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="189" y1="111" x2="210" y2="145" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <path d="M99 96 Q116 112 133 99" fill="none" stroke="#7a8490" stroke-width="3"/>
        """, "Schulterblätter auseinander")

    else:
        f1 = svg("""
          <circle cx="130" cy="36" r="11" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="130" y1="47" x2="130" y2="96" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="130" y1="62" x2="96" y2="80" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="62" x2="164" y2="80" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="96" x2="111" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="130" y1="96" x2="149" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
        """, "Start")
        f2 = svg("""
          <circle cx="130" cy="36" r="11" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
          <line x1="130" y1="47" x2="130" y2="96" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="130" y1="62" x2="78" y2="58" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="62" x2="182" y2="58" stroke="#222" stroke-width="6" stroke-linecap="round"/>
          <line x1="130" y1="96" x2="111" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
          <line x1="130" y1="96" x2="149" y2="145" stroke="#222" stroke-width="7" stroke-linecap="round"/>
        """, "Ende")

    tip = tips.get(key, "Langsam, kontrolliert und nur im schmerzfreien Bewegungsbereich ausführen.")

    html = f"""
    <style>
      .anim-wrap {{
        position: relative;
        width: 100%;
        max-width: 480px;
        height: 178px;
        margin: 8px auto 6px auto;
      }}
      .anim-frame {{
        position: absolute;
        inset: 0;
        animation-duration: 2.0s;
        animation-iteration-count: infinite;
        animation-timing-function: steps(1,end);
      }}
      .frame-a {{ animation-name: phaseA; }}
      .frame-b {{ animation-name: phaseB; }}
      @keyframes phaseA {{
        0%,49% {{ opacity:1; }}
        50%,100% {{ opacity:0; }}
      }}
      @keyframes phaseB {{
        0%,49% {{ opacity:0; }}
        50%,100% {{ opacity:1; }}
      }}
      .tipbox {{
        max-width:480px;
        margin: 2px auto 8px auto;
        padding: 10px 12px;
        border-radius: 12px;
        background: #eef4ff;
        font-size: 14px;
        line-height: 1.35;
        text-align:center;
        white-space:normal;
        overflow-wrap:anywhere;
      }}
    </style>
    <div class="anim-wrap">
      <div class="anim-frame frame-a">{f1}</div>
      <div class="anim-frame frame-b">{f2}</div>
    </div>
    <div class="tipbox"><b>Technik:</b> {tip}</div>
    """
    st.components.v1.html(html, height=235)

def workout_runner():
    phase = st.session_state.phase
    exercises = st.session_state.exercise_list
    n_ex = max(1, len(exercises))

    if phase not in ["stretch", "done"]:
        overall_index = ((st.session_state.round - 1) * n_ex + st.session_state.exercise_index)
        total_steps = max(1, st.session_state.rounds_total * n_ex)
        st.progress(min(1.0, overall_index / total_steps))

    if phase == "exercise":
        ex = exercises[st.session_state.exercise_index]
        ex_no = st.session_state.exercise_index + 1
        c1, c2 = st.columns(2)
        c1.metric("Runde", f"{st.session_state.round}/{st.session_state.rounds_total}")
        c2.metric("Übung", f"{ex_no}/{n_ex}")
        st.markdown(f"""
        <div style="padding:16px 14px;border-radius:16px;background:#18212f;color:#fff;text-align:center;margin-bottom:8px;border:1px solid rgba(255,255,255,.12);">
          <div style="font-size:28px;font-weight:800;line-height:1.15;">{ex['name']}</div>
          <div style="font-size:20px;font-weight:700;margin-top:8px;color:#dbeafe;">{ex['amount']}</div>
          <div style="font-size:15px;margin-top:10px;color:#e5e7eb;line-height:1.35;white-space:normal;overflow-wrap:anywhere;">{ex['cue']}</div>
        </div>
        """, unsafe_allow_html=True)
        exercise_animation(ex["name"])
        show_exercise_image(ex["name"])
        if ex["type"] == "timed":
            if st.session_state.timer_end is None:
                if st.button("▶ TIMER STARTEN", use_container_width=True, type="primary"):
                    start_timed_exercise(ex["seconds"]); st.rerun()
            else:
                remaining = max(0, int(st.session_state.timer_end - time.time()))
                render_timer(remaining, ex["name"])
                if st.button("✅ FERTIG → WEITER", use_container_width=True, type="primary"):
                    st.session_state.timer_end = None; next_exercise(); st.rerun()
        else:
            if st.button("✅ FERTIG → WEITER", use_container_width=True, type="primary"):
                next_exercise(); st.rerun()

    elif phase == "rest":
        remaining = max(0, int(st.session_state.timer_end - time.time()))
        st.markdown("## ⏱ Kurze Pause")
        st.caption("20 Sekunden – ruhig atmen, Position wechseln.")
        render_timer(remaining, "Pause")
        if st.button("⏭ NÄCHSTE ÜBUNG", use_container_width=True, type="primary"):
            st.session_state.phase = "exercise"; st.session_state.timer_end = None; st.rerun()

    elif phase == "round_rest":
        remaining = max(0, int(st.session_state.timer_end - time.time()))
        finished_round = st.session_state.round - 1
        st.success(f"Runde {finished_round} geschafft ✓")
        st.markdown(f"### Gleich startet Runde {st.session_state.round} von {st.session_state.rounds_total}")
        render_timer(remaining, "75 Sek. Rundenpause")
        if st.button(f"▶ RUNDE {st.session_state.round} STARTEN", use_container_width=True, type="primary"):
            st.session_state.phase = "exercise"; st.session_state.timer_end = None; st.rerun()

    elif phase == "stretch":
        idx = st.session_state.stretch_index
        if idx >= len(STRETCH):
            st.session_state.phase = "done"; st.rerun()
        s = STRETCH[idx]
        st.progress((idx + 1) / len(STRETCH))
        st.caption(f"Dehnung {idx+1} von {len(STRETCH)}")
        st.markdown(f"""
        <div style="padding:16px;border-radius:16px;background:#18212f;color:#fff;text-align:center;margin-bottom:10px;">
          <div style="font-size:26px;font-weight:800;">{s['name']}</div>
          <div style="font-size:20px;margin-top:8px;color:#dbeafe;">{s['seconds']} Sekunden</div>
          <div style="font-size:15px;margin-top:10px;color:#e5e7eb;white-space:normal;overflow-wrap:anywhere;">{s['cue']}</div>
        </div>
        """, unsafe_allow_html=True)
        render_timer(s["seconds"], s["name"])
        if st.button("✅ NÄCHSTE DEHNUNG", use_container_width=True, type="primary"):
            st.session_state.stretch_index += 1; st.rerun()

    elif phase == "done":
        st.balloons(); st.success("🎉 Training und Stretching geschafft!")
        st.markdown("**Heute zählt:** sauber trainiert, Kraftreiz gesetzt, fertig.")
        if st.button("Training beenden", use_container_width=True, type="primary"):
            reset_workout(); st.rerun()

    if phase not in ["done", "idle"]:
        st.divider()
        if st.button("⛔ Training abbrechen", use_container_width=True):
            reset_workout(); st.rerun()

# -------------------------------------------------
# App
# -------------------------------------------------
st.title("💪 Fit bis 90 kg")

today_name = GERMAN_DAYS[date.today().weekday()]
icon, typ, summary = WEEK_PLAN[today_name]

# Tages-Checkliste direkt ganz oben unter dem App-Titel.
render_daily_dashboard(today_name)

st.caption("Training ohne Geräte · Wochenplan · Gewicht · Ernährung")
st.markdown(f"### Heute: {today_name}")
st.info(f"{icon} **{typ}**  \n{summary}")

tabs = st.tabs(["🏠 Heute", "▶️ Training", "📅 Woche", "🎯 Aufgaben", "⚖️ Gewicht", "🥗 Ernährung"])

with tabs[0]:
    # Wenn ein Training gestartet wurde, läuft es direkt auf der Startseite weiter.
    # Dadurch bleibt man nach dem Klick auf "Starten" im sichtbaren Trainingsablauf.
    if st.session_state.active_workout:
        st.markdown(f"### 🏋️ {st.session_state.active_workout}")
        workout_runner()
    else:
        st.markdown("### 🏋️ Training heute")

        if today_name == "Dienstag":
            st.write("🐕 4 km mit dem Hund → danach Kraft A → Stretching")
            if st.button(
                "▶️ HEUTIGES TRAINING STARTEN",
                use_container_width=True,
                type="primary",
                key="today_train_tuesday",
            ):
                begin_workout("Kraft A", WORKOUT_A, 3)
                st.rerun()

        elif today_name == "Donnerstag":
            st.write("🐕 4 km mit dem Hund → danach Rücken/Core → Stretching")
            if st.button(
                "▶️ HEUTIGES TRAINING STARTEN",
                use_container_width=True,
                type="primary",
                key="today_train_thursday",
            ):
                begin_workout("Rücken/Core", WORKOUT_CORE, 2)
                st.rerun()

        elif today_name == "Freitag":
            st.write("🐕 4 km mit dem Hund → danach Kraft B → Stretching")
            if st.button(
                "▶️ HEUTIGES TRAINING STARTEN",
                use_container_width=True,
                type="primary",
                key="today_train_friday",
            ):
                begin_workout("Kraft B", WORKOUT_B, 3)
                st.rerun()

        elif today_name in ["Mittwoch", "Samstag", "Sonntag"]:
            c1, c2, c3 = st.columns(3)
            c1.metric("Dauer", "45 min")
            c2.metric("Tempo", "4,4 km/h")
            c3.metric("Steigung", "10 %")
            st.write("🏃 Gleichmäßig laufen. Bei ungewöhnlicher Kreislaufreaktion oder Schmerzen Training abbrechen.")
        else:
            st.success("🟦 Heute ist Regenerationstag.")

with tabs[1]:
    # Auswahl eines Trainings. Nach dem Start springt die App automatisch
    # auf die Startseite, wo der komplette Ablauf inklusive Animationen erscheint.
    if st.session_state.active_workout:
        st.success(f"▶️ {st.session_state.active_workout} läuft gerade auf der Startseite „Heute“.")
        st.caption("Dort siehst du Übung, Animation, Wiederholungen, Timer und den Weiter-Button.")
    else:
        st.markdown("### Training auswählen")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Dienstag\nKraft A", use_container_width=True, key="select_workout_a"):
                begin_workout("Kraft A", WORKOUT_A, 3)
                st.rerun()
        with c2:
            if st.button("Donnerstag\nRücken/Core", use_container_width=True, key="select_workout_core"):
                begin_workout("Rücken/Core", WORKOUT_CORE, 2)
                st.rerun()
        with c3:
            if st.button("Freitag\nKraft B", use_container_width=True, key="select_workout_b"):
                begin_workout("Kraft B", WORKOUT_B, 3)
                st.rerun()

        st.caption("Nach dem Start erscheint das Training direkt auf der Seite „Heute“ – Übung für Übung mit Animation.")

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
        target_date = date.today() + pd.Timedelta(days=math.ceil(weeks * 7))
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
