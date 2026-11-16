"""Data Interpretation questions from the restaurant regression case (Excel Part 4).
Models are estimated on the real merged data; students read the output and predict/interpret.
Answers are computed from the coefficients AS DISPLAYED (rounded), so a student working from
the table gets exactly the stored answer."""
import json, sys, datetime as dt
sys.path.insert(0, "/home/claude/work")
from restaurant import load, ols
from kit import make

d, raw = load(sys.argv[1])
d = d.assign(interaction=d.sales_364 * d.gameDay)
fit = d[(d.sales_7 > 0) & (d.sales_364 > 0)]          # zeros = restaurant closed that day, not $0 sales
CASE = "Excel Part 4 · Restaurant regression (Larry's Commissary)"
LABEL = {"Intercept": "Intercept", "tmax": "Max temperature (°F)", "gameDay": "Game day (1 = yes)",
         "sales_7": "Sales 7 days earlier ($)", "sales_364": "Sales 364 days earlier ($)",
         "interaction": "Sales 364 days earlier × Game day"}

def rnd(term, v):
    return round(v, 3) if term in ("sales_7", "sales_364", "interaction") else round(v, 2)

MODELS = {}
def model(key, title, xs):
    m = ols(fit, "sales", xs)
    coefs = [{"term": t, "label": LABEL[t], "estimate": rnd(t, b), "se": rnd(t, s), "p": round(float(p), 3)}
             for t, b, s, p in zip(m["terms"], m["b"], m["se"], m["p"])]
    MODELS[key] = {"key": key, "title": title, "outcome": "Daily sales ($)", "n": int(m["n"]),
                   "r2": round(float(m["r2"]), 3), "coefficients": coefs}
    return {c["term"]: c["estimate"] for c in coefs}, {c["term"]: c["p"] for c in coefs}

T, Tp = model("M1", "Model 1: sales and temperature", ["tmax"])
G, Gp = model("M2", "Model 2: sales and game days", ["gameDay"])
P, Pp = model("M3", "Model 3: prediction model", ["sales_7", "sales_364", "gameDay"])
I, Ip = model("M4", "Model 4: last year's sales × game day", ["sales_364", "gameDay", "interaction"])
F, Fp = model("M5", "Model 5: prediction model + temperature", ["sales_7", "sales_364", "gameDay", "tmax"])

Q = []
def add(qid, mkey, prompt, ans, how, explain, traps, unit="USD", tol=None, kind="number", **kw):
    tol = tol if tol is not None else (max(1.0, abs(ans) * 0.002) if kind == "number" else 0)
    extra = {"model": MODELS[mkey], "explanation": explain}
    extra.update(kw.pop("extra", {}))
    Q.append(make(qid, "restaurant", "Interpretation", CASE, prompt, round(ans, 2) if kind == "number" else ans,
                  {"excel": how}, traps, tol=tol, unit=unit if kind == "number" else None, extra=extra, **kw))

f2 = lambda v: f"{v:,.2f}"
# ---------------- predictions (Model 3) ----------------
last = d.date.max()
target = last + dt.timedelta(days=7)
s7 = float(d.loc[d.date == last, "sales"].iloc[0])                       # sales on 31 Dec 2018
s364 = float(d.loc[d.date == target - dt.timedelta(days=364), "sales"].iloc[0])
# clearer helper: x7 = sales 7 days earlier, x364 = sales 364 days earlier, g = game day
pr = lambda x7, x364, g: P["Intercept"] + P["sales_7"] * x7 + P["sales_364"] * x364 + P["gameDay"] * g
EQ = f"{P['Intercept']} + {P['sales_7']}×(sales 7 days earlier) + {P['sales_364']}×(sales 364 days earlier) + {P['gameDay']}×(game day)"

def pred_q(qid, prompt, x7, x364, g):
    ans = pr(x7, x364, g)
    traps = [(ans - P["Intercept"], "You left out the intercept. A prediction always starts from the intercept, then adds each coefficient × its value."),
             (P["Intercept"] + P["sales_7"] * x364 + P["sales_364"] * x7 + P["gameDay"] * g, "You swapped the two sales values: the 0.%s coefficient belongs to sales 7 days earlier, the other to sales 364 days earlier." % str(P["sales_7"]).split(".")[1])]
    if g == 1:
        traps.append((pr(x7, x364, 0), "It's a game day, so add the game-day coefficient (× 1)."))
    else:
        traps.append((pr(x7, x364, 1), "It's not a game day: the dummy is 0, so the game-day coefficient adds nothing."))
    add(qid, "M3", prompt, ans,
        f"Prediction = {EQ}. Here: {P['Intercept']} + {P['sales_7']}×{x7:,.0f} + {P['sales_364']}×{x364:,.0f} + {P['gameDay']}×{g} = {f2(ans)}.",
        "Each coefficient is multiplied by its value and added to the intercept. The game-day dummy is either 0 or 1, so its coefficient is either added in full or not at all.",
        traps)

pred_q("RI01", f"Bob wants a forecast for {target:%A %d %B %Y}, 7 days after the last day in the data. Sales on {last:%d %B %Y} were ${s7:,.0f}, sales 364 days before the target day were ${s364:,.0f}, and there is no game. What are the predicted sales?", s7, s364, 0)
pred_q("RI02", "Predict sales for a Saturday with a home game, when sales 7 days earlier were $4,500 and sales 364 days earlier were $4,800.", 4500, 4800, 1)
pred_q("RI03", "Predict sales for a Tuesday without a game, when sales 7 days earlier were $2,300 and sales 364 days earlier were $2,100.", 2300, 2100, 0)
pred_q("RI04", "Predict sales for a game day when sales 7 days earlier were $3,900 and sales 364 days earlier were $5,200.", 3900, 5200, 1)

# ---------------- temperature (Model 1) ----------------
b, a = T["tmax"], T["Intercept"]
add("RI05", "M1", "According to Model 1, by how much do predicted daily sales change when the maximum temperature rises by 10 °F?", 10 * b,
    f"Slope × change = {b} × 10 = {f2(10*b)}.",
    "The coefficient is the change in predicted sales for a 1-unit (1 °F) increase, holding nothing else constant in this simple model.",
    [(b, "That's the effect of 1 °F. The question asks for a 10 °F increase: multiply by 10."),
     (a + 10 * b, "You added the intercept. A change in sales only involves the slope; the intercept matters for a level (prediction), not a difference.")])
add("RI06", "M1", "The temperature in the data is in Fahrenheit. By how much do predicted daily sales change when the maximum temperature rises by 10 °C?", 18 * b,
    f"A change of 10 °C = 18 °F (1 °C = 1.8 °F), so {b} × 18 = {f2(18*b)}.",
    "Always check the units of a variable before using a coefficient. A 10-degree change in Celsius is an 18-degree change in Fahrenheit.",
    [(10 * b, "The model's temperature is in °F. A rise of 10 °C equals 18 °F, so multiply the coefficient by 18, not 10."),
     (b * (10 * 1.8 + 32), "For a CHANGE in temperature, only the 1.8 factor applies. The +32 is for converting a temperature level, not a difference.")])
add("RI07", "M1", "Using Model 1, predict daily sales on a day with a maximum temperature of 25 °C.", a + b * 77,
    f"25 °C = 25 × 1.8 + 32 = 77 °F. Prediction = {a} + {b} × 77 = {f2(a + b*77)}.",
    "To predict, convert the input to the model's units first (°F), then intercept + slope × value.",
    [(a + b * 25, "The model uses °F. 25 °C is 77 °F (×1.8 + 32); you plugged in 25 directly."),
     (a + b * 45, "For a temperature LEVEL, convert with °F = °C × 1.8 + 32. You forgot the +32."),
     (b * 77, "You forgot the intercept.")])
sig1 = "yes" if Tp["tmax"] < 0.05 else "no"
sig5 = "yes" if Fp["tmax"] < 0.05 else "no"
add("RI08", "M1", "At the 5% significance level, is maximum temperature a significant predictor of sales in Model 1? (yes / no)", sig1,
    f"The p-value for temperature is {Tp['tmax']}, which is {'below' if sig1=='yes' else 'above'} 0.05, so the answer is '{sig1}'.",
    "A coefficient is significant at 5% when its p-value is below 0.05. Significance says the effect is unlikely to be zero; it does not say the effect is large. Model 1 explains only "
    f"{MODELS['M1']['r2']*100:.1f}% of the variation in sales.",
    [("no" if sig1 == "yes" else "yes", f"Compare the p-value ({Tp['tmax']}) with 0.05: below 0.05 means significant. Don't compare the coefficient or R² with 0.05."),
     ("not significant" if sig1 == "yes" else "significant", f"Compare the p-value ({Tp['tmax']}) with 0.05: below 0.05 means significant.")],
    kind="text", extra={"alternatives": ["significant"] if sig1 == "yes" else ["not significant"]})
add("RI09", "M5", "In Model 5, which also includes past sales and game days, is maximum temperature significant at the 5% level? (yes / no)", sig5,
    f"The p-value for temperature is now {Fp['tmax']}, {'below' if sig5=='yes' else 'above'} 0.05, so the answer is '{sig5}'.",
    f"Temperature was significant on its own (Model 1, p = {Tp['tmax']}) but not once past sales are included (p = {Fp['tmax']}). Past sales already capture the seasonal pattern that temperature was picking up, so temperature adds little extra information. "
    "This is why a simple regression can overstate an effect (omitted variables).",
    [("no" if sig5 == "yes" else "yes", f"Look at Model 5's p-value ({Fp['tmax']}), not Model 1's. Once past sales are in the model, temperature is no longer significant at 5%."),
     ("significant" if sig5 == "no" else "not significant", f"Look at Model 5's p-value ({Fp['tmax']}), not Model 1's.")],
    kind="text", extra={"alternatives": ["not significant"] if sig5 == "no" else ["significant"]})

# ---------------- game day (Model 2 and Model 3) ----------------
add("RI10", "M2", "According to Model 2, how much higher are predicted sales on a game day than on other days?", G["gameDay"],
    f"For a 0/1 dummy, the coefficient is the difference between the two groups: {G['gameDay']}.",
    "A dummy coefficient compares the '1' group (game days) with the '0' group (other days). The intercept is the average for the '0' group.",
    [(G["Intercept"] + G["gameDay"], "That's the predicted LEVEL of sales on a game day (intercept + coefficient). The question asks how much HIGHER, which is the coefficient alone."),
     (G["Intercept"], "That's the predicted sales on a non-game day (the intercept).")])
add("RI11", "M2", "According to Model 2, what are predicted sales on a game day?", G["Intercept"] + G["gameDay"],
    f"Intercept + game-day coefficient × 1 = {G['Intercept']} + {G['gameDay']} = {f2(G['Intercept'] + G['gameDay'])}.",
    "The prediction for the dummy = 1 group is the intercept plus the dummy coefficient.",
    [(G["gameDay"], "That's the DIFFERENCE between game days and other days. For the predicted level, add the intercept.")])
add("RI12", "M3", "In Model 3, how much higher are predicted sales on a game day than on another day with the same past sales?", P["gameDay"],
    f"Holding the other variables constant, the dummy coefficient is the difference: {P['gameDay']}.",
    f"Notice the game-day effect is much smaller here ({P['gameDay']}) than in Model 2 ({G['gameDay']}), and its p-value is {Pp['gameDay']}. Games fall on Saturdays, which are busy anyway; once sales on the same weekday last year and last week are included, part of the 'game effect' turns out to be a weekday effect.",
    [(G["gameDay"], "That's Model 2's coefficient. Model 3 controls for past sales, so read the game-day coefficient from Model 3."),
     (P["Intercept"] + P["gameDay"], "You added the intercept. 'How much higher' is the coefficient alone.")])

# ---------------- interaction (Model 4) ----------------
add("RI13", "M4", "In Model 4, on a game day, by how much do predicted sales increase for each extra $1 of sales 364 days earlier?", I["sales_364"] + I["interaction"],
    f"On a game day the slope is {I['sales_364']} + {I['interaction']} × 1 = {round(I['sales_364'] + I['interaction'], 3)}.",
    "With an interaction, the effect of last year's sales depends on whether it's a game day: on non-game days the slope is the main coefficient; on game days you add the interaction coefficient.",
    [(I["sales_364"], "That's the slope on a NON-game day. On a game day, add the interaction coefficient."),
     (I["interaction"], "The interaction coefficient is only the EXTRA slope on game days; add it to the main sales_364 coefficient.")],
    unit="$ per $1", tol=0.001)
def gd_effect(x): return I["gameDay"] + I["interaction"] * x
add("RI14", "M4", "In Model 4, how much higher are predicted sales on a game day than on a non-game day, when sales 364 days earlier were $4,000?", gd_effect(4000),
    f"Game-day effect = {I['gameDay']} + {I['interaction']} × 4,000 = {f2(gd_effect(4000))}.",
    f"With an interaction, the game-day effect is not a single number: it depends on last year's sales. Note the large p-values ({Ip['gameDay']} and {Ip['interaction']}): the data give little evidence that game days change the relationship, so Bob shouldn't rely on this effect.",
    [(I["gameDay"], "You ignored the interaction. The game-day effect is gameDay coefficient + interaction coefficient × last year's sales."),
     (I["Intercept"] + I["sales_364"] * 4000 + gd_effect(4000), "That's the predicted LEVEL of sales on a game day. The question asks for the DIFFERENCE between game and non-game days.")])
add("RI15", "M4", "Using Model 4, predict sales on a game day when sales 364 days earlier were $4,500.", I["Intercept"] + I["sales_364"] * 4500 + I["gameDay"] + I["interaction"] * 4500,
    f"{I['Intercept']} + {I['sales_364']}×4,500 + {I['gameDay']}×1 + {I['interaction']}×(4,500×1) = {f2(I['Intercept'] + I['sales_364']*4500 + I['gameDay'] + I['interaction']*4500)}.",
    "The interaction variable is the product of the two variables (4,500 × 1 on a game day), multiplied by its coefficient.",
    [(I["Intercept"] + I["sales_364"] * 4500 + I["gameDay"], "You left out the interaction term. Its value is sales 364 days earlier × game day = 4,500 × 1."),
     (I["Intercept"] + I["sales_364"] * 4500, "It's a game day: add the game-day coefficient and the interaction term.")])
add("RI16", "M3", "What percentage of the variation in daily sales does Model 3 explain? (R², in %)", MODELS["M3"]["r2"] * 100,
    f"R² = {MODELS['M3']['r2']}, i.e. {MODELS['M3']['r2']*100:.1f}%.",
    f"About half of the day-to-day variation is explained, so predictions can easily be off by several hundred dollars. Bob should use the forecast as a guide for ordering and staffing, with a buffer.",
    [(MODELS["M2"]["r2"] * 100, "That's Model 2's R². Read it from Model 3.")],
    unit="%", tol=0.1)

json.dump({"questions": Q, "models": MODELS, "prediction_inputs": {"target": str(target.date()), "sales_7": s7, "sales_364": s364}},
          open("/home/claude/work/out_interp.json", "w"), indent=1, default=float)
print(len(Q), "interpretation questions;", target.date(), s7, s364)
