# Baut data.js für die Brand-Weg-App aus einem Cockpit-Export.
# Aufruf: python -I tools/build_data.py <cockpit-export.json>
# Der Export ist {settings, items:[...]} aus IndexedDB oder „Sicherung herunterladen“.
# Persönliche Antworten kommen NICHT in data.js (das Repo ist öffentlich), nur Inhalte aus den Quellen.
import json, re, sys, pathlib

src = json.load(open(sys.argv[1], encoding="utf-8"))
IT = {i["id"]: i for i in src["items"]}
OUT = pathlib.Path(__file__).resolve().parent.parent / "data.js"


def clean(t):
    t = re.split(r"\n## (Deine Antwort|Weitere Antworten)", t)[0]
    t = re.sub(r"(\d\.?)\s?–\s?(\d)", r"\1 bis \2", t)
    t = t.replace(" – ", ", ").replace(" — ", ", ")
    t = t.replace("Brand-Profil", "„Brand“").replace("im „Brand“", "unter „Brand“")
    t = t.replace("Content-Werkzeugkasten", "Video-Werkstatt")
    t = t.replace("Gewohnheit „Video gepostet“ abhaken", "In der Werkstatt auf „Gepostet“ stellen")
    return t.strip()


def task(tid):
    return clean(IT[tid]["body"])


# ---------- Felder: alles, was du einträgst ----------
# sec = Abschnitt unter „Brand“. Die Profil-Felder kommen aus der Vorlage im Cockpit (brandtpl-main).
TPL = IT["brandtpl-main"]["tpl"]
SECTIONS, FIELDS = [], {}
for s in TPL["sections"]:
    SECTIONS.append({"id": s["id"], "title": s["title"], "why": clean(s.get("why", ""))})
    for f in s["fields"]:
        FIELDS[f["id"]] = {"label": f["label"], "hint": clean(f.get("hint", "")), "rows": f.get("rows", 2), "sec": s["id"]}

# Ergänzungen aus Fahrplan und Leitfaden
FIELDS["helfen"] = {"label": "Wie ich mit meinem Content Menschen helfe", "hint": "Ein Satz. Dein Anker an Tagen ohne Aufrufe (Mino, Kurs-Tag 4).", "rows": 2, "sec": "weg"}
FIELDS["einwaende"] = {"label": "Ihre typischen Einwände und meine Antwort", "hint": "Zum Beispiel „keine Zeit“, „kenne ich schon“. Die kommen später direkt ins Skript (Mino).", "rows": 3, "sec": "fuerwen"}
FIELDS["keywords"] = {"label": "Meine Keyword-Bank", "hint": "Wörter, die deine Zuschauer selbst benutzen. Mit Google Trends prüfen, welches mehr Menschen interessiert (Mino).", "rows": 3, "sec": "hooks"}
FIELDS["versprechen"] = {"label": "Mein eines Versprechen", "hint": "Wobei hilfst du, in einem Satz? Eins, nicht zehn (Sam Gaudet, die vier P).", "rows": 2, "sec": "themen"}
FIELDS["proofstack"] = {"label": "Woran ich gerade öffentlich arbeite (Proof Stacking)", "hint": "Ein laufendes Ziel, das du offen zeigst und mit jedem Ergebnis weiter belegst. Sam baut gerade öffentlich einen Account nur mit dem iPhone auf 100.000 Follower.", "rows": 2, "sec": "experte"}
SECTIONS.insert(1, {"id": "dran", "title": "Dranbleiben", "why": "Die meisten scheitern nicht am Wissen, sondern daran, dass sie aufhören (Leitfaden Kapitel 1)."})
FIELDS["zahlziel"] = {"label": "Mein Zahlenziel für 6 Monate", "hint": "Eins, nicht zwei (Mino). Zum Beispiel 100.000 Follower oder 10.000 $ im Monat. Sichtbar aufschreiben, etwa als Hintergrundbild.", "rows": 2, "sec": "dran"}
FIELDS["huerden"] = {"label": "Meine Hürden und wie ich sie umdeute", "hint": "Pro Hürde: die schlimmste realistische Folge und warum sich das Posten trotzdem lohnt.", "rows": 4, "sec": "dran"}
FIELDS["partner"] = {"label": "Wer mich zur Rechenschaft zieht", "hint": "Mino zahlt jedem Freund 30 $, wenn er einen Tag nicht postet. Und: 1 bis 2 Leute, die Content ernst nehmen.", "rows": 2, "sec": "dran"}

# Antworten aus den Kurs-Tagen (Abschnitt „Aus den Kurs-Tagen“)
SECTIONS.append({"id": "kurs", "title": "Antworten aus den Kurs-Tagen", "why": "Die Fragen aus Minos 7-Tage-Kurs. Aus ihnen baut die App deine Skripte."})
K = {
    "k1_angst": ("Kurs-Tag 1: Meine größte Angst beim Posten", "Wird im Skript zu: „Ehrlich gesagt habe ich Angst davor, …“", 2),
    "k1_botschaft": ("Kurs-Tag 1: Was ich jemandem mit derselben Angst sage", "Ein bis zwei Sätze, direkt an diese Person.", 2),
    "k2_momente": ("Kurs-Tag 2: Die 3 Momente der letzten 7 Tage mit dem stärksten Gefühl", "Freude, Ekel, Angst, Wut oder Traurigkeit. Je 1 Satz, banal ist okay.", 3),
    "k2_ereignis": ("Kurs-Tag 2: Der stärkste Moment fürs Skript", "„Letzte Woche …“", 2),
    "k2_besonders": ("Kurs-Tag 2: Was den Moment besonders machte", "2 Sätze.", 2),
    "k2_gefuehl": ("Kurs-Tag 2: Das Gefühl", "1 bis 2 Wörter.", 1),
    "k2_lektion": ("Kurs-Tag 2: Was mir dabei klar wurde", "Welche Lektion, welche Überzeugung hat sich geändert? 2 Sätze.", 2),
    "k3_passiert": ("Kurs-Tag 3: Was im letzten Jahr passiert ist", "5 konkrete Dinge, über die dein jüngeres Ich begeistert wäre.", 4),
    "k3_noetig": ("Kurs-Tag 3: Was dafür nötig war", "Spezifisch, nicht „hart arbeiten“.", 3),
    "k3_zweifel": ("Kurs-Tag 3: Der Zweifel deines jüngeren Ichs", "In seinen Worten.", 2),
    "k3_antwort": ("Kurs-Tag 3: Deine Antwort darauf", "Mit konkreten Zahlen, 3 bis 4 Sätze.", 3),
    "k3_botschaft": ("Kurs-Tag 3: Die Botschaft, die du damals gebraucht hättest", "Kurz.", 2),
    "k4_geschichte": ("Kurs-Tag 4: Eine persönliche Geschichte zu deinem Ziel", "4 bis 5 Sätze.", 4),
    "k4_jetzt": ("Kurs-Tag 4: Warum dieses Ziel, warum jetzt?", "5 bis 6 Sätze.", 4),
    "k5_passiert": ("Kurs-Tag 5: Was ist heute passiert?", "", 2),
    "k5_gelernt": ("Kurs-Tag 5: Was habe ich gelernt oder gemerkt?", "Das wird dein Hook: 1 bis 2 Sätze, als überraschende Aussage an eine Person.", 2),
    "k6_ideen": ("Kurs-Tag 6: 10 Ideen in 10 Minuten", "Erst 4 Minuten Begriffe zu deiner Nische sammeln, dann Ideen daraus. Eine pro Zeile.", 6),
    "k7_rueckblick": ("Kurs-Tag 7: Was war am leichtesten, was lief am besten?", "Welcher Video-Typ hat sich am leichtesten angefühlt, welcher hatte die meisten Aufrufe?", 3),
}
for k, (l, h, r) in K.items():
    FIELDS[k] = {"label": l, "hint": h, "rows": r, "sec": "kurs"}
# Hinweise für die Skript-Bausteine
FIELDS["lage"]["hint"] = "Ein Satz: dein Alter und was du gerade startest. Ziel, Lage und Problem ordnen dich für Fremde in 3 bis 5 Sekunden ein (Mino)."
FIELDS["warum"]["hint"] = "Wird im Skript zu: „Ich starte diese Challenge, weil …“. Dein Anker für Tage ohne Aufrufe."

# ---------- Video-Arten mit Skript-Vorlage ----------
TYPES = {
    "freund": {"label": "Freund-Video", "src": "Mino", "tip": "Ziel, Lebenslage und Problem erzählen. Du gibst Wert als Freund, nicht als Experte.",
               "tpl": "Hook:\n\nMein Ziel:\n\nMeine Lage:\n\nMein Problem gerade:\n\nWas ich heute gemerkt habe:"},
    "lern": {"label": "Lernvideo", "src": "Mino, Educational", "tip": "Der Zuschauer lernt etwas. Erklärung ist 60 bis 70 % des Videos.",
             "tpl": "Hook (klares Ergebnis):\n\nLösung in einem Satz:\n\nEinwand („Jetzt denkst du wahrscheinlich …“):\n\nErklärung mit Warum und Beispiel:\n\nZurück zum Hook:"},
    "geschichte": {"label": "Geschichte (5 Stufen)", "src": "Mino, how i script videos", "tip": "60 bis 90 Sekunden. Kurze Sätze, höchstens 12 Wörter.",
                   "tpl": "1 Hook mit bekanntem Schmerz (max. 15 Wörter):\n\n2 Vorgeschichte mit Ort, Alter, Zahl (2 bis 4 Sätze):\n\n3 Wendepunkt, ein einziger Moment (1 bis 2 Sätze):\n\n4 Erkenntnis mit echtem Ergebnis (2 bis 3 Sätze):\n\n5 Lockerer Aufruf (optional):"},
    "meinung": {"label": "Meinung (BEST)", "src": "Ronny Mitchell", "tip": "Starke Aussage, Begründung, Geschichte, was der Zuschauer tun soll.",
                "tpl": "Bait, starke Aussage:\n\nElaborate, warum:\n\nStory, wo ich das gelernt habe:\n\nTakeaway, was du jetzt tun sollst:"},
    "frueher": {"label": "Botschaft an dein früheres Ich", "src": "Mino", "tip": "Fast alle viralen Videos von Mino sind Botschaften an sein jüngeres Ich.",
                "tpl": "Im letzten Jahr habe ich …\n\nUnd mir wurde klar, ich musste nur …\n\nJetzt denkst du wahrscheinlich: …\n\nAber …\n\nAlso …"},
    "heit": {"label": "Hook, Explain, Illustrate, Teach", "src": "Sam Gaudet", "tip": "Sams Aufbau für Kurzvideos. Als Gliederung schreiben und frei sprechen, nicht Wort für Wort ablesen.",
             "tpl": "Hook (Kontext, Gegenposition, offene Schleife):\n\nExplain, worum es geht und warum es für dich zählt:\n\nIllustrate, Geschichte, Vergleich oder Beispiel:\n\nTeach, eine Sache zum Mitnehmen:"},
    "youtube": {"label": "YouTube-Video (Sams Vorlage)", "src": "Sam Gaudet, YouTube-Skript-Vorlage", "tip": "Langes Video: Recherche, Titel, Thumbnail, Hook mit Versprechen, Beweis, Plan, dann Punkt für Punkt.",
             "tpl": ""},
    "vlog": {"label": "Ohne Skript (Vlog)", "src": "Mino, Minimum Viable Vlog", "tip": "Für volle Tage: zwei Fragen beantworten und frei erzählen.",
             "tpl": "Hook, meine Lektion in 1 bis 2 Sätzen:\n\nWas heute passiert ist (frei erzählen):\n\nPraktischer Tipp und positives Ende:"},
}

# ---------- Der Weg ----------
PHASES = [
    {"id": "p1", "title": "Anfangen: Minos 7-Tage-Kurs", "short": "Anfangen",
     "goal": "Jeden Kurs-Tag ein Video. Ein Kurs-Tag ist kein Kalendertag: Du machst den nächsten, wenn du so weit bist.",
     "src": "Mino Lee, Kurs & Workbook"},
    {"id": "p2", "title": "Rhythmus und Handwerk", "short": "Rhythmus",
     "goal": "Mindestens 3 Videos pro Woche, besser täglich. Ziel sind die ersten 30 Videos, konstant um 1.000 Aufrufe und ein Video mit 10.000.",
     "src": "Mino Lee, Fahrplan Phase 1"},
    {"id": "p3", "title": "Verdoppeln", "short": "Verdoppeln",
     "goal": "Das Format, das am besten lief, immer wieder machen. Erste bezahlte UGC-Aufträge.",
     "src": "Mino Lee, Fahrplan Phase 2"},
    {"id": "p4", "title": "Wachsen", "short": "Wachsen",
     "goal": "Erstes Video mit 100.000 Aufrufen und 10.000 Follower. Deinen eigenen Blickwinkel finden. Laut Mino melden sich hier die ersten Marken.",
     "src": "Mino Lee, Fahrplan Phase 3"},
    {"id": "p5", "title": "Geld verdienen", "short": "Geld",
     "goal": "Die ersten 1.000 $ aus UGC und Markendeals. Danach Richtung 10.000 € im Monat mit eigenem Angebot.",
     "src": "Mino Lee, Fahrplan Phase 4"},
    {"id": "p6", "title": "Später: Skalieren", "short": "Skalieren",
     "goal": "Wenn das Geld fließt, wird Zeit knapp. Systeme bauen, abgeben, Fähigkeiten stapeln.",
     "src": "Leitfaden Kapitel 11"},
]

S = []
def step(**kw):
    kw.setdefault("fields", []); kw.setdefault("refs", []); kw.setdefault("ch", [])
    S.append(kw)

step(id="s01", ph="p1", title="Kurs-Tag 1: Dein erstes Video",
     src="Mino, Kurs & Workbook Tag 1", refs=["muwc3ej574xmr4", "mv7nrb4z5wjppk"], ch=[1],
     why="Heute zählt nur, dass es online ist. Es darf schlecht sein. Plan etwa 60 bis 90 Minuten ein.",
     body="""**1. Vier Fragen beantworten (5 Min.)**
Unten eintragen. Daraus baut die App dein Skript.

**2. Skript laut lesen**
Auf „Skript in die Werkstatt“ tippen, dann einmal laut lesen und ändern, was sich nicht nach dir anhört.

**3. Filmen**
- CapCut öffnen, Kamera, Teleprompter an, Skript einfügen
- Hellstes Licht vor dir, Handy einfach irgendwo abstellen
- Vorher einatmen, 6 Sek. halten, 8 Sek. ausatmen
- Versprochen? Den Satz einfach neu sagen, das schneidest du später raus

**4. Schneiden**
- Alle Pausen am Anfang, am Ende und zwischen den Sätzen raus
- Automatische Untertitel, Tippfehler korrigieren, nie zwei Sätze in einer Zeile, auf etwa 30 % Höhe von unten schieben
- Clips auf 200 % Lautstärke
- Export 4K, 30 fps

**5. Posten**
- In der Instagram-App hochladen, nicht direkt aus CapCut
- Kurze Beschreibung, höchstens 1 Hashtag
- Nicht schlafen gehen, bevor das Video online ist (Mino)

**Dazu: Ziele auf Papier.** Ein Zahlenziel für 6 Monate, nicht zwei (Mino).""",
     fields=["lage", "warum", "k1_angst", "k1_botschaft", "zahlziel"], video="freund",
     tpl="Heute ist Tag 1 meiner 7-Tage-Challenge. Ich poste jeden Tag ein Video. Kurz zu mir: {lage} Ich starte diese Challenge, weil {warum}. Ehrlich gesagt habe ich Angst davor, {k1_angst}. Also: {k1_botschaft} Wir sehen uns morgen zu Tag 2.")

step(id="s02", ph="p1", title="Deine Hürden aufschreiben und umdeuten",
     src="Mino, If you're in college", refs=["muyyxm20972jcz"], ch=[1],
     why="Wer seine Bremsen kennt, hört nicht nach 2 bis 3 Tagen auf. Gehört zu Kurs-Tag 2.",
     body=task("mv6c2xlr64fdj0"), fields=["huerden"])

step(id="s03", ph="p1", title="Kurs-Tag 2: Nahbares Video über deine Woche",
     src="Mino, Kurs & Workbook Tag 2", refs=["muwc3ej574xmr4"], ch=[5],
     why="Kleine echte Momente machen dich nahbar. Realistisch: in den ersten 30 Tagen ein Video über 10.000 Aufrufe.",
     body="""Beantworte die Fragen unten, dann baut die App dein Skript.

**Umsetzung**
- Nie mit „Hey Leute“ anfangen.
- Mehrere Skripte schreiben, das stärkste filmen.
- 1 bis 2 Sätze pro Aufnahme.
- Erstes B-Roll als Overlay, Ton aus.""",
     fields=["k2_momente", "k2_ereignis", "k2_besonders", "k2_gefuehl", "k2_lektion"], video="freund",
     tpl="Letzte Woche {k2_ereignis}. {k2_besonders} Das war ehrlich gesagt so {k2_gefuehl}, weil mir klar wurde: {k2_lektion}")

step(id="s04", ph="p1", title="B-Roll sammeln und Schnitt-Vorlage in CapCut speichern",
     src="Mino, B-rollOS und ViralEditsOS", refs=["mv7nrb4y0h15k8", "mv7nrb4z5wjppk", "mv7nrb50ocqigf"], ch=[6, 7],
     why="Für Kurs-Tag 3 brauchst du 5 bis 10 kurze Clips. Und eine Vorlage, damit jeder Schnitt gleich aussieht.",
     body=task("mv6c2xltjqz9s2"), fields=["look"])

step(id="s05", ph="p1", title="Kurs-Tag 3: Botschaft an dein früheres Ich",
     src="Mino, Kurs & Workbook Tag 3", refs=["muwc3ej574xmr4"], ch=[5],
     why="Fast alle viralen Videos von Mino sind Botschaften an sein jüngeres Ich.",
     body="""Beantworte die Fragen unten, die App baut daraus dein Skript.

**Umsetzung**
- Mit einem Zungenbrecher aufwärmen. Die Kamera ist dein jüngeres Ich.
- B-Roll etwa alle 5 Sek. (die gesammelten Clips), Musik ohne Gesang.
- Nach dem Posten anderen Creators Feedback geben.""",
     fields=["k3_passiert", "k3_noetig", "k3_zweifel", "k3_antwort", "k3_botschaft"], video="frueher",
     tpl="Im letzten Jahr habe ich {k3_passiert}, und mir wurde klar, ich musste nur {k3_noetig}. Jetzt denkst du wahrscheinlich: {k3_zweifel} Aber {k3_antwort} Also … {k3_botschaft}")

step(id="s06", ph="p1", title="Deinen idealen Zuschauer festlegen",
     src="Mino, Ideal Viewer", refs=["mv1wdfbeaqfx71", "mv0iq93x9fbhht"], ch=[2],
     why="Eine echte Person, oft du selbst vor 2 bis 3 Jahren. Sie bestimmt deine Themen, Hooks und später dein Angebot. Passt zu Kurs-Tag 3.",
     body=task("mv6c2xls8pgeoc"), fields=["person", "schmerz", "wunsch", "signal", "einwaende", "markt"])

step(id="s07", ph="p1", title="Kurs-Tag 4: Road-to-Video über dein Ziel und Profil optimieren",
     src="Mino, Kurs & Workbook Tag 4", refs=["muwc3ej574xmr4", "mux1cwxu3il6dl"], ch=[2, 9],
     why="Ein klares Ziel, das man erreicht oder nicht erreicht, und die Reise dorthin dokumentieren. Beispiele: „Weg zu 100.000 $ im Monat“, „ersten Film in 30 Tagen schreiben“.",
     body="""Beantworte die Fragen unten, die App baut daraus dein Skript.

**Profil**
- Bio Zeile 1 Ort und Herkunft, Zeile 2 ein Satz über dich, Zeile 3 dein Ziel („Dokumentiere jeden Tag bis …“).
- Klares Porträt bis zu den Schultern, Benutzername ohne Zahlen.
- Business-E-Mail in die Bio, damit Marken dich finden.

**Schnitt-Trick:** in den ersten 3 bis 4 Sek. B-Roll-Schnitte unter 1 Sek.

**Hinweis:** Den „Tag X“-Hook nennt Mino in anderen Videos schwach. Als Rahmen in Bio und Serie ist er gut, später muss jeder Hook auch allein neugierig machen.""",
     fields=["helfen", "ziel", "k4_geschichte", "k4_jetzt", "bio", "mail"], video="freund",
     tpl="Heute ist Tag X auf dem Weg zu {ziel}. Warum? Nun … {k4_geschichte} {k4_jetzt} Folg mir, um die Reise mitzuerleben.")

step(id="s08", ph="p1", title="Kurs-Tag 5: Video ohne Skript",
     src="Mino, Kurs & Workbook Tag 5", refs=["muwc3ej574xmr4"], ch=[7],
     why="Für volle Tage: wenig Vorbereitung, wirkt natürlicher als Ablesen.",
     body=task("mv6cin74cyenlf").replace("**Zwei Fragen:** Was ist heute passiert? Was habe ich gelernt oder gemerkt?", "**Zwei Fragen:** unten beantworten."),
     fields=["k5_passiert", "k5_gelernt"], video="vlog",
     tpl="{k5_gelernt}\n\n(Frei erzählen: {k5_passiert} Oft „du“ und „wir“ sagen. Am Ende ein praktischer Tipp und ein positives Ende.)")

step(id="s09", ph="p1", title="Kurs-Tag 6: How-to-Video, Format und Nische festlegen",
     src="Mino, Kurs & Workbook Tag 6", refs=["muwc3ej574xmr4", "mv0iq93x9fbhht", "mv7nrb4we2wfql", "mv7nrb4x7edu9i"], ch=[2, 3],
     why="Das längste Video der Woche, etwa 90 bis 120 Minuten. Eine Nische, höchstens drei. Das Format ist noch wichtiger.",
     body=task("mv6cin75i5p28w"), fields=["nische", "format", "saeulen", "k6_ideen"], video="lern")

step(id="s10", ph="p1", title="Kurs-Tag 7: Rückblick auf die erste Woche",
     src="Mino, Kurs & Workbook Tag 7", refs=["muwc3ej574xmr4", "muyyxm20972jcz"], ch=[8],
     why="Hast du 6 Videos gepostet? Das allein ist der Erfolg dieser Woche.",
     body=task("mv6c2xlu73o27x"), fields=["k7_rueckblick"])

# Die Seite als Ganzes ist eine Zusammenstellung, kein Schritt aus den Quellen. Jeder Block nennt, woher seine Fragen stammen.
step(id="s10s", ph="p1", title="Deine Strategie auf einer Seite",
     src="Zusammenstellung, nicht aus den Quellen · Fragen von Mino und Sam Gaudet",
     refs=["muwc3ej574xmr4", "mv1wdfbeaqfx71", "mv0iq93x9fbhht", "muyyxm20972jcz", "muwzljdpz2t1bs", "mvsamgaudet02"], ch=[2],
     why="Alles, was du in der ersten Woche festgelegt hast, steht hier zusammen. So siehst du, ob es zusammenpasst, bevor der Rhythmus losgeht.",
     body="""**1. Einmal ganz durchlesen.** Wo noch etwas fehlt, steht der Schritt dabei, in dem du es einträgst.

**2. Mit deiner ersten Woche abgleichen.** Bei Kurs-Tag 7 hast du notiert, welcher Video-Typ am leichtesten ging und welcher am besten lief. Passt das zu deinem Format? Wenn nicht, stell das Format um (Mino, Kurs-Tag 6 und 7).

**3. Nachfrage prüfen.** Gibt es zu deiner Nische Videos mit vielen Aufrufen auf YouTube, TikTok und Instagram? (Mino, „become the niche“)

**4. Als Annahme behandeln.** Mino: mit einer Annahme starten, ausprobieren, offen bleiben. In Phase 3 verdoppelst du, was in deinen Zahlen läuft. In Phase 4 schärfst du Blickwinkel und Markenkern.

**Zur Kennzeichnung:** Dass alles auf einer Seite steht, ist eine Zusammenstellung und kommt nicht aus den Quellen. Woher jede Frage kommt, steht am jeweiligen Block.""",
     sheet=[
         {"t": "Für wen ich Videos mache", "src": "Mino, Ideal Viewer · Signal-Wörter: Sam Gaudet", "f": ["person", "schmerz", "wunsch", "einwaende", "signal"]},
         {"t": "Wer ich für sie bin", "src": "Mino, If you're in college (Ziel, Lage, Problem) · Kurs-Tag 4", "f": ["rolle", "ziel", "lage", "problem", "helfen"]},
         {"t": "Worüber ich rede", "src": "Mino, Kurs-Tag 6 und „become the niche“ · Versprechen: Sam Gaudet, die vier P", "f": ["nische", "versprechen", "saeulen"]},
         {"t": "Wie ich es zeige", "src": "Mino, Kurs-Tag 6 (Format) · Wiedererkennbarer Look", "f": ["format", "look"]},
         {"t": "Was die erste Woche gezeigt hat", "src": "Mino, Kurs-Tag 7", "f": ["k7_rueckblick"]},
     ])

step(id="s11", ph="p2", title="Hook-Bank und Keyword-Bank anlegen",
     src="Mino, how i create hooks", refs=["mux1cwxu3il6dl", "mv1wdfbfp4c6jh", "muxqsxactci59k"], ch=[4],
     why="Der Hook ist rund 80 % des Videos. Einen Hook selbst zu erfinden ist fast immer schlechter als eine bewährte Vorlage anzupassen.",
     body=task("mv6c2xlvxkz295"), fields=["hooks", "keywords"])

step(id="s12", ph="p2", title="Drei Skripte in 5 Stufen schreiben",
     src="Mino, how i script videos", refs=["mux0jynqqv7ogn"], ch=[5],
     why="Minos Schema für fast alle seine Videos mit über 1 Million Aufrufen.",
     body=task("mv6cin76r5m613"), video="geschichte")

step(id="s13", ph="p2", title="Stimme und Tempo üben",
     src="Mino, 400 views to 1M · Julian Treasure", refs=["muxqsxactci59k", "mv8jtreasure01"], ch=[6],
     why="Monotone Stimme und zu langsames Sprechen sind zwei von Minos 15 Fehlern.",
     body=task("mv6cin77zx9mcr"))

step(id="s14", ph="p2", title="Herausfinden, wie du wirklich redest",
     src="Ronny Mitchell, Markenkern", refs=["mv7szw0gj14n3r"], ch=[2],
     why="Sei vor der Kamera wie mit Freunden. Eine „Kamera-Stimme“ macht unsympathisch (Ronny).",
     body="""- Zwei Freunde fragen: Was ist typisch für mich, wie rede ich, worüber lache ich?
- Typische Sprüche, Humor und Eigenarten unten aufschreiben.
- Beim nächsten Skript einen davon einbauen.""",
     fields=["ton"])

step(id="s15", ph="p2", title="Leute finden, die dich dranhalten",
     src="Mino, how i grew 200K followers", refs=["muwzljdpz2t1bs"], ch=[1],
     why="Mino nennt das den wichtigsten Punkt. Ohne Umfeld bleibt Content ein Hobby, das einschläft.",
     body=task("mv6c2xlxcbbewk") + "\n\n**Posting-Wette:** Such dir eine Person, mit der du eine Wette abschließt. Mino zahlt jedem Freund 30 $, wenn er einen Tag nicht postet.",
     fields=["partner"])

step(id="s16", ph="p2", title="Ein Vorbild-Video Schnitt für Schnitt zerlegen",
     src="Mino, 400 views to 1M", refs=["muxqsxactci59k"], ch=[7],
     why="Minos Übung, bevor er bekannt wurde. Danach hatte er drei virale Videos hintereinander.",
     body=task("mv6cin78ys1xpw"))

step(id="s17", ph="p2", title="Retention prüfen: bestes und schwächstes Video",
     src="Mino, how i grew 200K followers", refs=["muwzljdpz2t1bs"], ch=[8],
     why="5 bis 10 % mehr Zuschauer nach den ersten 3 Sekunden können 10- bis 20-mal mehr Aufrufe bringen.",
     body=task("mv6c2xlwrj7spp"))

step(id="s18", ph="p2", title="1.000-Aufrufe-Check: deine Videos gegen die 15 Fehler",
     src="Mino, 400 views to 1M", refs=["muxqsxactci59k"], ch=[8],
     why="Wenn du nicht wächst, liegt es an deinen Videos, nicht an Algorithmus, Uhrzeit oder Hashtags (Mino).",
     body=task("mv6cin79g0fx3i"))

step(id="s19", ph="p2", title="Meilenstein: 30 Videos",
     src="Mino, If you're in college · Leitfaden Kapitel 8", refs=["muyyxm20972jcz", "muxqsxactci59k"], ch=[8], goal=30,
     why="Nach etwa 30 Videos hast du genug Daten (Mino). Die ersten 30 zählt Menge, danach Qualität und die Jagd nach Ausreißern.",
     body="""- Mindestens 3 Videos pro Woche durchgezogen?
- Ein Video mit 10.000 Aufrufen?
- Videos nach Aufrufen sortieren: Instagram im Profi-Dashboard unter „meistgesehen“ (Ronny), TikTok unter „Beliebt“ (Mino).
- Bestes und schlechtestes Video vergleichen: Idee, erste 3 Sekunden, Text im Bild, Kleidung, Ort, Ton.
- Welches Format lief am besten? Das machst du ab jetzt immer wieder.

Noch nicht bei 30? Kein Problem. Weiter posten, der Schritt wartet.""",
     fields=["laeuft", "naechstes"])

step(id="s20", ph="p3", title="Bestes Format verdoppeln: 10 Varianten skripten",
     src="Mino, If you're in college · 400 views to 1M", refs=["muyyxm20972jcz", "muxqsxactci59k", "mux1cwxu3il6dl"], ch=[8],
     why="Du wirst dich selbst schneller leid als dein Publikum.",
     body=task("mv6c2xm06on4mr"))

step(id="s21", ph="p3", title="UGC: Profile anlegen",
     src="Mino, how i made a fulltime income", refs=["muwdk6hmnlylop", "mv2urvoaxyc4cy", "mv5of447g0e3wq"], ch=[10],
     why="UGC ist der einfachste Einstieg, solange du kein eigenes Produkt hast. Dafür brauchst du weder Follower noch Expertenstatus (Mino).",
     body=task("mv6c2xlzlkfjcq") + """

Plattformen: SideShift, Launchpoint, Home From College. Ein Übungsaccount mit täglichen Posts ist dein Portfolio, denn Marken achten vor allem auf Regelmäßigkeit.

**Wichtig, das ist kein Tipp von Mino:** Bist du unter 18, verlangen viele UGC-Plattformen und Marken die Zustimmung der Eltern, manche nehmen dich gar nicht. Für Geld brauchst du außerdem ein Konto und eine Abrechnung. Lies die Regeln jeder Plattform und mach diesen Schritt zusammen mit deinen Eltern.""",
     fields=["ugc"])

step(id="s22", ph="p3", title="UGC: jede Woche 10 Bewerbungen mit Probevideo",
     src="Mino, how i made a fulltime income", refs=["muwdk6hmnlylop", "mv2urvoaxyc4cy"], ch=[10],
     why="Minos Rechnung: 30 UGC-Videos × 50 $ ergeben etwa 1.500 $ im Monat.",
     body=task("mv6c2xm1aw18fz"))

step(id="s23", ph="p3", title="Meilenstein: Format läuft, erste Aufträge",
     src="Mino, If you're in college", refs=["muyyxm20972jcz"], ch=[8, 10],
     why="Mino sagt klar: Phasen lassen sich nicht überspringen. 6 Monate in Phase 1 und 2 sind normal.",
     body="""- Wie oft hat das verdoppelte Format funktioniert?
- Wie viele UGC-Bewerbungen, wie viele Aufträge?
- Erstes Video mit 10.000 Aufrufen geschafft?""",
     fields=["laeuft"])

step(id="s24", ph="p4", title="Dein Blickwinkel: Skripte genau auf die Persona",
     src="Mino, how i grew 200K followers", refs=["muwzljdpz2t1bs", "mv0iq93x9fbhht", "muvnm80sxs4gcz"], ch=[2],
     why="Werde der Creator für ein bestimmtes Thema in deiner Nische. Mino spricht lieber von einem klaren Blickwinkel als von einem „einzigartigen Stil“.",
     body=task("mv6c2xm32ktods"), fields=["selten"])

step(id="s25", ph="p4", title="Markenkern: Woran du glaubst und wogegen du bist",
     src="Ronny Mitchell · Sam Gaudet", refs=["mv7szw0gj14n3r", "mv7tlfsamgaudt"], ch=[2, 9],
     why="Dogma und Gegenposition machen aus Followern Fans (Ronny). 3 bis 5 Gegenpositionen reichen (Sam).",
     body="""- **Dogma-Interview mit Claude:** Lebensgeschichte per Diktat erzählen, so früh du dich erinnerst. Dann Claude bitten, Rückfragen zu stellen, welche Überzeugungen daraus kommen. 3 bis 5 Sätze unten eintragen.
- **Gegenposition:** Pro Lebensbereich einen Satz: Was glaube ich anders als die meisten? Nicht nur in der Nische, auch zu Leben, Geld, Beziehungen.
- **Interessen außerhalb der Nische** zeigen, sobald die Basis steht. Damit Leute merken, dass du einer wie sie bist.
- Auch als Lernender hast du eine Sicht. Teil sie als das, was du bisher gemerkt hast, nicht als Expertenurteil.""",
     fields=["glaube", "gegen", "interessen"])

step(id="s26", ph="p4", title="Einfluss-Check und deine Beweise",
     src="Ronny Mitchell · Alex Hormozi", refs=["mv7t8c82qujgd1", "mvahormozi04"], ch=[9],
     why="Dein dokumentierter Weg wird mit der Zeit dein Beweis. So wächst Glaubwürdigkeit, ohne dass du je etwas behaupten musst.",
     body="""- Ronnys sechs Merkmale durchgehen (Vorreiter, Inspiration, Ähnlichkeit, Sicherheit, Sympathie, Hebel) und zu jedem einen Satz über dich schreiben. Details im Wissen, Kapitel 9.
- Eigene Beweise sammeln, auch eigene Fortschritte zählen.
- Rat gibst du erst zu dem, was du selbst gemacht hast (Ronny). Sag „Das hat bei mir funktioniert“ statt „So musst du es machen“.""",
     fields=["beweise", "grenze"])

step(id="s27", ph="p4", title="Meilenstein: 100.000 Aufrufe und 10.000 Follower",
     src="Mino, If you're in college · how i grew 200K followers", refs=["muyyxm20972jcz", "muwzljdpz2t1bs"], ch=[8],
     why="Danach kommt Phase 4: Geld.",
     body="""- Hattest du ein Video mit 100.000 Aufrufen?
- Hast du 10.000 Follower?
- Was läuft bei dir? Unter „Brand“ bei „Was ich gelernt habe“ ergänzen.""",
     fields=["laeuft", "naechstes"])

step(id="s28", ph="p5", title="Die ersten 1.000 $: UGC und Markendeals",
     src="Mino · Leitfaden Kapitel 10", refs=["muwdk6hmnlylop", "muwbmswt80g4wc"], ch=[10],
     why="Es gibt nur zwei Wege, mit Content Geld zu verdienen (Mino): fremde Produkte bewerben oder ein eigenes verkaufen.",
     body="""- **UGC** weiter ausbauen: Skript-Vorlage der Marke, drehen, schicken, Freigabe abwarten, posten, Auszahlung.
- **Markendeals:** Anfragen kommen schon bei 1.000 bis 10.000 Followern, wenn die Business-E-Mail in der Bio steht.
- Viral heißt nicht Geld: 50 Millionen Aufrufe mit Sketchen brachten Mino rund 2.000 $.
- Nachteil von Weg 1: abhängig von Marken und vom nächsten viralen Video.""")

step(id="s29", ph="p5", title="Eigenes Angebot, erst mit echten Ergebnissen",
     src="Mino, how i built a $1M business", refs=["muwbmswt80g4wc", "mvahormozi03"], ch=[10],
     why="Mehr Arbeit, aber es reichen weniger Aufrufe. Mino: Phasen lassen sich nicht überspringen.",
     body="""- Digitales Produkt, Coaching, Community, App oder eigene Marke.
- Minos Rechnung: 10.000 Aufrufe, 1 % kommt in deinen Funnel, 10 % davon kaufen. Das sind 10 Kunden, bei 100 $ also 1.000 $. Dafür reichen 1.000 echte Fans.
- 10.000 $ im Monat sind etwa 5 Kunden à 2.000 $ oder 10 à 1.000 $.
- **Bei einem Angebot bleiben**, mindestens 3 Monate. Preis und Verkaufsweg anpassen, aber nicht ständig etwas Neues. Mino startete mit einem Discord für 50 $ im Monat.
- Call to Action dezent an eine wertvolle Geschichte hängen.
- Eigene Kanäle aufbauen: E-Mail-Liste gehört dir, Follower nicht (Sam Gaudet).
- Buchtipp: „$100M Offers“ von Alex Hormozi.""",
     fields=["spaeter"])

step(id="s30", ph="p6", title="Deine eigene Video-Checkliste (SOP)",
     src="Mino, how i built a $1M business", refs=["muwbmswt80g4wc"], ch=[11],
     why="So kam Mino von 4 auf 1 bis 2 Stunden pro Video.",
     body="""- Routine vor dem Filmen, Sammlung bewährter Hooks, Liste mit Dos und Don'ts.
- Kein ganzes Skript mehr, nur Stichpunkte und ein starker Hook.
- Schnitt kann später ein Editor übernehmen (Ronny). Wichtig ist, dass du verstehst, was guter Schnitt ist.""")

step(id="s31", ph="p6", title="Deine Skill-Leiter",
     src="Ronny Mitchell, watch this if you want to get rich in your 20's", refs=["mv7spfhqnv97hg"], ch=[11],
     why="Such dir ein Feld, in dem viel Geld steckt, und steig mit der kleinsten Fähigkeit ein (Ronny).",
     body="""- 4 bis 6 Stufen aufschreiben, jede baut auf der vorigen auf. Bei Ronny: Videoschnitt, Kamera und Licht, Creative Direction, Strategie, das Paket als Dienstleistung verkaufen, Leute einstellen.
- **Nimm Leuten Arbeit ab, ohne zu fragen.** Mach es, hol Feedback, mach es besser.
- Frag später nicht „Was zahlst du mir?“, sondern: „Was muss wahr sein, damit ich in dieser Rolle X verdiene?“""")

# ---------- Checklisten der Werkstatt ----------
STAGES = [
    {"id": "idee", "label": "Idee", "tips": [
        "Ein Thema, ein Problem. Die Idee muss in 10 Wörtern erklärbar sein (Mino).",
        "Nachfrage prüfen: Gibt es zu dem Thema Videos mit vielen Aufrufen? (Ronny)",
        "10 Ideen in 10 Minuten: erst 4 Minuten Begriffe sammeln, dann Ideen (Mino).",
        "Nur, was du wirklich lösen oder erzählen kannst (Ronny)."]},
    {"id": "hook", "label": "Hook", "tips": [
        "Keine Begrüßung, keine Vorstellung. Du sprichst zu Fremden (Mino).",
        "Erster Satz in 1,5 Sekunden, höchstens 15 Wörter. Ein 10-jähriges Kind muss ihn verstehen (Mino).",
        "Bewährten Hook nehmen und nur ein, zwei Wörter anpassen (Mino, Copy Understand Maximize).",
        "Ein bis zwei Schlüsselwörter, ein Schmerz, den der Zuschauer kennt (Ronny, Mino)."]},
    {"id": "skript", "label": "Skript", "tips": [
        "Eine Hauptaussage. Kurze Sätze, höchstens 12 Wörter (Mino).",
        "Zu einer Person sprechen, meistens zu deinem früheren Ich. Wie ein Freund, nie wie ein Guru.",
        "Konkret: Zahlen, Orte, Alter, Namen. „Vor 45 Tagen“ statt „vor einer Weile“.",
        "Prüfen lassen: „Überarbeite das Skript und finde alle Stellen, die verwirrend sind oder bei denen Leute weiterscrollen würden.“ (Mino)"]},
    {"id": "dreh", "label": "Dreh", "checks": [
        "Hellstes Licht vor mir, nie dahinter",
        "Handy nah dran, auf Augenhöhe, ruhiger Hintergrund",
        "Stimme 1 Minute aufgewärmt (Sirene von hoch nach tief)",
        "Einatmen, 6 Sek. halten, 8 Sek. ausatmen",
        "Direkt in die Kamera geschaut, Teleprompter in CapCut",
        "Hook zuletzt aufgenommen, dann ist die Stimme warm",
        "B-Roll gefilmt (Tätigkeit 30 Sek., Gehen oder Bildschirm 10 Sek.)"],
     "src": "Mino · Julian Treasure",
     "tips": ["Pfad statt Schiene: die Gliederung ist ein Wegweiser, nicht Wort für Wort ablesen. Vorher einprägen, frei erzählen, dieselben Gedanken oft wiederholen (Sam Gaudet). Mino nutzt dagegen oft den Teleprompter, probier beides."]},
    {"id": "schnitt", "label": "Schnitt", "checks": [
        "Rohschnitt über das Transkript: Versprecher als Text gelöscht",
        "Feinschnitt: jede Pause bis direkt ans letzte Wort weg",
        "B-Roll bei jedem neuen Satz, in den ersten 3 bis 4 Sek. Schnitte unter 1 Sek.",
        "Untertitel: höchstens 4 Wörter, eine Zeile, etwa 30 % über dem unteren Rand",
        "Musik passend zum Gefühl, ohne lauten Gesang, leise unter der Sprache",
        "Nie 2 Sekunden ohne Ton, Musik oder Bewegung",
        "Export 4K, 30 fps"],
     "src": "Mino, Minimum Viable Editing · ViralEditsOS"},
    {"id": "check", "label": "Check", "checks": [
        "Löst ein echtes Problem, das Leute wirklich haben",
        "Startet mit einer starken Aussage, die ohne Kontext verständlich ist",
        "Ein bis zwei Schlüsselwörter im Hook",
        "Jeder Fachbegriff sofort erklärt",
        "Würde jemand, der mich nie gesehen hat, das verstehen und mögen?",
        "Ich rede wie mit einem Freund, nicht mit einer Kamera-Stimme",
        "Konkrete Zahlen, Orte oder Namen drin"],
     "src": "Ronny Mitchell, Video-Check · Mino, 15 Fehler"},
    {"id": "posten", "label": "Posten", "checks": [
        "In der Instagram-App hochgeladen, nicht direkt aus CapCut",
        "Kurze Beschreibung, höchstens 1 Hashtag",
        "Vor dem Schlafen online"],
     "src": "Mino"},
]

# ---------- Wissen ----------
CH = {}
for i in src["items"]:
    if i["kind"] == "kmv7tso3zp2fssf" and re.match(r"^\d+ · ", i["title"]):
        n = int(i["title"].split(" ")[0])
        if n == 0:
            continue
        CH[n] = i
fmt = next(i for i in src["items"] if i["id"] == "mv7t8c82v1gn8u")
WISSEN = []
for n in sorted(CH):
    i = CH[n]
    WISSEN.append({"id": "k%d" % n, "n": n, "title": i["title"].split(" · ", 1)[1], "body": clean(i["body"]), "refs": [r for r in i.get("rel", [])]})
WISSEN.append({"id": "formate", "n": None, "title": "Format-Tabelle: 25 Formate bewertet", "body": clean(fmt["body"]), "refs": fmt.get("rel", [])})

CREATORS = [("Mino-Lee", "Mino Lee"), ("Ronny-Mitchell", "Ronny Mitchell"), ("Sam-Gaudet", "Sam Gaudet"), ("Alex-Hormozi", "Alex Hormozi"), ("Julian-Treasure", "Julian Treasure"), ("Caleb-Ralston", "Caleb Ralston"), ("Ekko-Amaryllis", "Ekko Amaryllis"), ("Richard-Yu", "Richard Yu"), ("Robert-McKeaveney", "Robert McKeaveney")]
SRC = {}
for i in src["items"]:
    if i["kind"] != "resource" or i.get("archived"):
        continue
    tags = i.get("tags", [])
    if not (i.get("topic") == "tmusc5da9pm0dij" or set(tags) & {c for c, _ in CREATORS}):
        continue
    who = next((n for c, n in CREATORS if c in tags), "Werkzeuge")
    url = (i.get("links") or [{}])[0].get("url", "")
    body = re.sub(r"[#*_>`\[\]]", "", i.get("body", "")).strip()
    first = next((p.strip() for p in body.split("\n\n") if len(p.strip()) > 40), "")
    first = re.sub(r"\s+", " ", first)
    if len(first) > 230:
        first = first[:230].rsplit(" ", 1)[0] + " …"
    SRC[i["id"]] = {"t": clean(i["title"]), "who": who, "url": url, "sum": clean(first), "img": i.get("image", "")}

for st in S:
    st["refs"] = [r for r in st["refs"] if r in SRC]
for w in WISSEN:
    w["refs"] = [r for r in w["refs"] if r in SRC]

data = {"phases": PHASES, "steps": S, "fields": FIELDS, "sections": SECTIONS, "types": TYPES, "stages": STAGES, "wissen": WISSEN, "sources": SRC}
txt = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
for bad in ("Daniel", "Mama", "15 Jahre"):
    assert bad not in txt, "persönliche Angabe in data.js: " + bad
OUT.write_text("window.BW=" + txt + ";\n", encoding="utf-8")
print("ok", len(S), "Schritte,", len(WISSEN), "Kapitel,", len(SRC), "Quellen,", len(txt), "Zeichen")
