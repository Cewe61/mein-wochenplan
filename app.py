
import streamlit as st
from datetime import date
import pandas as pd
import math
import time
import json
import calendar
from pathlib import Path

st.set_page_config(page_title="Fit bis 90 kg", page_icon="💪", layout="centered")

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
        font-size: 15px;
        line-height: 1.35;
        text-align:center;
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

    st.progress(
        min(
            1.0,
            ((st.session_state.round - 1) * len(st.session_state.exercise_list)
             + st.session_state.exercise_index + 1)
            / (st.session_state.rounds_total * len(st.session_state.exercise_list))
        )
        if phase not in ["stretch", "done"] else 1.0
    )

    if phase == "exercise":
        ex = st.session_state.exercise_list[st.session_state.exercise_index]
        st.markdown(
            f"""
            <div style="padding:22px;border-radius:16px;background:#f2f4f7;text-align:center;">
              <div style="font-size:18px;">Runde {st.session_state.round} von {st.session_state.rounds_total}</div>
              <div style="font-size:34px;font-weight:800;margin-top:8px;">{ex['name']}</div>
              <div style="font-size:24px;margin-top:8px;">{ex['amount']}</div>
              <div style="font-size:17px;margin-top:12px;">{ex['cue']}</div>
            </div>
            """, unsafe_allow_html=True
        )

        exercise_animation(ex["name"])

        if ex["type"] == "timed":
            if st.session_state.timer_end is None:
                if st.button("▶️ TIMER STARTEN", use_container_width=True, type="primary"):
                    start_timed_exercise(ex["seconds"])
                    st.rerun()
            else:
                remaining = max(0, int(st.session_state.timer_end - time.time()))
                render_timer(remaining, ex["name"])
                if st.button("✅ FERTIG → WEITER", use_container_width=True, type="primary"):
                    st.session_state.timer_end = None
                    next_exercise()
                    st.rerun()
        else:
            if st.button("✅ FERTIG → WEITER", use_container_width=True, type="primary"):
                next_exercise()
                st.rerun()

    elif phase == "rest":
        remaining = max(0, int(st.session_state.timer_end - time.time()))
        st.markdown("## ⏱️ 20 Sekunden Pause")
        render_timer(remaining, "Kurze Pause")
        if st.button("Weiter zur nächsten Übung", use_container_width=True, type="primary"):
            st.session_state.phase = "exercise"
            st.session_state.timer_end = None
            st.rerun()

    elif phase == "round_rest":
        remaining = max(0, int(st.session_state.timer_end - time.time()))
        st.markdown(f"## Runde {st.session_state.round - 1} geschafft ✓")
        render_timer(remaining, "Pause zwischen den Zirkeln")
        if st.button(f"Runde {st.session_state.round} starten", use_container_width=True, type="primary"):
            st.session_state.phase = "exercise"
            st.session_state.timer_end = None
            st.rerun()

    elif phase == "stretch":
        idx = st.session_state.stretch_index
        if idx >= len(STRETCH):
            st.session_state.phase = "done"
            st.rerun()

        s = STRETCH[idx]
        st.markdown("## 🧘 Stretching")
        st.markdown(
            f"""
            <div style="padding:22px;border-radius:16px;background:#f2f4f7;text-align:center;">
              <div style="font-size:32px;font-weight:800;">{s['name']}</div>
              <div style="font-size:24px;margin-top:8px;">{s['seconds']} Sekunden</div>
              <div style="font-size:17px;margin-top:10px;">{s['cue']}</div>
            </div>
            """, unsafe_allow_html=True
        )
        render_timer(s["seconds"], s["name"])
        if st.button("✅ NÄCHSTE DEHNUNG", use_container_width=True, type="primary"):
            st.session_state.stretch_index += 1
            st.rerun()

    elif phase == "done":
        st.balloons()
        st.success("🎉 Training und Stretching geschafft!")
        st.markdown("**Ziel:** Kraft möglichst erhalten, während das Gewicht sinkt.")
        if st.button("Training beenden", use_container_width=True):
            reset_workout()
            st.rerun()

    if phase not in ["done", "idle"]:
        st.divider()
        if st.button("⛔ Training abbrechen", use_container_width=True):
            reset_workout()
            st.rerun()



# -------------------------------------------------
# Monatsziele, Teilziele, Wochenaufgaben & Tagesblöcke
# -------------------------------------------------
TASK_FILE = Path("monatsziele.json")

DEFAULT_PROJECTS = [
    {
        "name": "Liskara Werbung",
        "sessions_per_week": 2,
        "session_minutes": 60,
        "preferred_days": ["Montag", "Donnerstag"],
    },
    {
        "name": "Klimaforum Werbung",
        "sessions_per_week": 4,
        "session_minutes": 60,
        "preferred_days": ["Montag", "Dienstag", "Donnerstag", "Freitag"],
    },
]

DEFAULT_MONTH_PLAN = {
    "month": date.today().strftime("%Y-%m"),
    "monthly_goal": "",
    "projects": DEFAULT_PROJECTS,
    "subgoals": [],
    "weekly_tasks": [],
    "completed": {}
}

def load_goals():
    if TASK_FILE.exists():
        try:
            data = json.loads(TASK_FILE.read_text(encoding="utf-8"))
            for k, v in DEFAULT_MONTH_PLAN.items():
                if k not in data:
                    data[k] = v
            return data
        except Exception:
            pass
    return DEFAULT_MONTH_PLAN.copy()

def save_goals(data):
    try:
        TASK_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False

def current_week_key():
    y, w, _ = date.today().isocalendar()
    return f"{y}-W{w:02d}"

def realistic_day_capacity():
    # Minuten zusätzlich zu Praxis + Bewegung; bewusst konservativ
    return {
        "Montag": 120,
        "Dienstag": 60,
        "Mittwoch": 45,
        "Donnerstag": 60,
        "Freitag": 60,
        "Samstag": 45,
        "Sonntag": 45,
    }

def distribute_week(projects, weekly_tasks=None):
    weekly_tasks = weekly_tasks or []
    capacities = realistic_day_capacity()
    used = {d: 0 for d in capacities}
    plan = {d: [] for d in capacities}

    # Wiederkehrende Projektblöcke zuerst
    for p in projects:
        sessions = int(p.get("sessions_per_week", 1))
        mins = int(p.get("session_minutes", 60))
        preferred = p.get("preferred_days", list(capacities.keys())) or list(capacities.keys())

        for _ in range(sessions):
            candidates = sorted(
                preferred,
                key=lambda d: (used[d] / max(capacities[d], 1), used[d])
            )
            chosen = candidates[0]
            plan[chosen].append({
                "kind": "Routine",
                "project": p["name"],
                "task": p["name"],
                "minutes": mins,
            })
            used[chosen] += mins

    # Konkrete Wochenaufgaben danach
    for task in weekly_tasks:
        mins = int(task.get("minutes", 30))
        preferred = task.get("preferred_days", list(capacities.keys())) or list(capacities.keys())
        candidates = sorted(
            preferred,
            key=lambda d: (used[d] / max(capacities[d], 1), used[d])
        )
        chosen = candidates[0]
        plan[chosen].append({
            "kind": "Aufgabe",
            "project": task.get("project", ""),
            "task": task.get("task", "Aufgabe"),
            "minutes": mins,
        })
        used[chosen] += mins

    return plan

def build_weekly_tasks_from_subgoals(subgoals):
    """Zerlegt Teilziele in kleine, realistische 30–60-Minuten-Blöcke."""
    tasks = []
    for sg in subgoals:
        title = sg.get("title", "").strip()
        project = sg.get("project", "").strip()
        total_minutes = int(sg.get("minutes_total", 60))
        preferred_days = sg.get("preferred_days", list(GERMAN_DAYS.values()))

        if not title:
            continue

        remaining = total_minutes
        n = 1
        while remaining > 0:
            block = 60 if remaining >= 60 else (45 if remaining >= 45 else 30)
            tasks.append({
                "project": project,
                "task": f"{title}" if total_minutes <= 60 else f"{title} – Teil {n}",
                "minutes": block,
                "preferred_days": preferred_days,
            })
            remaining -= block
            n += 1
    return tasks

def monthly_progress_box():
    goals = load_goals()
    month_label = datetime.now().strftime("%B %Y")
    week_key = current_week_key()

    st.subheader(f"🎯 Monatsplanung – {month_label}")
    st.caption("Einmal im Monat Ziele festlegen. Daraus entstehen kleine Wochen- und Tagesaufgaben.")

    goal_text = st.text_area(
        "Monatsziel",
        value=goals.get("monthly_goal", ""),
        placeholder="z. B. Klimaforum-Kampagne vorbereiten, Liskara-Werbung verbessern, weitere Projekte abschließen"
    )

    st.markdown("### 1. Feste Wochenblöcke")
    projects = []
    existing_projects = goals.get("projects", DEFAULT_PROJECTS)

    for i, default in enumerate(existing_projects):
        with st.expander(default.get("name", f"Projekt {i+1}"), expanded=True):
            name = st.text_input("Projekt", value=default.get("name", ""), key=f"proj_name_{i}")
            sessions = st.number_input(
                "Einheiten pro Woche",
                min_value=1, max_value=7,
                value=int(default.get("sessions_per_week", 1)),
                key=f"proj_sessions_{i}"
            )
            mins_options = [30, 45, 60, 90, 120]
            default_mins = int(default.get("session_minutes", 60))
            idx = mins_options.index(default_mins) if default_mins in mins_options else 2
            mins = st.selectbox(
                "Dauer je Einheit",
                mins_options,
                index=idx,
                key=f"proj_mins_{i}"
            )
            pref = st.multiselect(
                "Geeignete Tage",
                list(GERMAN_DAYS.values()),
                default=default.get("preferred_days", ["Montag"]),
                key=f"proj_days_{i}"
            )
            projects.append({
                "name": name,
                "sessions_per_week": int(sessions),
                "session_minutes": int(mins),
                "preferred_days": pref or list(GERMAN_DAYS.values()),
            })

    st.markdown("### 2. Teilziele des Monats")
    st.caption("Beispiel: „3 neue Anzeigenmotive“, „Landingpage prüfen“, „Newsletter vorbereiten“.")

    existing_subgoals = goals.get("subgoals", [])
    subgoal_count = st.number_input(
        "Anzahl Teilziele",
        min_value=0, max_value=12,
        value=max(3, len(existing_subgoals)) if existing_subgoals else 3,
        step=1
    )

    subgoals = []
    for i in range(int(subgoal_count)):
        old = existing_subgoals[i] if i < len(existing_subgoals) else {}
        with st.expander(f"Teilziel {i+1}", expanded=(i < 3)):
            project = st.text_input(
                "Projekt / Bereich",
                value=old.get("project", ""),
                placeholder="z. B. Klimaforum",
                key=f"sg_proj_{i}"
            )
            title = st.text_input(
                "Konkretes Ergebnis",
                value=old.get("title", ""),
                placeholder="z. B. drei Anzeigenmotive fertigstellen",
                key=f"sg_title_{i}"
            )
            minutes_total = st.selectbox(
                "Geschätzter Gesamtaufwand",
                [30, 45, 60, 90, 120, 180, 240],
                index=[30,45,60,90,120,180,240].index(old.get("minutes_total", 60))
                if old.get("minutes_total", 60) in [30,45,60,90,120,180,240] else 2,
                key=f"sg_minutes_{i}"
            )
            preferred = st.multiselect(
                "Geeignete Tage",
                list(GERMAN_DAYS.values()),
                default=old.get("preferred_days", ["Montag", "Donnerstag"]),
                key=f"sg_days_{i}"
            )
            if title.strip():
                subgoals.append({
                    "project": project,
                    "title": title,
                    "minutes_total": int(minutes_total),
                    "preferred_days": preferred or list(GERMAN_DAYS.values())
                })

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧩 Teilziele in Wochenaufgaben zerlegen", use_container_width=True):
            generated = build_weekly_tasks_from_subgoals(subgoals)
            goals["weekly_tasks"] = generated
            goals["subgoals"] = subgoals
            goals["monthly_goal"] = goal_text
            goals["projects"] = projects
            save_goals(goals)
            st.success(f"{len(generated)} konkrete Arbeitsblöcke erstellt.")
            st.rerun()

    with c2:
        if st.button("💾 Monatsplan speichern", use_container_width=True, type="primary"):
            goals["month"] = date.today().strftime("%Y-%m")
            goals["monthly_goal"] = goal_text
            goals["projects"] = projects
            goals["subgoals"] = subgoals
            if save_goals(goals):
                st.success("Monatsplan gespeichert.")
            else:
                st.warning("Plan konnte auf diesem Hosting nicht dauerhaft gespeichert werden.")

    # Aktuelle Wochenaufgaben
    goals = load_goals()
    weekly_tasks = goals.get("weekly_tasks", [])

    st.markdown("### 3. Diese Woche")
    if not weekly_tasks:
        st.info("Noch keine konkreten Wochenaufgaben erzeugt. Oben Teilziele eintragen und zerlegen.")
    else:
        st.caption("Diese Blöcke werden zusätzlich zu den festen Liskara-/Klimaforum-Stunden verteilt.")

    plan = distribute_week(goals.get("projects", projects), weekly_tasks)
    completed = goals.get("completed", {})
    week_done = completed.get(week_key, {})

    for day in GERMAN_DAYS.values():
        with st.expander(f"{day}", expanded=(day == GERMAN_DAYS[date.today().weekday()])):
            st.write(f"**Bewegung:** {WEEK_PLAN[day][2]}")

            items = plan[day]
            if not items:
                st.write("Keine zusätzliche Aufgabe.")
                continue

            for j, item in enumerate(items):
                task_id = f"{day}_{j}_{item['project']}_{item['task']}"
                default_done = bool(week_done.get(task_id, False))
                label = f"{item['task']} · {item['minutes']} Min."
                if item["project"] and item["project"] != item["task"]:
                    label = f"{item['project']}: {label}"

                done = st.checkbox(
                    label,
                    value=default_done,
                    key=f"done_{week_key}_{task_id}"
                )
                week_done[task_id] = done

    completed[week_key] = week_done
    goals["completed"] = completed
    save_goals(goals)

    # Fortschritt
    all_values = list(week_done.values())
    if all_values:
        done_count = sum(1 for x in all_values if x)
        total = len(all_values)
        st.progress(done_count / total)
        st.caption(f"Woche: {done_count} von {total} Blöcken erledigt.")

    st.markdown("### 4. Monats-Review")
    st.write("Am Monatsanfang oder Monatsende können Sie mir einfach Ihre neuen Ziele nennen. Ich kann daraus passende Teilziele und realistische Zeitblöcke formulieren, die Sie hier übernehmen.")

# -------------------------------------------------
# App
# -------------------------------------------------
st.title("💪 Fit bis 90 kg")
st.caption("Training ohne Geräte · Wochenplan · Gewicht · Ernährung")

today_name = GERMAN_DAYS[date.today().weekday()]
icon, typ, summary = WEEK_PLAN[today_name]

st.markdown(f"### Heute: {today_name}")
st.info(f"{icon} **{typ}**  \n{summary}")

tabs = st.tabs(["🏠 Heute", "▶️ Training", "📅 Woche", "🎯 Aufgaben", "⚖️ Gewicht", "🥗 Ernährung"])

with tabs[0]:
    if today_name == "Dienstag":
        st.write("🐕 4 km mit dem Hund → danach Kraft A → Stretching")
        if st.button("▶️ HEUTIGES TRAINING STARTEN", use_container_width=True, type="primary"):
            begin_workout("Kraft A", WORKOUT_A, 3)
            st.rerun()
    elif today_name == "Donnerstag":
        st.write("🐕 4 km mit dem Hund → danach Rücken/Core → Stretching")
        if st.button("▶️ HEUTIGES TRAINING STARTEN", use_container_width=True, type="primary"):
            begin_workout("Rücken/Core", WORKOUT_CORE, 2)
            st.rerun()
    elif today_name == "Freitag":
        st.write("🐕 4 km mit dem Hund → danach Kraft B → Stretching")
        if st.button("▶️ HEUTIGES TRAINING STARTEN", use_container_width=True, type="primary"):
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

    st.divider()
    st.markdown("#### Tagesstruktur Ernährung")
    st.write("**Bis 16:00:** Fasten / kalorienfreie Getränke")
    st.write("**16:00:** ca. 300 g Hähnchen + Gurke/Gemüse + 1 EL Olivenöl")
    st.write("**19:30–20:00:** ca. 300 g Garnelen + Gemüse + 2 Eier bzw. andere Proteinquelle")

with tabs[1]:
    if st.session_state.active_workout:
        st.markdown(f"### {st.session_state.active_workout}")
        workout_runner()
    else:
        st.markdown("### Training auswählen")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Dienstag\nKraft A", use_container_width=True):
                begin_workout("Kraft A", WORKOUT_A, 3)
                st.rerun()
        with c2:
            if st.button("Donnerstag\nRücken/Core", use_container_width=True):
                begin_workout("Rücken/Core", WORKOUT_CORE, 2)
                st.rerun()
        with c3:
            if st.button("Freitag\nKraft B", use_container_width=True):
                begin_workout("Kraft B", WORKOUT_B, 3)
                st.rerun()

        st.caption("Die App führt anschließend Übung für Übung durch den Zirkel und danach durch das Stretching.")

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
