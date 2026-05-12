import requests
import os
import base64

def get_discord_status():
    user_id = "687315513021562892"
    url = f"https://api.lanyard.rest/v1/users/{user_id}"
    try:
        response = requests.get(url)
        data = response.json()
        if data["success"]:
            return data["data"]
    except Exception as e:
        print(f"Error fetching data: {e}")
    return None

def get_image_base64(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
    except:
        pass
    return None

def truncate(text, max_len=40):
    return text if len(text) <= max_len else text[:max_len - 1] + "…"

# ── README Theme Palette ─────────────────────────────────────
# capsule-render header:  #ff69b4  (hot pink)
# capsule-render sub:     #ffb6c1  (light pink)
# table border/bg:        #ff69b4 with ~50% opacity
# text on dark:           #ffffff
# ────────────────────────────────────────────────────────────
BG_DARK   = "#0d1117"   # GitHub dark bg
BG_CARD   = "#161b22"   # GitHub card bg
PRIMARY   = "#ff69b4"   # Hot pink (main)
LIGHT     = "#ffb6c1"   # Light pink (sub)
WHITE     = "#ffffff"   # Primary text
SUBTEXT   = "#ffb6c1"   # Sub text (same as light pink)
SPOTIFY   = "#1DB954"
# ────────────────────────────────────────────────────────────

def generate_svg(data):
    if not data:
        return ""

    status = data["discord_status"]
    user   = data["discord_user"]
    username    = user["global_name"] or user["username"]
    user_id     = user["id"]
    avatar_hash = user["avatar"]

    status_colors = {
        "online":  "#43b581",
        "idle":    "#faa61a",
        "dnd":     "#f04747",
        "offline": "#747f8d"
    }
    dot_color = status_colors.get(status, "#747f8d")

    avatar_url    = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png?size=128"
    avatar_base64 = get_image_base64(avatar_url)

    custom_status = ""
    for act in data.get("activities", []):
        if act.get("id") == "custom":
            custom_status = act.get("state", "")
            break

    display_activities = []

    if data.get("listening_to_spotify"):
        s = data["spotify"]
        album_art_b64 = get_image_base64(s["album_art_url"])
        display_activities.append({
            "kind": "spotify", "name": "Spotify",
            "details": truncate(s["song"]),
            "state":   truncate(f"by {s['artist']}"),
            "image":   album_art_b64,
        })

    for act in data.get("activities", []):
        if act["type"] == 0:
            display_activities.append({
                "kind":    "game",
                "name":    truncate(act["name"]),
                "details": truncate(act.get("details", "")),
                "state":   truncate(act.get("state", "")),
            })

    if not display_activities:
        display_activities.append({
            "kind": "idle", "name": "Napping…",
            "details": "Uhee~ Senior is sleeping", "state": "",
        })

    display_activities = display_activities[:2]

    W         = 480
    AVT_R     = 40
    AVT_CX    = 55
    AVT_CY    = 55
    HEADER_H  = 110
    BOX_H     = 62
    BOX_GAP   = 8
    BOX_TOP   = 12
    PAD       = 12

    total_h = HEADER_H + BOX_TOP + len(display_activities) * (BOX_H + BOX_GAP) + 12

    # ── Activity boxes ─────────────────────────────────────
    activities_svg = ""
    for i, act in enumerate(display_activities):
        bx = PAD
        by = HEADER_H + BOX_TOP + i * (BOX_H + BOX_GAP)
        bw = W - PAD * 2

        if act["kind"] == "spotify" and act.get("image"):
            inner = f"""
            <rect x="10" y="10" width="42" height="42" rx="8" fill="{BG_DARK}" opacity="0.6"/>
            <image href="data:image/png;base64,{act['image']}" x="10" y="10" width="42" height="42" clip-path="inset(0% round 8px)"/>
            <text x="62" y="26" font-family="Segoe UI,sans-serif" font-size="13" font-weight="bold" fill="{SPOTIFY}">🎵 {act['name']}</text>
            <text x="62" y="43" font-family="Segoe UI,sans-serif" font-size="11" fill="{WHITE}">{act['details']}</text>
            <text x="62" y="56" font-family="Segoe UI,sans-serif" font-size="10" fill="{SUBTEXT}">{act['state']}</text>
            """
        elif act["kind"] == "game":
            inner = f"""
            <text x="14" y="24" font-family="Segoe UI,sans-serif" font-size="13" font-weight="bold" fill="{PRIMARY}">🎮 {act['name']}</text>
            <text x="14" y="41" font-family="Segoe UI,sans-serif" font-size="11" fill="{WHITE}">{act['details']}</text>
            <text x="14" y="55" font-family="Segoe UI,sans-serif" font-size="10" fill="{SUBTEXT}">{act['state']}</text>
            """
        else:
            inner = f"""
            <text x="14" y="24" font-family="Segoe UI,sans-serif" font-size="13" font-weight="bold" fill="{PRIMARY}">😴 {act['name']}</text>
            <text x="14" y="42" font-family="Segoe UI,sans-serif" font-size="11" fill="{SUBTEXT}">{act['details']}</text>
            """

        activities_svg += f"""
        <g transform="translate({bx},{by})">
            <rect x="0" y="0" width="{bw}" height="{BOX_H}" rx="12"
                  fill="{PRIMARY}" fill-opacity="0.08"
                  stroke="{PRIMARY}" stroke-width="1.5" stroke-opacity="0.4"/>
            {inner}
        </g>"""

    # ── Decorative petals (matching README palette) ────────
    petals = f"""
    <text x="440" y="28"  font-size="14" fill="{LIGHT}" opacity="0.35">🌸</text>
    <text x="452" y="75"  font-size="10" fill="{LIGHT}" opacity="0.20">🌸</text>
    <text x="438" y="100" font-size="12" fill="{LIGHT}" opacity="0.15">🌸</text>
    """

    svg = f"""<svg width="{W}" height="{total_h}" viewBox="0 0 {W} {total_h}"
     fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"   stop-color="{BG_DARK}"/>
      <stop offset="100%" stop-color="{BG_CARD}"/>
    </linearGradient>
    <linearGradient id="headerGlow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   stop-color="{PRIMARY}" stop-opacity="0.20"/>
      <stop offset="100%" stop-color="{BG_DARK}"  stop-opacity="0"/>
    </linearGradient>
    <clipPath id="avatarClip">
      <circle cx="{AVT_CX}" cy="{AVT_CY}" r="{AVT_R}"/>
    </clipPath>
    <clipPath id="cardClip">
      <rect width="{W}" height="{total_h}" rx="20"/>
    </clipPath>
  </defs>

  <!-- Card background -->
  <rect width="{W}" height="{total_h}" rx="20"
        fill="url(#bgGrad)" stroke="{PRIMARY}" stroke-width="2"/>

  <!-- Header pink glow -->
  <rect x="0" y="0" width="{W}" height="{HEADER_H}"
        fill="url(#headerGlow)" clip-path="url(#cardClip)"/>

  <!-- Avatar ring — matches table border in README (#ff69b4) -->
  <circle cx="{AVT_CX}" cy="{AVT_CY}" r="{AVT_R + 5}"
          fill="{PRIMARY}" fill-opacity="0.15"/>
  <circle cx="{AVT_CX}" cy="{AVT_CY}" r="{AVT_R + 2}"
          fill="none" stroke="{PRIMARY}" stroke-width="2.5"/>
  <image href="data:image/png;base64,{avatar_base64 or ''}"
         x="{AVT_CX - AVT_R}" y="{AVT_CY - AVT_R}"
         width="{AVT_R * 2}" height="{AVT_R * 2}"
         clip-path="url(#avatarClip)"/>

  <!-- Status dot -->
  <circle cx="{AVT_CX + 29}" cy="{AVT_CY + 29}" r="9"  fill="{BG_DARK}"/>
  <circle cx="{AVT_CX + 29}" cy="{AVT_CY + 29}" r="6.5" fill="{dot_color}"/>

  <!-- Profile text — white + #ffb6c1 sub, matching README font style -->
  <text x="112" y="34" font-family="Segoe UI,sans-serif" font-size="21" font-weight="bold" fill="{WHITE}">{username}</text>
  <text x="112" y="53" font-family="Segoe UI,sans-serif" font-size="13" fill="{LIGHT}" opacity="0.85">@{user['username']}</text>
  <text x="112" y="73" font-family="Segoe UI,sans-serif" font-size="12" font-style="italic" fill="{PRIMARY}">"{truncate(custom_status, 42)}"</text>

  <!-- Status badge pill — #ff69b4 border like README table -->
  <rect x="112" y="80" width="68" height="18" rx="9"
        fill="{PRIMARY}" fill-opacity="0.20"
        stroke="{PRIMARY}" stroke-width="1.2"/>
  <text x="146" y="93" text-anchor="middle"
        font-family="Segoe UI,sans-serif" font-size="10" font-weight="bold" fill="{WHITE}">{status.upper()}</text>

  <!-- Divider — same #ff69b4 as README pink-divider.svg -->
  <line x1="{PAD}" y1="{HEADER_H}" x2="{W - PAD}" y2="{HEADER_H}"
        stroke="{PRIMARY}" stroke-width="1.5" stroke-opacity="0.3"/>

  {activities_svg}
  {petals}
</svg>"""
    return svg

def main():
    data = get_discord_status()
    svg_content = generate_svg(data)
    if svg_content:
        os.makedirs("Assets", exist_ok=True)
        with open("Assets/discord-presence.svg", "w", encoding="utf-8") as f:
            f.write(svg_content)
        print("Updated discord-presence.svg — synced with README theme ✿")

if __name__ == "__main__":
    main()
