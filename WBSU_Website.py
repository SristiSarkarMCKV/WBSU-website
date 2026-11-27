import base64
import io
import mimetypes
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="WBSU Alumni Association — Zoology",
    page_icon="🦋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- 1. REPO & FILE PATHS ---
BASE_DIR = Path(__file__).resolve().parent
IMAGES_ZIP_DIR = BASE_DIR / "Images"
EXTRACTED_IMG_DIR = BASE_DIR / "extracted_images"
PDF_DIR = BASE_DIR / "pdfs"

ZIP_FILENAMES = [
    "WhatsApp Unknown 2026-11-18 at 13.03.39.zip",
    "WhatsApp Unknown 2026-11-18 at 13.03.45.zip",
    "WhatsApp Unknown 2026-11-18 at 13.03.49.zip",
]

GITHUB_RAW_ZIP_BASE = "https://raw.githubusercontent.com/SristiSarkarMCKV/WBSU-website/main/Images"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# --- 2. SKY-BLUE LIGHT TINT <-> RECIPROCAL DARK TINT + OVERLAY MENU ---
st.markdown(
    """
    <style>
        :root {
            /* Light Mode: Sky Blue Tint */
            --bg-gradient: linear-gradient(160deg, #cfe8ff 0%, #e6f3ff 52%, #d6ecff 100%);
            --card-bg: rgba(242, 250, 255, 0.94);
            --card-border: #8ec5f5;
            --contact-bg: rgba(196, 228, 255, 0.96);
            --contact-border: #4d9de0;
            --contact-accent: #0b4a82;
            --text-main: #0b2540;
            --text-muted: #2d567d;
            --accent: #1464b8;
            --accent-soft: #cde6ff;
            --menu-btn-bg: #0f4c81;
            --menu-btn-hover: #1866ab;
            --menu-btn-text: #ffffff;
            --overlay-bg: rgba(235, 247, 255, 0.98);
            --banner-grad: linear-gradient(120deg, #0c3561 0%, #165696 58%, #2074c4 100%);
            --shadow-soft: 0 8px 24px rgba(11, 37, 64, 0.10);
        }

        @media (prefers-color-scheme: dark) {
            :root {
                /* Dark Mode: Reciprocal Deep Midnight Blue Tint */
                --bg-gradient: linear-gradient(160deg, #061324 0%, #0a1e36 52%, #071629 100%);
                --card-bg: rgba(12, 31, 54, 0.95);
                --card-border: #28578a;
                --contact-bg: rgba(16, 44, 74, 0.96);
                --contact-border: #3d7ec2;
                --contact-accent: #82c7ff;
                --text-main: #e8f4ff;
                --text-muted: #a6c9eb;
                --accent: #63b3ff;
                --accent-soft: #17385e;
                --menu-btn-bg: #1b5694;
                --menu-btn-hover: #286eb8;
                --menu-btn-text: #ffffff;
                --overlay-bg: rgba(10, 27, 48, 0.98);
                --banner-grad: linear-gradient(120deg, #051120 0%, #0d2b4d 58%, #154170 100%);
                --shadow-soft: 0 10px 28px rgba(0, 0, 0, 0.45);
            }
        }

        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"] {
            background: var(--bg-gradient) !important;
            color: var(--text-main) !important;
        }

        .stApp,
        .stApp p,
        .stApp span,
        .stApp div,
        .stApp label,
        .stApp li,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] * {
            color: var(--text-main);
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--text-main) !important;
        }

        /* Compact top-right MENU button with 10px padding and crisp visible text */
        .st-key-menu_toggle_btn {
            position: fixed !important;
            top: 16px !important;
            right: 22px !important;
            z-index: 10000 !important;
            width: auto !important;
        }

        .st-key-menu_toggle_btn button,
        .st-key-menu_toggle_btn button *,
        div[data-testid="stButton"] > button[kind="secondary"] {
            background-color: var(--menu-btn-bg) !important;
            color: var(--menu-btn-text) !important;
            border: 1.5px solid var(--card-border) !important;
            border-radius: 10px !important;
            padding: 10px !important;
            font-size: 0.85rem !important;
            font-weight: 800 !important;
            line-height: 1 !important;
            min-height: 0 !important;
            height: auto !important;
            width: auto !important;
            box-shadow: var(--shadow-soft) !important;
            cursor: pointer !important;
        }

        .st-key-menu_toggle_btn button:hover {
            background-color: var(--menu-btn-hover) !important;
            color: var(--menu-btn-text) !important;
        }

        /* Floating overlay panel over current page content when expanded */
        .st-key-menu_overlay_container {
            position: fixed !important;
            top: 62px !important;
            right: 22px !important;
            width: 245px !important;
            z-index: 9999 !important;
            background: var(--overlay-bg) !important;
            border: 1.5px solid var(--card-border) !important;
            border-radius: 14px !important;
            padding: 14px 16px !important;
            box-shadow: 0 14px 34px rgba(0, 0, 0, 0.28) !important;
        }

        .st-key-menu_overlay_container label,
        .st-key-menu_overlay_container span,
        .st-key-menu_overlay_container p {
            color: var(--text-main) !important;
        }

        /* Zoology & Auto-Scroll Animations */
        @keyframes floatSpecimen {
            0%, 100% {
                transform: translateY(0px) rotate(0deg);
            }
            50% {
                transform: translateY(-7px) rotate(2.5deg);
            }
        }

        @keyframes pulseRipple {
            0%, 100% {
                transform: scale(1);
                opacity: 0.75;
            }
            50% {
                transform: scale(1.06);
                opacity: 1;
            }
        }

        @keyframes fadeSlideUp {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes scrollAcrossScreen {
            0% {
                transform: translateX(0%);
            }
            100% {
                transform: translateX(-50%);
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .zoo-float, .zoo-pulse, .blue-card, .contact-card, .top-nav-banner, .auto-scroll-track {
                animation: none !important;
                transition: none !important;
            }
        }

        .zoo-float {
            animation: floatSpecimen 5.5s ease-in-out infinite;
            display: inline-block;
        }

        .zoo-pulse {
            animation: pulseRipple 3.8s ease-in-out infinite;
        }

        .top-nav-banner {
            background: var(--banner-grad) !important;
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 18px 24px;
            margin-bottom: 18px;
            box-shadow: var(--shadow-soft);
            animation: fadeSlideUp 0.55s ease-out both;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }

        .top-nav-banner h2,
        .top-nav-banner p,
        .top-nav-banner span {
            color: #f4faff !important;
            margin: 0;
        }

        .auto-scroll-wrapper {
            width: 100%;
            overflow: hidden;
            border-radius: 16px;
            border: 1px solid var(--card-border);
            background-color: var(--card-bg) !important;
            box-shadow: var(--shadow-soft);
            padding: 14px 0;
            margin-bottom: 16px;
        }

        .auto-scroll-track {
            display: flex;
            width: max-content;
            gap: 16px;
            animation-name: scrollAcrossScreen;
            animation-timing-function: linear;
            animation-iteration-count: infinite;
        }

        .auto-scroll-wrapper:hover .auto-scroll-track {
            animation-play-state: paused;
        }

        .scroll-slide-card {
            flex: 0 0 auto;
            width: 310px;
            height: 215px;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--card-border);
            background: var(--accent-soft);
        }

        .scroll-slide-card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }

        .blue-card {
            background-color: var(--card-bg) !important;
            border: 1px solid var(--card-border);
            border-left: 4px solid var(--accent);
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 14px;
            color: var(--text-main) !important;
            box-shadow: var(--shadow-soft);
            transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
            animation: fadeSlideUp 0.45s ease-out both;
        }

        .blue-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent);
        }

        .blue-card h3,
        .blue-card strong,
        .blue-card p {
            color: var(--text-main) !important;
            line-height: 1.65;
        }

        .blue-card p {
            margin-bottom: 0;
        }

        /* Distinct colour styling for the Contact section */
        .contact-card {
            background-color: var(--contact-bg) !important;
            border: 1.5px solid var(--contact-border);
            border-top: 5px solid var(--contact-accent);
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 14px;
            color: var(--text-main) !important;
            box-shadow: var(--shadow-soft);
            transition: transform 0.25s ease, border-color 0.25s ease;
            animation: fadeSlideUp 0.45s ease-out both;
        }

        .contact-card:hover {
            transform: translateY(-3px);
            border-color: var(--contact-accent);
        }

        .contact-title {
            color: var(--contact-accent) !important;
            font-weight: 800;
            font-size: 1.02rem;
            display: block;
            margin-bottom: 6px;
        }

        .muted-text {
            color: var(--text-muted) !important;
            font-size: 0.92rem;
        }

        .role-badge {
            display: inline-block;
            background-color: var(--accent-soft) !important;
            color: var(--accent) !important;
            font-weight: 700;
            font-size: 0.76rem;
            letter-spacing: 0.03em;
            padding: 4px 10px;
            border-radius: 999px;
            margin-bottom: 8px;
            border: 1px solid var(--card-border);
        }

        .zoo-divider {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 22px 0 14px 0;
        }

        .zoo-divider::before,
        .zoo-divider::after {
            content: "";
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--card-border), transparent);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 3. ZOOLOGY SVG GRAPHICS ---
ZOOLOGY_HEADER_SVG = """
<svg width="92" height="64" viewBox="0 0 92 64" fill="none" xmlns="http://www.w3.org/2000/svg" class="zoo-float" aria-label="Zoology emblem">
  <path d="M46 32C36 16 14 10 10 24C7 34 22 40 46 32Z" fill="#7CC4FA" fill-opacity="0.35" stroke="#BDE0FE" stroke-width="2"/>
  <path d="M46 32C56 16 78 10 82 24C85 34 70 40 46 32Z" fill="#7CC4FA" fill-opacity="0.35" stroke="#BDE0FE" stroke-width="2"/>
  <path d="M46 32C34 34 20 44 26 53C31 60 42 48 46 32Z" fill="#4EA8DE" fill-opacity="0.4" stroke="#90E0EF" stroke-width="2"/>
  <path d="M46 32C58 34 72 44 66 53C61 60 50 48 46 32Z" fill="#4EA8DE" fill-opacity="0.4" stroke="#90E0EF" stroke-width="2"/>
  <line x1="46" y1="15" x2="46" y2="52" stroke="#E6F1FC" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M46 16C42 10 37 8 34 9" stroke="#E6F1FC" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M46 16C50 10 55 8 58 9" stroke="#E6F1FC" stroke-width="1.8" stroke-linecap="round"/>
  <circle cx="24" cy="25" r="3.5" fill="#E6F1FC" fill-opacity="0.75"/>
  <circle cx="68" cy="25" r="3.5" fill="#E6F1FC" fill-opacity="0.75"/>
</svg>
"""

ZOOLOGY_RIBBON_SVG = """
<div style="display:flex; justify-content:center; align-items:center; gap:18px; padding:6px 0;">
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg" class="zoo-pulse">
    <circle cx="14" cy="14" r="10" stroke="currentColor" stroke-width="1.6" stroke-dasharray="3 3"/>
    <circle cx="14" cy="14" r="4" fill="currentColor"/>
  </svg>
  <svg width="160" height="26" viewBox="0 0 160 26" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M4 13C24 2 44 24 64 13C84 2 104 24 124 13C136 6 146 10 156 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" opacity="0.75"/>
    <path d="M4 13C24 24 44 2 64 13C84 24 104 2 124 13C136 20 146 16 156 13" stroke="currentColor" stroke-width="1.6" stroke-dasharray="4 3" stroke-linecap="round" opacity="0.55"/>
  </svg>
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg" class="zoo-float">
    <path d="M6 16C10 9 18 9 22 16C18 21 10 21 6 16Z" stroke="currentColor" stroke-width="1.6"/>
    <circle cx="14" cy="15" r="2.5" fill="currentColor"/>
  </svg>
</div>
"""


def render_zoo_divider(label: str):
    st.markdown(
        f"""
        <div class="zoo-divider">
            <span class="role-badge" style="margin:0;">🔬 {label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- 4. ZIP EXTRACTION & SLOW AUTO-SCROLL STRIP ---
@st.cache_data(show_spinner="Extracting images from ZIP archives...")
def extract_all_zip_images(zip_names: list[str], use_github_fallback: bool = True) -> list[str]:
    EXTRACTED_IMG_DIR.mkdir(parents=True, exist_ok=True)
    found_images: list[str] = []

    for zname in zip_names:
        zip_bytes: bytes | None = None
        local_candidate = IMAGES_ZIP_DIR / zname
        if local_candidate.exists():
            zip_bytes = local_candidate.read_bytes()
        elif use_github_fallback:
            encoded_name = urllib.parse.quote(zname)
            url = f"{GITHUB_RAW_ZIP_BASE}/{encoded_name}"
            try:
                with urllib.request.urlopen(url, timeout=15) as resp:
                    zip_bytes = resp.read()
            except Exception:
                zip_bytes = None

        if not zip_bytes:
            continue

        safe_prefix = zname.replace(".zip", "").replace(" ", "_").replace(":", "-")
        target_subdir = EXTRACTED_IMG_DIR / safe_prefix
        target_subdir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
            for member in zf.infolist():
                if member.is_dir():
                    continue
                if Path(member.filename).suffix.lower() in IMAGE_EXTENSIONS:
                    clean_name = Path(member.filename).name
                    if clean_name.startswith("._"):
                        continue
                    out_path = target_subdir / clean_name
                    with zf.open(member) as src, open(out_path, "wb") as dst:
                        dst.write(src.read())
                    found_images.append(str(out_path))

    return sorted(found_images)


def _image_to_data_uri(img_path: str) -> str | None:
    p = Path(img_path)
    if not p.exists():
        return None
    mime_type, _ = mimetypes.guess_type(p.name)
    if not mime_type:
        mime_type = "image/jpeg"
    encoded = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def render_auto_scrolling_gallery(image_paths: list[str], seconds_per_image: float = 3.6):
    valid_uris = []
    for path in image_paths:
        uri = _image_to_data_uri(path)
        if uri:
            valid_uris.append((uri, Path(path).name))

    if not valid_uris:
        st.info("No images extracted yet. Keep the ZIP files inside `Images/` or push them to GitHub `Images/`.")
        return

    total_duration_sec = max(len(valid_uris) * seconds_per_image, 12.0)
    loop_items = valid_uris + valid_uris
    cards_html = "".join(
        f'<div class="scroll-slide-card"><img src="{uri}" alt="{name}" title="{name}"/></div>'
        for uri, name in loop_items
    )

    st.markdown(
        f"""
        <div class="auto-scroll-wrapper" aria-label="Slow auto-scrolling gallery from ZIP archives">
            <div class="auto-scroll-track" style="animation-duration: {total_duration_sec:.1f}s;">
                {cards_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- 5. WEBSITE DATA ---
COMMITTEE_MEMBERS = [
    {"role": "President", "name": "Dr. Anirban Sen", "email": "president@alumniassoc.org"},
    {"role": "Vice President", "name": "Smt. Gargi Mukherjee", "email": "vp@alumniassoc.org"},
    {"role": "General Secretary", "name": "Sri Sourav Chatterjee", "email": "gs@alumniassoc.org"},
    {"role": "Treasurer", "name": "Sri Debashis Roy", "email": "treasurer@alumniassoc.org"},
]

ALUMNI_PDFS = [
    {"year": "Batch of 2020", "file": PDF_DIR / "alumni_2020.pdf"},
    {"year": "Batch of 2021", "file": PDF_DIR / "alumni_2021.pdf"},
    {"year": "Batch of 2022", "file": PDF_DIR / "alumni_2022.pdf"},
    {"year": "Batch of 2023", "file": PDF_DIR / "alumni_2023.pdf"},
]

NOTABLE_ALUMNI = [
    {"name": "Subhojit Das", "position": "Senior Scientist, ISRO", "email": "subhojit.das@example.com"},
    {"name": "Riya Chakraborty", "position": "IAS Officer, Govt. of West Bengal", "email": "riya.ias@example.com"},
    {"name": "Kaushik Bose", "position": "VP of Engineering, Google", "email": "kaushik.b@example.com"},
]

EVENTS_DATA = [
    {
        "title": "Annual Alumni Seminar & Guest Lectures",
        "description": (
            "Our annual seminar bridges the gap between current students and industry veterans. "
            "Through interactive sessions, former students share insights on emerging technologies, "
            "career pathways, and research opportunities. These lectures inspire young minds to aim higher "
            "and prepare for real-world challenges. It fosters a culture of continuous learning and mentorship "
            "within our academic community, helping students build strong professional networks early on."
        ),
    },
    {
        "title": "Grand Alumni Reunion",
        "description": (
            "The Grand Reunion is a celebration of lifelong friendships, shared memories, and institutional pride. "
            "Graduates from different decades return to campus to reconnect with old batchmates and beloved faculty members. "
            "Beyond nostalgia, this gathering strengthens our alumni network and creates opportunities for collaborative "
            "initiatives. It reminds every member that no matter where life takes them, their alma mater remains "
            "a permanent home and a pillar of support."
        ),
    },
    {
        "title": "Green Campus Plantation Drive",
        "description": (
            "Committed to environmental sustainability, our alumni regularly organize tree plantation drives across "
            "the campus and surrounding locality. Climate change demands collective action, and this initiative instills "
            "ecological responsibility among both students and former graduates. By nurturing green spaces today, "
            "we ensure a cleaner, healthier environment for future generations. Each sapling planted stands as a "
            "living symbol of our enduring bond with the institution."
        ),
    },
]

BANK_DETAILS = {
    "Account Name": "XYZ College Alumni Association",
    "Bank Name": "State Bank of India (SBI)",
    "Branch": "Khardaha Branch, West Bengal",
    "Account Number": "123456789012",
    "IFSC Code": "SBIN0001234",
    "UPI ID": "alumniassoc@sbi",
}

CONTACT_INFO = {
    "address": "123 College Road, Campus Building, Kolkata - 700117, West Bengal",
    "phone": "+91 98765 43210",
    "email": "contact@alumniassoc.org",
}

# --- 6. TOP-RIGHT OVERLAY MENU TOGGLE ---
if "menu_expanded" not in st.session_state:
    st.session_state.menu_expanded = False

if "current_page" not in st.session_state:
    st.session_state.current_page = "Cover Page"

btn_label = "MENU>" if st.session_state.menu_expanded else "<MENU "
if st.button(btn_label, key="menu_toggle_btn"):
    st.session_state.menu_expanded = not st.session_state.menu_expanded
    st.rerun()

if st.session_state.menu_expanded:
    with st.container(key="menu_overlay_container"):
        st.markdown("**Navigation**")
        selected_page = st.radio(
            "Go to",
            ["Cover Page", "Alumni Corner", "Events", "Support Us"],
            index=["Cover Page", "Alumni Corner", "Events", "Support Us"].index(st.session_state.current_page),
            key="top_right_nav_radio",
        )
        if selected_page != st.session_state.current_page:
            st.session_state.current_page = selected_page
            st.rerun()

page = st.session_state.current_page

# --- 7. BANNER & FOOTER ---
st.markdown(
    f"""
    <div class="top-nav-banner">
        <div>
            <h2>🐾 WBSU Zoology Alumni Association</h2>
            <p>Exploring Biodiversity • Mentorship &amp; Research • Giving Back to Our Alma Mater</p>
        </div>
        <div>{ZOOLOGY_HEADER_SVG}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

all_extracted_imgs = extract_all_zip_images(ZIP_FILENAMES, use_github_fallback=True)


def render_footer():
    st.markdown(ZOOLOGY_RIBBON_SVG, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            '<div class="contact-card">'
            '<span class="contact-title">Zoology Alumni Association</span>'
            '<span class="muted-text">Uniting past, present, and future generations of naturalists &amp; scholars.</span>'
            "</div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="contact-card">'
            f'<span class="contact-title">Address</span>'
            f'<span class="muted-text">{CONTACT_INFO["address"]}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="contact-card">'
            f'<span class="contact-title">Contact</span>'
            f'<span class="muted-text">Email: {CONTACT_INFO["email"]}<br>'
            f'Phone: {CONTACT_INFO["phone"]}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )


# --- 8. PAGES ---
if page == "Cover Page":
    render_zoo_divider("Live ZIP Gallery Auto-Scroll")
    render_auto_scrolling_gallery(all_extracted_imgs, seconds_per_image=3.6)

    render_zoo_divider("Who Are We & Our Vision")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            <div class="blue-card">
                <h3>Who Are We?</h3>
                <p>We are a registered body of former students dedicated to maintaining a lifelong bond
                between the institution and its graduates. Our association connects batches across years,
                bringing together researchers, conservationists, educators, and leaders on one platform.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="blue-card">
                <h3>Our Vision</h3>
                <p>Our vision is to build a vibrant, supportive alumni community that actively contributes
                to student welfare, zoological research excellence, biodiversity awareness, and social impact
                through mentorship, scholarships, and collaborative initiatives.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_zoo_divider("Who's Who")
    cols = st.columns(4)
    for idx, member in enumerate(COMMITTEE_MEMBERS):
        with cols[idx % 4]:
            st.markdown(
                f"""
                <div class="blue-card">
                    <span class="role-badge">{member["role"]}</span><br>
                    <strong>{member["name"]}</strong><br>
                    <span class="muted-text">{member["email"]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    render_footer()

elif page == "Alumni Corner":
    st.header("Alumni Corner")

    render_zoo_divider("Notable Alumni")
    n_cols = st.columns(3)
    for idx, alum in enumerate(NOTABLE_ALUMNI):
        with n_cols[idx % 3]:
            st.markdown(
                f"""
                <div class="blue-card">
                    <span class="role-badge">Distinguished Alumnus/Alumna</span><br>
                    <strong>{alum["name"]}</strong><br>
                    <span>{alum["position"]}</span><br>
                    <span class="muted-text">{alum["email"]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    render_zoo_divider("Year-by-Year Alumni Directory (PDF)")
    p_cols = st.columns(2)
    for idx, item in enumerate(ALUMNI_PDFS):
        pdf_path: Path = item["file"]
        with p_cols[idx % 2]:
            st.markdown(
                f'<div class="blue-card"><strong>{item["year"]}</strong><br>'
                f'<span class="muted-text">Student Names &amp; Email IDs</span></div>',
                unsafe_allow_html=True,
            )
            if pdf_path.exists():
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label=f"Download {item['year']} PDF",
                        data=f.read(),
                        file_name=pdf_path.name,
                        mime="application/pdf",
                        key=f"dl_{idx}",
                    )
            else:
                st.caption(f"Add `{pdf_path.relative_to(BASE_DIR)}` to enable download.")

    render_footer()

elif page == "Events":
    st.header("Our Events & Initiatives")
    for idx, event in enumerate(EVENTS_DATA):
        render_zoo_divider(f"Initiative {idx + 1}")
        st.markdown(
            f"""
            <div class="blue-card">
                <h3>{event["title"]}</h3>
                <p>{event["description"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_footer()

elif page == "Support Us":
    st.header("Support Us")
    st.markdown(
        """
        <div class="blue-card">
            <p>Your generous contributions help fund student scholarships, zoological field seminars,
            ecological initiatives, and campus welfare programmes.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_zoo_divider("Official Bank Account Details")
    for k, v in BANK_DETAILS.items():
        l, r = st.columns([1, 2])
        l.markdown(f"**{k}**")
        r.code(v, language=None)

    render_footer()
