"""Moon phases and the waning window. Pure Python, on your computer, with zero network calls.

Ported from the sibling Rocha Coded kit analog-bag (core/moon.py, MIT, Copyright (c) 2026
Rochelle Livingstone / Thriving Era Studio). The equinox and solstice tables were left behind;
the waning-window functions at the bottom are new for this kit.

Phases use the method in Jean Meeus, Astronomical Algorithms (2nd ed.), chapter 49,
including the periodic and planetary correction terms. That gives Dynamical Time; we
subtract Delta T to get UT. Expected accuracy is a few minutes.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

J2000 = 2451545.0
SYNODIC = 29.530588861
PHASE_NAMES = ("new moon", "first quarter", "full moon", "last quarter")


def _sin(deg: float) -> float:
    return math.sin(math.radians(deg))


def _cos(deg: float) -> float:
    return math.cos(math.radians(deg))


def jd_to_datetime(jd: float) -> datetime:
    """Julian Day to an aware UTC datetime."""
    return datetime(2000, 1, 1, 12, tzinfo=timezone.utc) + timedelta(days=jd - J2000)


def datetime_to_jd(dt: datetime) -> float:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = dt - datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
    return J2000 + delta.total_seconds() / 86400.0


def delta_t_seconds(year: float) -> float:
    """Delta T (TT minus UT). NASA polynomial for 2005 to 2050, held flat outside it."""
    t = min(max(year, 2005.0), 2050.0) - 2000.0
    return 62.92 + 0.32217 * t + 0.005589 * t * t


def _phase_jde(k: float) -> float:
    """Meeus 49.1 plus corrections. k is an integer for new moon, +.25 first quarter,
    +.5 full, +.75 last quarter. Returns JDE (Dynamical Time)."""
    t = k / 1236.85
    jde = (2451550.09766 + SYNODIC * k + 0.00015437 * t**2
           - 0.000000150 * t**3 + 0.00000000073 * t**4)
    e = 1 - 0.002516 * t - 0.0000074 * t**2
    m = 2.5534 + 29.10535670 * k - 0.0000014 * t**2 - 0.00000011 * t**3
    mp = (201.5643 + 385.81693528 * k + 0.0107582 * t**2
          + 0.00001238 * t**3 - 0.000000058 * t**4)
    f = (160.7108 + 390.67050284 * k - 0.0016118 * t**2
         - 0.00000227 * t**3 + 0.000000011 * t**4)
    om = 124.7746 - 1.56375588 * k + 0.0020672 * t**2 + 0.00000215 * t**3
    frac = round((k - math.floor(k)) * 4) % 4

    if frac in (0, 2):
        new = frac == 0
        c = ((-0.40720 if new else -0.40614) * _sin(mp)
             + (0.17241 if new else 0.17302) * e * _sin(m)
             + (0.01608 if new else 0.01614) * _sin(2 * mp)
             + (0.01039 if new else 0.01043) * _sin(2 * f)
             + (0.00739 if new else 0.00734) * e * _sin(mp - m)
             - (0.00514 if new else 0.00515) * e * _sin(mp + m)
             + (0.00208 if new else 0.00209) * e * e * _sin(2 * m)
             - 0.00111 * _sin(mp - 2 * f)
             - 0.00057 * _sin(mp + 2 * f)
             + 0.00056 * e * _sin(2 * mp + m)
             - 0.00042 * _sin(3 * mp)
             + 0.00042 * e * _sin(m + 2 * f)
             + 0.00038 * e * _sin(m - 2 * f)
             - 0.00024 * e * _sin(2 * mp - m)
             - 0.00017 * _sin(om)
             - 0.00007 * _sin(mp + 2 * m)
             + 0.00004 * _sin(2 * mp - 2 * f)
             + 0.00004 * _sin(3 * m)
             + 0.00003 * _sin(mp + m - 2 * f)
             + 0.00003 * _sin(2 * mp + 2 * f)
             - 0.00003 * _sin(mp + m + 2 * f)
             + 0.00003 * _sin(mp - m + 2 * f)
             - 0.00002 * _sin(mp - m - 2 * f)
             - 0.00002 * _sin(3 * mp + m)
             + 0.00002 * _sin(4 * mp))
    else:
        c = (-0.62801 * _sin(mp)
             + 0.17172 * e * _sin(m)
             - 0.01183 * e * _sin(mp + m)
             + 0.00862 * _sin(2 * mp)
             + 0.00804 * _sin(2 * f)
             + 0.00454 * e * _sin(mp - m)
             + 0.00204 * e * e * _sin(2 * m)
             - 0.00180 * _sin(mp - 2 * f)
             - 0.00070 * _sin(mp + 2 * f)
             - 0.00040 * _sin(3 * mp)
             - 0.00034 * e * _sin(2 * mp - m)
             + 0.00032 * e * _sin(m + 2 * f)
             + 0.00032 * e * _sin(m - 2 * f)
             - 0.00028 * e * e * _sin(mp + 2 * m)
             + 0.00027 * e * _sin(2 * mp + m)
             - 0.00017 * _sin(om)
             - 0.00005 * _sin(mp - m - 2 * f)
             + 0.00004 * _sin(2 * mp + 2 * f)
             - 0.00004 * _sin(mp + m + 2 * f)
             + 0.00004 * _sin(mp - 2 * m)
             + 0.00003 * _sin(mp + m - 2 * f)
             + 0.00003 * _sin(3 * m)
             + 0.00002 * _sin(2 * mp - 2 * f)
             + 0.00002 * _sin(mp - m + 2 * f)
             - 0.00002 * _sin(3 * mp + m))
        w = (0.00306 - 0.00038 * e * _cos(m) + 0.00026 * _cos(mp)
             - 0.00002 * _cos(mp - m) + 0.00002 * _cos(mp + m) + 0.00002 * _cos(2 * f))
        c += w if frac == 1 else -w

    planetary = (
        (0.000325, 299.77 + 0.107408 * k - 0.009173 * t**2),
        (0.000165, 251.88 + 0.016321 * k), (0.000164, 251.83 + 26.651886 * k),
        (0.000126, 349.42 + 36.412478 * k), (0.000110, 84.66 + 18.206239 * k),
        (0.000062, 141.74 + 53.303771 * k), (0.000060, 207.14 + 2.453732 * k),
        (0.000056, 154.84 + 7.306860 * k), (0.000047, 34.52 + 27.261239 * k),
        (0.000042, 207.19 + 0.121824 * k), (0.000040, 291.34 + 1.844379 * k),
        (0.000037, 161.72 + 24.198154 * k), (0.000035, 239.56 + 25.513099 * k),
        (0.000023, 331.55 + 3.592518 * k),
    )
    return jde + c + sum(a * _sin(arg) for a, arg in planetary)


def _jde_to_ut(jde: float) -> datetime:
    dt = jd_to_datetime(jde)
    return dt - timedelta(seconds=delta_t_seconds(dt.year + dt.timetuple().tm_yday / 365.25))


def phases_between(start: datetime, end: datetime) -> list[tuple[str, datetime]]:
    """Every principal phase with start <= time < end, as (name, UTC datetime)."""
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    years = start.year + (start.timetuple().tm_yday - 1) / 365.25 - 2000
    k = math.floor(years * 12.3685) - 1
    out: list[tuple[str, datetime]] = []
    while True:
        for q in range(4):
            when = _jde_to_ut(_phase_jde(k + q / 4))
            if when >= end:
                return out
            if when >= start:
                out.append((PHASE_NAMES[q], when))
        k += 1


def new_moon_jd(k: int) -> float:
    return datetime_to_jd(_jde_to_ut(_phase_jde(float(k))))


def moon_age(when: datetime) -> float:
    """Fraction of the lunation since the last new moon: 0 new, 0.5 full, toward 1 dark."""
    jd = datetime_to_jd(when)
    k = math.floor((jd - 2451550.09766) / SYNODIC)
    while new_moon_jd(k) > jd:
        k -= 1
    while new_moon_jd(k + 1) <= jd:
        k += 1
    nm, nxt = new_moon_jd(k), new_moon_jd(k + 1)
    return (jd - nm) / (nxt - nm)


def illumination(age: float) -> float:
    return (1 - math.cos(2 * math.pi * age)) / 2


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def waning_window(now: datetime) -> dict:
    """The waning moon runs from a full moon to the next new moon.

    Returns {"now": bool, "full": datetime, "new": datetime} in UTC. When `now` sits inside a
    waning stretch, "now" is True and the window is the current one. Otherwise it is the next one.
    """
    now = _aware(now)
    found = phases_between(now - timedelta(days=32), now + timedelta(days=64))
    fulls = [t for name, t in found if name == "full moon"]
    news = [t for name, t in found if name == "new moon"]
    for full in fulls:
        new = next((t for t in news if t > full), None)
        if new is None:
            continue
        if full <= now < new:
            return {"now": True, "full": full, "new": new}
        if full > now:
            return {"now": False, "full": full, "new": new}
    raise RuntimeError("no waning window found in the next two months")


def phase_name(age: float) -> str:
    names = ("new moon", "waxing crescent", "first quarter", "waxing gibbous",
             "full moon", "waning gibbous", "last quarter", "waning crescent")
    return names[int(age * 8 + 0.5) % 8]
