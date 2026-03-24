import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from domain_recon import get_whois_info, get_dns_records, get_ip_address, get_ip_location, vpn_breaker
from social_recon import check_social_media, lookup_discord_id, search_real_name
from phone_recon import lookup_phone, check_account_existence, check_breaches, password_finder
from media_recon import get_exif_data
from PIL import Image
from fpdf import FPDF
import datetime

# --- PDF GENERATOR ---
def _safe_text(text, max_len=180):
    """Text auf latin-1 bereinigen, Sonderzeichen ersetzen und Länge begrenzen."""
    text = str(text)
    text = text.encode("latin-1", "replace").decode("latin-1")
    if len(text) > max_len:
        text = text[:max_len] + "..."
    return text

def create_pdf(report_data, title="OSINT Recherche Bericht"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt=_safe_text(title, 80), ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, txt=f"Erstellt am: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", ln=True, align="C")
    pdf.ln(10)
    for section, data in report_data.items():
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, txt=_safe_text(str(section).upper(), 80), ln=True)
        pdf.set_font("Arial", "", 9)
        if isinstance(data, dict):
            for k, v in data.items():
                line = _safe_text(f"{k}: {v}", 200)
                pdf.multi_cell(0, 7, txt=line)
        else:
            pdf.multi_cell(0, 7, txt=_safe_text(str(data), 500))
        pdf.ln(4)
    result = pdf.output(dest="S")
    if isinstance(result, bytes):
        return result
    return result.encode("latin-1", "replace")

# --- SEITEN KONFIGURATION ---
st.set_page_config(page_title="Full Data", page_icon="🔍", layout="wide")

# --- PASSWORTSCHUTZ ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if not st.session_state.password_correct:
        st.title("🔒 Zugriff geschützt")
        pwd = st.text_input("Passwort eingeben:", type="password")
        if st.button("Einloggen"):
            if pwd == "31nichoy":
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("Falsches Passwort!")
        return False
    return True

# --- MINDMAP ---
def render_mindmap():
    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0d1117;font-family:'Segoe UI',Arial,sans-serif;overflow:hidden}
#mm{width:100%;height:580px;position:relative}
svg{width:100%;height:100%}
.node circle{cursor:pointer;stroke-width:2px;transition:all .25s}
.node circle:hover{filter:brightness(1.5);stroke-width:3px}
.node text{font-size:13px;fill:#e6edf3;cursor:pointer;user-select:none;pointer-events:none}
.link{fill:none;stroke:#30363d;stroke-width:1.5px}
#tip{position:absolute;background:#161b22;border:1px solid #30363d;border-radius:8px;
     padding:9px 13px;color:#e6edf3;font-size:12px;pointer-events:none;opacity:0;
     transition:opacity .2s;max-width:240px;z-index:99}
#leg{position:absolute;bottom:8px;left:10px;color:#8b949e;font-size:11px;line-height:1.9}
</style></head>
<body>
<div id="mm"><div id="tip"></div>
<div id="leg">🖱 Klicken = Auf-/Zuklappen &nbsp;|&nbsp; Seitenleiste = Tool öffnen</div></div>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const data={name:"🔍 Full Data",color:"#58a6ff",children:[
  {name:"📱 Telefon & Nummer",color:"#3fb950",action:"phone",desc:"Telefonnummern analysieren",children:[
    {name:"Telefon-Lookup",color:"#3fb950",action:"phone",leaf:true,desc:"Carrier, Land, Leitungstyp"},
    {name:"WhatsApp prüfen",color:"#3fb950",leaf:true,url:"https://wa.me/",desc:"Manuell via wa.me prüfen"},
    {name:"Telegram prüfen",color:"#3fb950",leaf:true,desc:"In Telegram App suchen"},
    {name:"Standort (Vorwahl)",color:"#3fb950",action:"phone",leaf:true,desc:"Land & Region per Vorwahl"}
  ]},
  {name:"📧 E-Mail & Accounts",color:"#f78166",action:"email",desc:"E-Mail & Accounts untersuchen",children:[
    {name:"Account-Existenz",color:"#f78166",action:"email",leaf:true,desc:"Google, Apple u.a. prüfen"},
    {name:"Datenlecks",color:"#f78166",action:"email",leaf:true,desc:"Have I Been Pwned, DeHashed"},
    {name:"IntelligenceX",color:"#f78166",leaf:true,url:"https://intelx.io",desc:"Erweiterte Breach-Suche"}
  ]},
  {name:"👤 Social & Namen",color:"#d2a8ff",action:"social",desc:"Personen & Profile recherchieren",children:[
    {name:"Benutzername",color:"#d2a8ff",action:"social",leaf:true,desc:"Plattformübergreifende Suche"},
    {name:"Echter Name",color:"#d2a8ff",action:"social",leaf:true,desc:"Namenssuche via Suchmaschinen"},
    {name:"Discord-ID",color:"#d2a8ff",action:"social",leaf:true,desc:"Discord Profil via ID finden"}
  ]},
  {name:"🌐 Domain & IP",color:"#ffa657",action:"domain",desc:"Domains und IPs analysieren",children:[
    {name:"WHOIS Info",color:"#ffa657",action:"domain",leaf:true,desc:"Registrar, Inhaber, Datum"},
    {name:"DNS-Einträge",color:"#ffa657",action:"domain",leaf:true,desc:"A, MX, NS, TXT Records"},
    {name:"IP-Adresse",color:"#ffa657",action:"domain",leaf:true,desc:"IP-Auflösung der Domain"},
    {name:"IP-Standort",color:"#ffa657",action:"domain",leaf:true,desc:"Geolokalisierung der IP"}
  ]},
  {name:"📸 Bild & Metadaten",color:"#79c0ff",action:"image",desc:"EXIF-Daten extrahieren",children:[
    {name:"EXIF-Daten",color:"#79c0ff",action:"image",leaf:true,desc:"Kamera, Datum, Software"},
    {name:"GPS-Koordinaten",color:"#79c0ff",action:"image",leaf:true,desc:"Aufnahmeort aus Bild"},
    {name:"Kamera-Infos",color:"#79c0ff",action:"image",leaf:true,desc:"Gerätemodell & Einstellungen"}
  ]},
  {name:"🛡️ VPN-Breaker",color:"#ff7b72",action:"vpn",desc:"VPN/Proxy erkennen & echten Standort analysieren",children:[
    {name:"VPN erkennen",color:"#ff7b72",action:"vpn",leaf:true,desc:"Proxy/VPN/Hosting Flag prüfen"},
    {name:"Echter Standort",color:"#ff7b72",action:"vpn",leaf:true,desc:"Gemeldeter vs. echter Standort"},
    {name:"ISP & ASN",color:"#ff7b72",action:"vpn",leaf:true,desc:"Internetanbieter & Netzwerk-Info"},
    {name:"Reverse-DNS",color:"#ff7b72",action:"vpn",leaf:true,desc:"Hostname hinter der IP"}
  ]},
  {name:"🔑 Passwort-Finder",color:"#e3b341",action:"pwfind",desc:"Passwörter aus Leaks per E-Mail suchen",children:[
    {name:"Leak-Datenbanken",color:"#e3b341",action:"pwfind",leaf:true,desc:"DeHashed, LeakCheck, Snusbase"},
    {name:"Passwort-Hashes",color:"#e3b341",action:"pwfind",leaf:true,desc:"SHA1/MD5 Hashes aus Leaks"},
    {name:"Klartext-Passwörter",color:"#e3b341",action:"pwfind",leaf:true,desc:"Wenn im Klartext geleakt"},
    {name:"Breach-Quellen",color:"#e3b341",action:"pwfind",leaf:true,desc:"Welche Seite wurde gehackt"}
  ]}
]};
const W=document.getElementById("mm").offsetWidth,H=580,R=Math.min(W,H)/2-90;
const svg=d3.select("#mm").append("svg").attr("width",W).attr("height",H);
const g=svg.append("g");
svg.call(d3.zoom().scaleExtent([.35,3]).on("zoom",e=>g.attr("transform",e.transform)))
   .call(d3.zoom().transform,d3.zoomIdentity.translate(W/2,H/2));
g.attr("transform",`translate(${W/2},${H/2})`);
const tree=d3.tree().size([2*Math.PI,R]).separation((a,b)=>(a.parent==b.parent?1:2)/a.depth);
let root=d3.hierarchy(data);
root.descendants().forEach(d=>{if(d.depth>0&&d.children){d._children=d.children;d.children=null;}});
const tip=document.getElementById("tip");
function update(src){
  const lo=tree(root);
  const lk=g.selectAll(".link").data(lo.links(),d=>d.target.data.name);
  lk.enter().append("path").attr("class","link").merge(lk).transition().duration(350)
    .attr("d",d3.linkRadial().angle(d=>d.x).radius(d=>d.y));
  lk.exit().remove();
  const nd=g.selectAll(".node").data(lo.descendants(),d=>d.data.name);
  const ne=nd.enter().append("g").attr("class","node")
    .attr("transform",d=>`rotate(${src.x*180/Math.PI-90}) translate(${src.y},0)`)
    .on("click",(ev,d)=>{
      ev.stopPropagation();
      if(d.data.leaf){if(d.data.url)window.open(d.data.url,"_blank");}
      else{if(d.children){d._children=d.children;d.children=null;}else{d.children=d._children;d._children=null;}update(d);}
    })
    .on("mouseover",(ev,d)=>{if(d.data.desc){tip.style.opacity="1";tip.innerHTML=`<strong style="color:${d.data.color||"#58a6ff"}">${d.data.name}</strong><br>${d.data.desc}`;}})
    .on("mousemove",ev=>{const r=document.getElementById("mm").getBoundingClientRect();tip.style.left=(ev.clientX-r.left+14)+"px";tip.style.top=(ev.clientY-r.top-10)+"px";})
    .on("mouseout",()=>{tip.style.opacity="0";});
  ne.append("circle")
    .attr("r",d=>d.depth===0?20:d.data.leaf?6:13)
    .attr("fill",d=>d.data.color||"#58a6ff")
    .attr("stroke",d=>d.data.color||"#58a6ff")
    .attr("fill-opacity",d=>d.data.leaf?.55:.88);
  ne.append("text").attr("dy","0.31em")
    .attr("x",d=>{if(d.depth===0)return 0;return d.x<Math.PI===!d.children?18:-18;})
    .attr("text-anchor",d=>{if(d.depth===0)return"middle";return d.x<Math.PI===!d.children?"start":"end";})
    .attr("transform",d=>d.depth===0?"":`rotate(${d.x>=Math.PI?180:0})`)
    .text(d=>d.data.name)
    .style("font-size",d=>d.depth===0?"16px":d.data.leaf?"11px":"13px")
    .style("font-weight",d=>d.depth<=1?"bold":"normal");
  nd.merge(ne).transition().duration(350).attr("transform",d=>`rotate(${d.x*180/Math.PI-90}) translate(${d.y},0)`);
  nd.exit().transition().duration(350).attr("transform",d=>`rotate(${src.x*180/Math.PI-90}) translate(${src.y},0)`).remove();
}
update(root);
</script></body></html>"""
    components.html(html, height=600, scrolling=False)

# --- HILFSFUNKTION: Tabelle mit klickbaren Links ---
def link_table(data: dict, col1="Kategorie", col2="Link / Wert"):
    """Rendert ein dict als HTML-Tabelle mit klickbaren Links."""
    rows = ""
    for k, v in data.items():
        v_str = str(v)
        if v_str.startswith("http"):
            cell = f'<a href="{v_str}" target="_blank" style="color:#58a6ff;text-decoration:none">{v_str}</a>'
        else:
            cell = v_str
        rows += f"<tr><td style='padding:6px 12px;border-bottom:1px solid #30363d;color:#8b949e;white-space:nowrap'>{k}</td><td style='padding:6px 12px;border-bottom:1px solid #30363d;color:#e6edf3;word-break:break-all'>{cell}</td></tr>"
    html = f"""
    <table style='width:100%;border-collapse:collapse;background:#161b22;border-radius:8px;overflow:hidden'>
      <thead><tr>
        <th style='padding:8px 12px;background:#21262d;color:#58a6ff;text-align:left'>{col1}</th>
        <th style='padding:8px 12px;background:#21262d;color:#58a6ff;text-align:left'>{col2}</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>"""
    st.markdown(html, unsafe_allow_html=True)

# --- TOOL PANELS ---
def show_phone_panel():
    st.markdown("### 📱 Telefon & Nummer")
    phone = st.text_input("Telefonnummer (+49...)", key="phone_in")
    if st.button("🔍 Analysieren", key="phone_go"):
        with st.spinner("Läuft..."):
            d = lookup_phone(phone)
            link_table(d, "Info", "Wert / Link")
            pdf = create_pdf(d, f"Telefon Bericht: {phone}")
            st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_Phone_{phone}.pdf", key="phone_pdf")

def show_email_panel():
    st.markdown("### 📧 E-Mail & Accounts")
    email = st.text_input("E-Mail Adresse", key="email_in")
    if st.button("🔍 Analysieren", key="email_go"):
        with st.spinner("Läuft..."):
            e = check_account_existence(email)
            b = check_breaches(email)
            st.subheader("Account-Existenz")
            link_table(e, "Dienst", "Link")
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Datenlecks")
            link_table(b, "Quelle", "Link")
            pdf = create_pdf({**e,**b}, f"Email Bericht: {email}")
            st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_Email_{email}.pdf", key="email_pdf")

def show_social_panel():
    st.markdown("### 👤 Social Media & Namen")
    t1,t2,t3 = st.tabs(["Benutzername","Echter Name","Discord-ID"])
    with t1:
        u = st.text_input("Benutzername", key="u_in")
        if st.button("🔍 Suchen", key="u_go"):
            with st.spinner("Läuft..."):
                r = check_social_media(u)
                link_table(r, "Plattform", "Ergebnis / Link")
                pdf = create_pdf(r, f"Social Bericht: {u}")
                st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_Social_{u}.pdf", key="u_pdf")
    with t2:
        n = st.text_input("Echter Name", key="n_in")
        if st.button("🔍 Suchen", key="n_go"):
            with st.spinner("Läuft..."):
                r = search_real_name(n)
                link_table(r, "Quelle", "Link")
                pdf = create_pdf(r, f"Namens Bericht: {n}")
                st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_Name_{n}.pdf", key="n_pdf")
    with t3:
        d = st.text_input("Discord-ID", key="d_in")
        if st.button("🔍 Lookup", key="d_go"):
            with st.spinner("Läuft..."):
                r = lookup_discord_id(d)
                link_table(r, "Service", "Link")
                pdf = create_pdf(r, f"Discord Bericht: {d}")
                st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_Discord_{d}.pdf", key="d_pdf")

def show_domain_panel():
    st.markdown("### 🌐 Domain & IP")
    domain = st.text_input("Domain (z.B. google.com)", key="dom_in")
    if st.button("🔍 Analysieren", key="dom_go"):
        with st.spinner("Läuft..."):
            ip  = get_ip_address(domain)
            loc = get_ip_location(ip)
            dns = get_dns_records(domain)
            c1,c2 = st.columns(2)
            with c1:
                st.subheader("IP & Standort")
                st.write(f"**IP:** {ip}")
                st.json(loc)
            with c2:
                st.subheader("DNS-Einträge")
                st.table(pd.DataFrame(dns.items(), columns=["Typ","Wert"]))
            pdf = create_pdf({"Domain":domain,"IP":ip,"Standort":loc,"DNS":dns}, f"Domain Bericht: {domain}")
            st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_Domain_{domain}.pdf", key="dom_pdf")

def show_image_panel():
    st.markdown("### 📸 Bild & Metadaten")
    f = st.file_uploader("Bild hochladen", type=["jpg","jpeg","png"], key="img_up")
    if f:
        st.image(Image.open(f), caption="Hochgeladenes Bild", use_container_width=True)
        if st.button("🔍 Metadaten auslesen", key="img_go"):
            with open("temp_image.jpg","wb") as fp: fp.write(f.getbuffer())
            exif = get_exif_data("temp_image.jpg")
            st.json(exif)
            pdf = create_pdf(exif, "Bild Metadaten Bericht")
            st.download_button("📄 PDF", data=pdf, file_name="OSINT_Bild_Metadaten.pdf", key="img_pdf")

def show_vpn_panel():
    st.markdown("### 🛡️ VPN-Breaker")
    st.markdown("""
    <div style='background:#161b22;border:1px solid #ff7b72;border-radius:8px;padding:12px 16px;margin-bottom:1rem;color:#ff7b72;font-size:.9rem'>
    ⚠️ Gibt den <strong>gemeldeten Standort</strong> (VPN-Server) sowie Hinweise ob ein VPN/Proxy erkannt wurde zurück.
    Der <strong>echte Standort</strong> des Nutzers kann technisch nicht ermittelt werden – nur der VPN-Anbieter kennt ihn.
    </div>
    """, unsafe_allow_html=True)
    ip = st.text_input("IP-Adresse eingeben (z.B. 95.112.84.129)", key="vpn_in")
    if st.button("🔍 IP analysieren", key="vpn_go"):
        with st.spinner("Analysiere IP..."):
            result = vpn_breaker(ip)
            is_vpn = "JA" in result.get("VPN / Proxy erkannt", "")
            if is_vpn:
                st.error("🚨 VPN / Proxy erkannt!")
            else:
                st.success("✅ Kein VPN/Proxy erkannt")
            link_table(result, "Eigenschaft", "Wert")
            pdf = create_pdf(result, f"VPN-Analyse: {ip}")
            st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_VPN_{ip}.pdf", key="vpn_pdf")

def show_pwfind_panel():
    st.markdown("### 🔑 Passwort-Finder")
    st.markdown("""
    <div style='background:#161b22;border:1px solid #e3b341;border-radius:8px;padding:12px 16px;margin-bottom:1rem;color:#e3b341;font-size:.9rem'>
    🔑 Sucht in öffentlich bekannten Leak-Datenbanken nach Passwörtern, die mit einer E-Mail verbunden sind.
    Direkte Links zu den wichtigsten Diensten + automatische API-Abfrage bei BreachDirectory.
    </div>
    """, unsafe_allow_html=True)
    email = st.text_input("E-Mail Adresse eingeben", key="pw_in")
    if st.button("🔍 Passwörter suchen", key="pw_go"):
        with st.spinner("Durchsuche Leak-Datenbanken..."):
            result = password_finder(email)
            leak_funds = {k: v for k, v in result.items() if k.startswith("Leak-Fund")}
            links      = {k: v for k, v in result.items() if not k.startswith("Leak-Fund")}
            if leak_funds:
                st.error(f"🚨 {len(leak_funds)} Passwort-Einträge in Leaks gefunden!")
                st.subheader("Gefundene Einträge")
                link_table(leak_funds, "Fund", "Details")
                st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.info("ℹ️ Keine direkten Treffer über automatische API. Manuelle Suche empfohlen.")
            st.subheader("🔗 Such-Links (manuell prüfen)")
            link_table(links, "Dienst", "Link")
            pdf = create_pdf(result, f"Passwort-Finder: {email}")
            st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_PW_{email}.pdf", key="pw_pdf")

# --- HAUPT APP ---
if check_password():
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"]{background:#0d1117;color:#e6edf3}
    [data-testid="stSidebar"]{background:#161b22;border-right:1px solid #30363d}
    .stButton>button{background:#21262d;color:#e6edf3;border:1px solid #30363d;border-radius:6px;transition:all .2s}
    .stButton>button:hover{background:#388bfd;border-color:#388bfd;color:#fff}
    .stTextInput>div>div>input{background:#161b22;color:#e6edf3;border:1px solid #30363d;border-radius:6px}
    h1,h2,h3{color:#58a6ff !important}
    .stTabs [data-baseweb="tab"]{color:#8b949e}
    .stTabs [aria-selected="true"]{color:#58a6ff !important}
    hr{border-color:#30363d}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center;padding:1rem 0 .3rem'>
      <h1 style='color:#58a6ff;font-size:2.2rem;letter-spacing:3px'>🔍 FULL DATA</h1>
      <p style='color:#8b949e;font-size:.9rem'>Klicke auf einen Knoten oder wähle links eine Kategorie</p>
    </div><hr>
    """, unsafe_allow_html=True)

    if "panel" not in st.session_state:
        st.session_state.panel = None

    st.sidebar.markdown("## 🗂️ Kategorien")
    for label, key in [
        ("📱 Telefon & Nummer","phone"),
        ("📧 E-Mail & Accounts","email"),
        ("👤 Social & Namen","social"),
        ("🌐 Domain & IP","domain"),
        ("📸 Bild & Metadaten","image"),
        ("🛡️ VPN-Breaker","vpn"),
        ("🔑 Passwort-Finder","pwfind"),
    ]:
        if st.sidebar.button(label, key=f"sb_{key}"):
            st.session_state.panel = key
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Ausloggen"):
        st.session_state.password_correct = False
        st.rerun()

    render_mindmap()
    st.markdown("<hr>", unsafe_allow_html=True)

    p = st.session_state.panel
    if   p == "phone":   show_phone_panel()
    elif p == "email":   show_email_panel()
    elif p == "social":  show_social_panel()
    elif p == "domain":  show_domain_panel()
    elif p == "image":   show_image_panel()
    elif p == "vpn":     show_vpn_panel()
    elif p == "pwfind":  show_pwfind_panel()
    else:
        st.markdown("<div style='text-align:center;color:#8b949e;padding:2rem;font-size:1.1rem'>👆 Wähle eine Kategorie aus der Seitenleiste oder klicke auf einen Knoten</div>", unsafe_allow_html=True)
