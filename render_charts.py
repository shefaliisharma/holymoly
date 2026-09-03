#!/usr/bin/env python
"""
Render the Apple Music analysis charts in the "Ledger" brand palette.
Reads directly from the local PostgreSQL `apple_music_dataset` table and writes
light + dark PNGs (transparent background) into assets/ as c1..c8[-dark].png.

Palette validated against the data-viz CVD checks (protan/deutan OKLab dE).
"""
import os, warnings, math
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import psycopg2

warnings.filterwarnings("ignore")
OUT = "assets"

# Connection details come from the environment (never hard-coded).
# Set at least PGPASSWORD before running, e.g.:
#   PGPASSWORD=yourpassword python render_charts.py
# Host/port/database/user fall back to the local dev defaults.
conn = psycopg2.connect(
    host=os.environ.get("PGHOST", "localhost"),
    port=os.environ.get("PGPORT", "5432"),
    dbname=os.environ.get("PGDATABASE", "shefalisharma"),
    user=os.environ.get("PGUSER", "postgres"),
    password=os.environ.get("PGPASSWORD"),
)
def sql(q):
    return pd.read_sql(q, conn)

# ---- themes -----------------------------------------------------------------
THEMES = {
    "light": dict(ink="#1A1D22", muted="#5B636E", faint="#8A919C", grid="#E7E4DD",
                  accent="#16704F", neg="#C4792B",
                  cat=["#12805B", "#2F6DB4", "#C4792B", "#8A4FA6"],
                  seq=["#EAF2ED", "#8FBFA9", "#3E9670", "#0E4C36"]),
    "dark":  dict(ink="#E9EAE6", muted="#9BA2AC", faint="#6C7480", grid="#2A2F36",
                  accent="#46C08B", neg="#C4823B",
                  cat=["#2FA574", "#4E8AD1", "#C4823B", "#A972C9"],
                  seq=["#15251D", "#1F5B43", "#3E9E76", "#8FE0B8"]),
}

def base(figsize, t):
    fig, ax = plt.subplots(figsize=figsize, dpi=200)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(t["grid"])
    ax.tick_params(colors=t["muted"], labelsize=9, length=0)
    ax.grid(axis="y", color=t["grid"], linewidth=.8, alpha=.9)
    ax.set_axisbelow(True)
    plt.rcParams["font.family"] = "sans-serif"
    return fig, ax

def label(ax, t, x=True, y=True):
    if ax.get_xlabel(): ax.xaxis.label.set_color(t["muted"]); ax.xaxis.label.set_size(9.5)
    if ax.get_ylabel(): ax.yaxis.label.set_color(t["muted"]); ax.yaxis.label.set_size(9.5)

def save(fig, name):
    fig.savefig(f"{OUT}/{name}.png", transparent=True, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)

facts = {}

# ============================================================ CHART 1: line
df1 = sql('''SELECT "primaryGenreName" genre, EXTRACT(year FROM "releaseDate")::int yr,
             COUNT("trackId") n FROM apple_music_dataset
             WHERE EXTRACT(year FROM "releaseDate") > 1900
             GROUP BY 1,2''')
top3 = df1.groupby("genre").n.sum().nlargest(3).index.tolist()
def chart1(tn, t):
    fig, ax = base((7.2, 4.0), t)
    for i, g in enumerate(top3):
        d = df1[df1.genre == g].sort_values("yr")
        ax.plot(d.yr.to_numpy(), d.n.to_numpy(), color=t["cat"][i], lw=2, label=g)
    ax.set_xlim(1950, df1.yr.max() + 2)
    leg = ax.legend(loc="upper left", frameon=False, fontsize=10.5,
                    labelcolor="linecolor", handlelength=1.3, borderaxespad=.2)
    for txt in leg.get_texts():
        txt.set_fontweight("bold")
    ax.set_ylabel("Tracks released")
    ax.set_xlabel("Release year")
    label(ax, t)
    save(fig, "c1" + ("" if tn == "light" else "-dark"))

# ============================================================ CHART 2: avg price / genre (explicit)
df2 = sql('''SELECT "primaryGenreName" genre,
             ROUND(SUM("trackPrice")/COUNT("trackId")::decimal, 2) avg_price,
             COUNT("trackId") n
             FROM apple_music_dataset WHERE "trackExplicitness"='explicit'
             GROUP BY 1 HAVING COUNT("trackId") >= 5 ORDER BY avg_price DESC''')
def chart2(tn, t):
    d = df2.sort_values("avg_price")
    fig, ax = base((7.2, max(3.2, .34 * len(d))), t)
    ax.grid(axis="y", alpha=0); ax.grid(axis="x", color=t["grid"], lw=.8)
    colors = [t["neg"] if g == "Hip-Hop/Rap" else t["accent"] for g in d.genre]
    ax.barh(d.genre.to_numpy(), d.avg_price.to_numpy(), color=colors, height=.66)
    for y, (g, v) in enumerate(zip(d.genre, d.avg_price)):
        ax.text(v + .01, y, f"${v:.2f}", va="center", ha="left", fontsize=8.5, color=t["muted"])
    ax.set_xlim(0, d.avg_price.max() * 1.15)
    ax.set_xlabel("Avg price per explicit track (USD)")
    for lb in ax.get_yticklabels():
        lb.set_color(t["neg"] if lb.get_text() == "Hip-Hop/Rap" else t["ink"]); lb.set_fontsize(9)
    label(ax, t)
    save(fig, "c2" + ("" if tn == "light" else "-dark"))
hh = df2.reset_index(drop=True)
facts["hh_rank"] = int(hh.index[hh.genre == "Hip-Hop/Rap"][0]) + 1 if (hh.genre == "Hip-Hop/Rap").any() else None
facts["hh_price"] = float(hh.loc[hh.genre == "Hip-Hop/Rap", "avg_price"].iloc[0]) if (hh.genre == "Hip-Hop/Rap").any() else None
facts["top_price_genre"] = (hh.iloc[0].genre, float(hh.iloc[0].avg_price))

# ============================================================ CHART 3: heatmap genre x decade
df3 = sql('''SELECT "primaryGenreName" genre,
             (FLOOR(EXTRACT(year FROM "releaseDate")/10)*10)::int decade, COUNT("trackId") n
             FROM apple_music_dataset WHERE EXTRACT(year FROM "releaseDate") > 1900
             GROUP BY 1,2''')
g8 = df3.groupby("genre").n.sum().nlargest(8).index.tolist()
piv = (df3[df3.genre.isin(g8)].pivot_table(index="genre", columns="decade", values="n", fill_value=0)
       .reindex(g8))
piv = piv[[c for c in piv.columns if c >= 1950]]
def chart3(tn, t):
    cmap = LinearSegmentedColormap.from_list("g", t["seq"])
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
    fig.patch.set_alpha(0); ax.set_facecolor("none")
    im = ax.imshow(piv.values, aspect="auto", cmap=cmap)
    ax.set_xticks(range(len(piv.columns))); ax.set_xticklabels([f"{c}s" for c in piv.columns])
    ax.set_yticks(range(len(piv.index))); ax.set_yticklabels(piv.index)
    ax.tick_params(colors=t["muted"], labelsize=9, length=0)
    for lb in ax.get_yticklabels(): lb.set_color(t["ink"])
    mx = piv.values.max()
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = int(piv.values[i, j])
            if v > 0:
                ax.text(j, i, v, ha="center", va="center", fontsize=7.5,
                        color="#FFFFFF" if v > mx * .55 else t["muted"])
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_xticks(np.arange(-.5, len(piv.columns), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(piv.index), 1), minor=True)
    ax.grid(which="minor", color=t["grid"], lw=2); ax.tick_params(which="minor", length=0)
    save(fig, "c3" + ("" if tn == "light" else "-dark"))

# ============================================================ CHART 4: price-duration corr / genre (diverging)
df4 = sql('''SELECT "primaryGenreName" genre, "trackPrice"::float p, "trackTimeMillis"::float d
             FROM apple_music_dataset WHERE "trackPrice" > 0 AND "trackTimeMillis" IS NOT NULL''')
corr = (df4.groupby("genre").filter(lambda x: len(x) >= 25)
        .groupby("genre").apply(lambda x: x.p.corr(x.d)).dropna().sort_values())
def chart4(tn, t):
    fig, ax = base((7.2, max(3.2, .34 * len(corr))), t)
    ax.grid(axis="y", alpha=0); ax.grid(axis="x", color=t["grid"], lw=.8)
    colors = [t["neg"] if v < 0 else t["accent"] for v in corr.values]
    ax.barh(list(corr.index), corr.to_numpy(), color=colors, height=.66)
    ax.axvline(0, color=t["muted"], lw=1)
    for y, v in enumerate(corr.values):
        ax.text(v + (.01 if v >= 0 else -.01), y, f"{v:+.2f}", va="center",
                ha="left" if v >= 0 else "right", fontsize=8.5, color=t["muted"])
    m = max(abs(corr.min()), abs(corr.max())) * 1.25
    ax.set_xlim(-m, m); ax.set_xlabel("Correlation: track price ↔ duration")
    for lb in ax.get_yticklabels(): lb.set_color(t["ink"]); lb.set_fontsize(9)
    label(ax, t)
    save(fig, "c4" + ("" if tn == "light" else "-dark"))
facts["corr_pos"] = (corr.index[-1], float(corr.iloc[-1]))
facts["corr_neg"] = (corr.index[0], float(corr.iloc[0]))

# ============================================================ CHART 5: top collection release spans
df5 = sql('''WITH c AS (
               SELECT "collectionId" cid, MAX("collectionName") AS "name",
                 (MAX("releaseDate")::date - MIN("releaseDate")::date) days
               FROM apple_music_dataset WHERE EXTRACT(year FROM "releaseDate") > 1900
               GROUP BY 1 HAVING COUNT(*) >= 2)
             SELECT c.name, c.days/365.0 yrs,
               (SELECT "primaryGenreName" FROM apple_music_dataset a WHERE a."collectionId"=c.cid LIMIT 1) genre
             FROM c ORDER BY days DESC LIMIT 12''')
def chart5(tn, t):
    d = df5.sort_values("yrs")
    fig, ax = base((7.2, .42 * len(d) + 1), t)
    ax.grid(axis="y", alpha=0); ax.grid(axis="x", color=t["grid"], lw=.8)
    ax.barh(range(len(d)), d.yrs.to_numpy(), color=t["accent"], height=.66)
    ax.set_yticks(range(len(d)))
    ax.set_yticklabels([(n[:30] + "…" if len(n) > 31 else n) for n in d.name], fontsize=8.5)
    for lb in ax.get_yticklabels(): lb.set_color(t["ink"])
    for y, (v, g) in enumerate(zip(d.yrs, d.genre)):
        ax.text(v + .3, y, f"{v:.0f}y · {g}", va="center", fontsize=8, color=t["muted"])
    ax.set_xlim(0, d.yrs.max() * 1.28); ax.set_xlabel("Years between first & last track in the collection")
    label(ax, t)
    save(fig, "c5" + ("" if tn == "light" else "-dark"))
facts["top_span"] = (df5.iloc[0]["name"], float(df5.iloc[0]["yrs"]), df5.iloc[0]["genre"])

# ============================================================ CHART 6: single vs collection (table -> print stats)
df6 = sql('''WITH cat AS (
               SELECT "collectionId" cid,
                 CASE WHEN COUNT("trackId")=1 THEN 'Single' ELSE 'Collection' END kind
               FROM apple_music_dataset GROUP BY 1)
             SELECT cat.kind,
               COUNT(*) tracks,
               ROUND(AVG("trackPrice"),2) avg_price,
               COUNT(DISTINCT a."collectionId") collections
             FROM apple_music_dataset a JOIN cat ON a."collectionId"=cat.cid
             GROUP BY cat.kind ORDER BY tracks DESC''')
facts["table6"] = df6.to_dict("records")

# ============================================================ CHART 7: tracks-in-collection vs avg price (scatter)
df7 = sql('''SELECT "collectionId" cid, COUNT("trackId") ntracks, AVG("trackPrice") avg_price
             FROM apple_music_dataset WHERE "trackPrice" > 0
             GROUP BY 1 HAVING COUNT("trackId") >= 1''')
def chart7(tn, t):
    fig, ax = base((7.2, 4.0), t)
    ax.grid(axis="x", color=t["grid"], lw=.8)
    ax.scatter(df7.ntracks.to_numpy(), df7.avg_price.to_numpy(), s=22, color=t["accent"], alpha=.28, edgecolors="none")
    med = df7.avg_price.median()
    ax.axhline(med, color=t["neg"], lw=1.6, ls=(0, (4, 3)))
    ax.text(df7.ntracks.max(), med, f"  median ${med:.2f}", color=t["neg"], va="bottom", ha="right", fontsize=9)
    ax.set_xlabel("Tracks in the collection"); ax.set_ylabel("Average track price (USD)")
    ax.set_ylim(0, df7.avg_price.quantile(.99) * 1.1)
    label(ax, t)
    save(fig, "c7" + ("" if tn == "light" else "-dark"))

# ============================================================ CHART 8: duration outliers, top 5 artists (strip)
df8 = sql('''WITH top AS (
               SELECT "artistId" aid, MAX("artistName") AS "name", COUNT(*) n
               FROM apple_music_dataset GROUP BY 1 ORDER BY n DESC LIMIT 5)
             SELECT top.name, a."trackName" track, a."trackTimeMillis"/60000.0 mins
             FROM apple_music_dataset a JOIN top ON a."artistId"=top.aid
             WHERE a."trackTimeMillis" IS NOT NULL''')
def chart8(tn, t):
    artists = df8.groupby("name").mins.count().sort_values(ascending=False).index.tolist()
    fig, ax = base((7.2, 4.2), t)
    ax.grid(axis="x", alpha=0); ax.grid(axis="y", color=t["grid"], lw=.8)
    rng = np.random.default_rng(7)
    top_out = None
    for i, name in enumerate(artists):
        d = df8[df8.name == name]
        p5, p95 = d.mins.quantile(.05), d.mins.quantile(.95)
        mv = d.mins.to_numpy()
        mask = ((mv > p95) | (mv < p5))
        xj = i + rng.uniform(-.16, .16, len(d))
        ax.scatter(xj[~mask], mv[~mask], s=20, color=t["accent"], alpha=.5, edgecolors="none")
        ax.scatter(xj[mask], mv[mask], s=34, color=t["neg"], alpha=.95,
                   edgecolors="none", zorder=3)
        hi = d.loc[d.mins.idxmax()]
        if top_out is None or hi.mins > top_out[1]:
            top_out = (hi.track, float(hi.mins), name)
    ax.set_xticks(range(len(artists)))
    ax.set_xticklabels([(a[:15] + "…" if len(a) > 16 else a) for a in artists],
                       fontsize=8.5, rotation=12, ha="right")
    for lb in ax.get_xticklabels(): lb.set_color(t["ink"])
    ax.set_ylabel("Track duration (minutes)")
    label(ax, t)
    save(fig, "c8" + ("" if tn == "light" else "-dark"))
    return top_out

# ---- render all -------------------------------------------------------------
last = None
for tn, t in THEMES.items():
    chart1(tn, t); chart2(tn, t); chart3(tn, t); chart4(tn, t)
    chart5(tn, t); chart7(tn, t); last = chart8(tn, t)
facts["top_out"] = last
facts["top3_genres"] = top3

import json
print("FACTS:", json.dumps(facts, default=str, indent=2))
conn.close()
print("done")
