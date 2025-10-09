from datetime import datetime
from .types import RitualContext
from services.i18n.loader import t
from services.astro.moon import phase_name, illumination

def _anchor_line(ctx: RitualContext) -> str:
    m = ctx.market
    lang = (ctx.extra or {}).get("lang")
    if m is None or m.price is None or m.change_24h_pct is None or m.volume_24h is None:
        return f"{ctx.chat_token}: {t('fallback.data_unavailable','data unavailable', lang=lang)}"
    sign = "▲" if m.change_24h_pct >= 0 else "▼"
    return f"{ctx.chat_token}: {m.price:.4f} {sign}{m.change_24h_pct:.2f}% · 24h vol {m.volume_24h:,.0f}"

def _moon_line(ctx: RitualContext) -> str:
    ex = ctx.extra or {}
    if not ex.get("show_moon", False):
        return ""
    lang = ex.get("lang")
    try:
        dt = datetime.now()
        name = phase_name(dt)
        pct = illumination(dt)
        label = t('labels.moon','Moon', lang=lang)
        return f"\n🌙 {label}: {name} ({pct}%)"
    except Exception:
        return ""

def template_pre_roll(ctx: RitualContext) -> str:
    ex = ctx.extra or {}
    lang = ex.get("lang")
    sep = t("labels.hub_sep","|", lang=lang)
    anchor = _anchor_line(ctx)
    body = (
        f"⏳ {t('labels.pre_roll','Pre-Roll', lang=lang)} {sep} {ctx.hub.name} {sep} {ctx.ritual_dt_iso}\n"
        f"{anchor}\n"
        f"{t('phrases.navigator','Navigator warm-up: breathe, prep, set intention. 🌊🌿', lang=lang)}"
    )
    body += _moon_line(ctx)
    return body

def template_holy_minute(ctx: RitualContext) -> str:
    ex = ctx.extra or {}
    lang = ex.get("lang")
    sep = t("labels.hub_sep","|", lang=lang)
    anchor = _anchor_line(ctx)
    body = (
        f"🔥 {t('labels.holy_minute','Holy Minute', lang=lang)} {sep} {ctx.hub.name} {sep} {ctx.ritual_dt_iso}\n"
        f"{anchor}\n"
        f"{t('quotes.service_first','\"O le ala i le pule o le tautua.\" Service first.', lang=lang)} "
        f"{t('phrases.bongterm','We are Bongterm 🌱', lang=lang)}"
    )
    body += _moon_line(ctx)
    return body
