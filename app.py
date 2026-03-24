import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from domain_recon import get_whois_info, get_dns_records, get_ip_address, get_ip_location, vpn_breaker
from social_recon import check_social_media, lookup_discord_id, search_real_name
from phone_recon import lookup_phone, check_account_existence, check_breaches, password_finder
from media_recon import get_exif_data
from sherlock_recon import sherlock_search, dork_generator, reverse_image_links
from crypto_recon import lookup_wallet
from github_recon import github_user_recon, github_email_search
from geo_recon import gps_to_map, phone_spam_score, ip_network_scan, address_lookup, fake_profile_check
from PIL import Image
from fpdf import FPDF
import datetime

# --- PDF GENERATOR ---
def _safe(text, max_len=160):
    """Text sicher auf latin-1 kodieren und Länge begrenzen."""
    s = str(text)
    s = s.encode("latin-1", "replace").decode("latin-1")
    return s[:max_len] + ("..." if len(s) > max_len else "")

def create_pdf(report_data, title="OSINT Bericht"):
    """Erstellt ein PDF aus einem flachen oder verschachtelten Dictionary."""
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    # Titel
    pdf.set_font("Arial", "B", 15)
    pdf.cell(0, 10, txt=_safe(title, 80), ln=True, align="C")
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 8, txt=_safe(f"Erstellt: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"), ln=True, align="C")
    pdf.ln(6)
    pdf.set_font("Arial", "", 10)
    usable_w = pdf.w - pdf.l_margin - pdf.r_margin
    for k, v in report_data.items():
        key_str   = _safe(str(k), 60)
        val_str   = _safe(str(v), 140)
        line      = f"{key_str}: {val_str}"
        pdf.multi_cell(usable_w, 7, txt=line)
    out = pdf.output(dest="S")
    if isinstance(out, bytes):
        return out
    return out.encode("latin-1", "replace")

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
  ]},
  {name:"🔎 Sherlock",color:"#56d364",action:"sherlock",desc:"Benutzername auf 50+ Plattformen suchen",children:[
    {name:"Instagram, TikTok",color:"#56d364",action:"sherlock",leaf:true,desc:"Social Media Profile finden"},
    {name:"GitHub, Steam",color:"#56d364",action:"sherlock",leaf:true,desc:"Tech & Gaming Profile"},
    {name:"OnlyFans, Patreon",color:"#56d364",action:"sherlock",leaf:true,desc:"Content Plattformen"},
    {name:"50+ Plattformen",color:"#56d364",action:"sherlock",leaf:true,desc:"Vollständige Plattform-Liste"}
  ]},
  {name:"🔍 Dork Generator",color:"#bc8cff",action:"dork",desc:"Google Dorks für Namen, E-Mail, Telefon",children:[
    {name:"Name Dorks",color:"#bc8cff",action:"dork",leaf:true,desc:"Suchanfragen für Personen"},
    {name:"E-Mail Dorks",color:"#bc8cff",action:"dork",leaf:true,desc:"Suchanfragen für E-Mails"},
    {name:"Telefon Dorks",color:"#bc8cff",action:"dork",leaf:true,desc:"Suchanfragen für Telefonnummern"}
  ]},
  {name:"🖼️ Reverse Image",color:"#f0883e",action:"revimg",desc:"Bild rückwärts suchen & Fake erkennen",children:[
    {name:"Google Lens",color:"#f0883e",action:"revimg",leaf:true,desc:"Google Bildersuche"},
    {name:"Yandex / TinEye",color:"#f0883e",action:"revimg",leaf:true,desc:"Alternative Suchmaschinen"},
    {name:"PimEyes (Gesicht)",color:"#f0883e",action:"revimg",leaf:true,desc:"Gesichtserkennung"},
    {name:"KI-Bild Erkennung",color:"#f0883e",action:"revimg",leaf:true,desc:"Fake-Profil-Bild erkennen"}
  ]},
  {name:"₿ Crypto Wallet",color:"#f7c948",action:"crypto",desc:"Bitcoin & Ethereum Wallets analysieren",children:[
    {name:"Bitcoin (BTC)",color:"#f7c948",action:"crypto",leaf:true,desc:"Guthaben & Transaktionen"},
    {name:"Ethereum (ETH)",color:"#f7c948",action:"crypto",leaf:true,desc:"ETH-Wallet analysieren"},
    {name:"Blockchain Explorer",color:"#f7c948",action:"crypto",leaf:true,desc:"Transaktionshistorie"}
  ]},
  {name:"🐙 GitHub OSINT",color:"#8b949e",action:"github",desc:"GitHub Profile & E-Mails aus Commits",children:[
    {name:"Profil-Analyse",color:"#8b949e",action:"github",leaf:true,desc:"Name, Bio, Standort, Repos"},
    {name:"E-Mail aus Commits",color:"#8b949e",action:"github",leaf:true,desc:"Versteckte E-Mails finden"},
    {name:"Aktivitäts-Analyse",color:"#8b949e",action:"github",leaf:true,desc:"Wann ist jemand aktiv"}
  ]},
  {name:"📡 IP-Netzwerk-Scan",color:"#ff9500",action:"ipscan",desc:"Offene Ports, Shodan, Blacklists",children:[
    {name:"Shodan",color:"#ff9500",action:"ipscan",leaf:true,desc:"Offene Ports & Dienste"},
    {name:"AbuseIPDB",color:"#ff9500",action:"ipscan",leaf:true,desc:"IP-Blacklist prüfen"},
    {name:"VirusTotal",color:"#ff9500",action:"ipscan",leaf:true,desc:"Malware & Reputation"}
  ]},
  {name:"📍 Adress-Lookup",color:"#39d353",action:"address",desc:"Adresse auf Karte & Personen suchen",children:[
    {name:"Google Maps",color:"#39d353",action:"address",leaf:true,desc:"Adresse auf Karte anzeigen"},
    {name:"Streetview",color:"#39d353",action:"address",leaf:true,desc:"Gebäude ansehen"},
    {name:"Telefonbuch",color:"#39d353",action:"address",leaf:true,desc:"Bewohner suchen (DE)"}
  ]},
  {name:"📞 Spam-Score",color:"#ff6b6b",action:"spam",desc:"Telefonnummer auf Spam prüfen",children:[
    {name:"Tellows",color:"#ff6b6b",action:"spam",leaf:true,desc:"Spam-Score & Bewertungen"},
    {name:"WerRuftAn",color:"#ff6b6b",action:"spam",leaf:true,desc:"Deutsche Spam-Datenbank"},
    {name:"Truecaller",color:"#ff6b6b",action:"spam",leaf:true,desc:"Weltweite Spam-Erkennung"}
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

def show_sherlock_panel():
    st.markdown("### 🔎 Sherlock – Benutzername-Suche")
    st.markdown("""
    <div style='background:#161b22;border:1px solid #56d364;border-radius:8px;padding:12px 16px;margin-bottom:1rem;color:#56d364;font-size:.9rem'>
    🔎 Sucht einen Benutzernamen auf <strong>50+ Plattformen</strong> gleichzeitig und gibt direkte Links zurück.
    </div>
    """, unsafe_allow_html=True)
    username = st.text_input("Benutzername eingeben", key="sh_in")
    if st.button("🔍 Auf allen Plattformen suchen", key="sh_go"):
        with st.spinner("Suche auf 50+ Plattformen..."):
            result = sherlock_search(username)
            st.success(f"✅ {len(result)} Plattformen durchsucht – klicke die Links um Profile zu prüfen")
            link_table(result, "Plattform", "Profil-Link")
            pdf = create_pdf(result, f"Sherlock: {username}")
            st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_Sherlock_{username}.pdf", key="sh_pdf")

def show_dork_panel():
    st.markdown("### 🔍 Google Dork Generator")
    st.markdown("""
    <div style='background:#161b22;border:1px solid #bc8cff;border-radius:8px;padding:12px 16px;margin-bottom:1rem;color:#bc8cff;font-size:.9rem'>
    🔍 Generiert optimierte Google-Suchanfragen (Dorks) für Namen, E-Mails und Telefonnummern.
    </div>
    """, unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["Name", "E-Mail", "Telefon"])
    with t1:
        q = st.text_input("Vollständiger Name", key="dk_name")
        if st.button("🔍 Dorks generieren", key="dk_name_go"):
            result = dork_generator(q, "name")
            link_table(result, "Suchanfrage", "Link")
            pdf = create_pdf(result, f"Dork Generator: {q}")
            st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_Dork_{q}.pdf", key="dk_name_pdf")
    with t2:
        q = st.text_input("E-Mail Adresse", key="dk_email")
        if st.button("🔍 Dorks generieren", key="dk_email_go"):
            result = dork_generator(q, "email")
            link_table(result, "Suchanfrage", "Link")
            pdf = create_pdf(result, f"Dork Generator: {q}")
            st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_Dork_{q}.pdf", key="dk_email_pdf")
    with t3:
        q = st.text_input("Telefonnummer", key="dk_phone")
        if st.button("🔍 Dorks generieren", key="dk_phone_go"):
            result = dork_generator(q, "phone")
            link_table(result, "Suchanfrage", "Link")
            pdf = create_pdf(result, f"Dork Generator: {q}")
            st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_Dork_{q}.pdf", key="dk_phone_pdf")

def show_revimg_panel():
    st.markdown("### 🖼️ Reverse Image Search & Fake-Erkennung")
    st.markdown("""
    <div style='background:#161b22;border:1px solid #f0883e;border-radius:8px;padding:12px 16px;margin-bottom:1rem;color:#f0883e;font-size:.9rem'>
    🖼️ Bild-URL eingeben oder direkt auf den Plattformen hochladen. Auch KI-generierte Bilder erkennbar.
    </div>
    """, unsafe_allow_html=True)
    t1, t2 = st.tabs(["Reverse Image Search", "Fake-Profil Erkennung"])
    with t1:
        img_url = st.text_input("Bild-URL (optional, für direkte Suche)", key="ri_url")
        if st.button("🔍 Such-Links generieren", key="ri_go"):
            result = reverse_image_links(img_url)
            link_table(result, "Dienst", "Link")
            pdf = create_pdf(result, "Reverse Image Search")
            st.download_button("📄 PDF", data=pdf, file_name="OSINT_ReverseImage.pdf", key="ri_pdf")
    with t2:
        img_url2 = st.text_input("Bild-URL (optional)", key="fp_url")
        if st.button("🔍 Fake-Check Links", key="fp_go"):
            result = fake_profile_check(img_url2)
            link_table(result, "Tool", "Link")
            pdf = create_pdf(result, "Fake-Profil Erkennung")
            st.download_button("📄 PDF", data=pdf, file_name="OSINT_FakeCheck.pdf", key="fp_pdf")

def show_crypto_panel():
    st.markdown("### ₿ Crypto Wallet Tracker")
    st.markdown("""
    <div style='background:#161b22;border:1px solid #f7c948;border-radius:8px;padding:12px 16px;margin-bottom:1rem;color:#f7c948;font-size:.9rem'>
    ₿ Bitcoin (BTC) und Ethereum (ETH) Wallets analysieren: Guthaben, Transaktionen, Explorer-Links.
    </div>
    """, unsafe_allow_html=True)
    wallet = st.text_input("Wallet-Adresse eingeben (BTC oder ETH)", key="cw_in")
    if st.button("🔍 Wallet analysieren", key="cw_go"):
        with st.spinner("Analysiere Wallet..."):
            result = lookup_wallet(wallet)
            link_table(result, "Eigenschaft", "Wert / Link")
            pdf = create_pdf(result, f"Crypto Wallet: {wallet}")
            st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_Crypto_{wallet[:10]}.pdf", key="cw_pdf")

def show_github_panel():
    st.markdown("### 🐙 GitHub OSINT")
    t1, t2 = st.tabs(["Benutzername-Analyse", "E-Mail Suche"])
    with t1:
        uname = st.text_input("GitHub Benutzername", key="gh_in")
        if st.button("🔍 Profil analysieren", key="gh_go"):
            with st.spinner("Analysiere GitHub-Profil..."):
                result = github_user_recon(uname)
                if "Fehler" in result:
                    st.error(result["Fehler"])
                else:
                    link_table(result, "Eigenschaft", "Wert / Link")
                    pdf = create_pdf(result, f"GitHub OSINT: {uname}")
                    st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_GitHub_{uname}.pdf", key="gh_pdf")
    with t2:
        email = st.text_input("E-Mail Adresse", key="ghe_in")
        if st.button("🔍 Auf GitHub suchen", key="ghe_go"):
            result = github_email_search(email)
            link_table(result, "Suche", "Link")
            pdf = create_pdf(result, f"GitHub E-Mail: {email}")
            st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_GitHubEmail_{email}.pdf", key="ghe_pdf")

def show_ipscan_panel():
    st.markdown("### 📡 IP-Netzwerk-Scan")
    ip = st.text_input("IP-Adresse eingeben", key="ips_in")
    if st.button("🔍 IP scannen", key="ips_go"):
        with st.spinner("Scanne IP..."):
            result = ip_network_scan(ip)
            is_vpn = result.get("Proxy/VPN", "Nein") == "Ja"
            if is_vpn:
                st.warning("⚠️ VPN/Proxy erkannt")
            link_table(result, "Eigenschaft", "Wert / Link")
            pdf = create_pdf(result, f"IP-Scan: {ip}")
            st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_IPScan_{ip}.pdf", key="ips_pdf")

def show_address_panel():
    st.markdown("### 📍 Adress-Lookup")
    addr = st.text_input("Adresse eingeben (z.B. Musterstr. 1, Berlin)", key="adr_in")
    if st.button("🔍 Adresse suchen", key="adr_go"):
        result = address_lookup(addr)
        link_table(result, "Dienst", "Link")
        pdf = create_pdf(result, f"Adress-Lookup: {addr}")
        st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_Adresse.pdf", key="adr_pdf")

def show_spam_panel():
    st.markdown("### 📞 Telefon Spam-Score")
    phone = st.text_input("Telefonnummer eingeben (+49...)", key="sp_in")
    if st.button("🔍 Spam-Score prüfen", key="sp_go"):
        result = phone_spam_score(phone)
        link_table(result, "Dienst", "Link")
        pdf = create_pdf(result, f"Spam-Score: {phone}")
        st.download_button("📄 PDF", data=pdf, file_name=f"OSINT_Spam_{phone}.pdf", key="sp_pdf")

# --- KI CHAT ---
def show_chat_page():
    st.markdown("### 💬 OSINT KI-Assistent")
    st.markdown("""
    <div style='background:#161b22;border:1px solid #388bfd;border-radius:8px;padding:12px 16px;margin-bottom:1rem;color:#8b949e;font-size:.9rem'>
    🤖 Stelle Fragen zu OSINT-Techniken, Recherche-Methoden oder lass dir Ergebnisse erklären.
    </div>
    """, unsafe_allow_html=True)
    import os
    from openai import OpenAI
    client = OpenAI()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": "Du bist ein OSINT-Experte und hilfst bei der Recherche von öffentlich verfügbaren Informationen. Du erklärst Techniken, Tools und Methoden. Antworte immer auf Deutsch und halte dich an legale, ethische OSINT-Methoden."}
        ]
    for msg in st.session_state.chat_history[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    user_input = st.chat_input("Frage stellen...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Denke nach..."):
                try:
                    resp = client.chat.completions.create(
                        model="gpt-4.1-mini",
                        messages=st.session_state.chat_history,
                        max_tokens=800
                    )
                    answer = resp.choices[0].message.content
                except Exception as e:
                    answer = f"Fehler: {e}"
                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
    if st.button("🗑️ Chat leeren"):
        st.session_state.chat_history = st.session_state.chat_history[:1]
        st.rerun()

# --- NEWS ---
def show_news_page():
    import requests as _req
    st.markdown("### 📰 Cybersecurity & Datenleck News")
    feeds = [
        ("Bleeping Computer",  "https://www.bleepingcomputer.com/feed/"),
        ("Krebs on Security",  "https://krebsonsecurity.com/feed/"),
        ("The Hacker News",    "https://feeds.feedburner.com/TheHackersNews"),
        ("Heise Security",     "https://www.heise.de/security/rss/news-atom.xml"),
        ("Have I Been Pwned",  "https://feeds.feedburner.com/HaveIBeenPwned"),
    ]
    tab_labels = [f[0] for f in feeds]
    tabs = st.tabs(tab_labels)
    for tab, (name, url) in zip(tabs, feeds):
        with tab:
            try:
                import xml.etree.ElementTree as ET
                r = _req.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
                root = ET.fromstring(r.content)
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                items = root.findall(".//item") or root.findall(".//atom:entry", ns)
                count = 0
                for item in items[:10]:
                    title_el = item.find("title") or item.find("atom:title", ns)
                    link_el  = item.find("link")  or item.find("atom:link", ns)
                    desc_el  = item.find("description") or item.find("atom:summary", ns)
                    if title_el is None:
                        continue
                    title_txt = title_el.text or ""
                    link_txt  = (link_el.text or link_el.get("href", "")) if link_el is not None else ""
                    desc_txt  = (desc_el.text or "")[:200] if desc_el is not None else ""
                    import re
                    desc_txt = re.sub(r"<[^>]+>", "", desc_txt)
                    st.markdown(f"""<div style='background:#161b22;border:1px solid #30363d;border-radius:8px;padding:12px 16px;margin-bottom:.7rem'>
                    <a href='{link_txt}' target='_blank' style='color:#58a6ff;font-weight:bold;text-decoration:none;font-size:1rem'>{title_txt}</a>
                    <p style='color:#8b949e;font-size:.85rem;margin:.4rem 0 0'>{desc_txt}...</p>
                    </div>""", unsafe_allow_html=True)
                    count += 1
                if count == 0:
                    st.info("Keine Artikel gefunden.")
            except Exception as e:
                st.error(f"Feed konnte nicht geladen werden: {e}")

# --- UMFRAGEN ---
def show_polls_page():
    st.markdown("### 📊 Community Umfragen")
    if "poll_votes" not in st.session_state:
        st.session_state.poll_votes = {}
    polls = [
        {
            "id": "p1",
            "frage": "🔍 Welches OSINT-Tool nutzt du am häufigsten?",
            "optionen": ["Sherlock", "Maltego", "OSINT Framework", "theHarvester", "Shodan"]
        },
        {
            "id": "p2",
            "frage": "🛡️ Wie schützt du deine eigene Online-Privatsphäre?",
            "optionen": ["VPN", "Tor Browser", "Fake-Accounts", "Nichts davon", "Mehreres kombiniert"]
        },
        {
            "id": "p3",
            "frage": "📊 Wie oft nutzt du OSINT-Tools?",
            "optionen": ["Täglich", "Wöchentlich", "Monatlich", "Selten"]
        },
        {
            "id": "p4",
            "frage": "💡 Welche neue Funktion würdest du dir wünschen?",
            "optionen": ["Darknet-Suche", "Gesichtserkennung", "Auto-Bericht", "Mehr Leak-Daten", "Mobile App"]
        },
    ]
    cols = st.columns(2)
    for i, poll in enumerate(polls):
        with cols[i % 2]:
            st.markdown(f"<div style='background:#161b22;border:1px solid #30363d;border-radius:10px;padding:16px;margin-bottom:1rem'>", unsafe_allow_html=True)
            st.markdown(f"**{poll['frage']}**")
            voted = st.session_state.poll_votes.get(poll["id"])
            if voted is None:
                choice = st.radio("", poll["optionen"], key=f"poll_{poll['id']}", label_visibility="collapsed")
                if st.button("✅ Abstimmen", key=f"vote_{poll['id']}"):
                    st.session_state.poll_votes[poll["id"]] = choice
                    st.rerun()
            else:
                st.success(f"Deine Stimme: **{voted}**")
                if st.button("🔄 Erneut abstimmen", key=f"revote_{poll['id']}"):
                    del st.session_state.poll_votes[poll["id"]]
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

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

    if "page" not in st.session_state:
        st.session_state.page = "kategorien"
    if "panel" not in st.session_state:
        st.session_state.panel = None

    # --- HAUPTNAVIGATION ---
    st.sidebar.markdown("""
    <div style='text-align:center;padding:.5rem 0 1rem'>
      <span style='color:#58a6ff;font-size:1.3rem;font-weight:bold;letter-spacing:2px'>🔍 FULL DATA</span>
    </div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("🔍 Kategorien", "kategorien"),
        ("💬 KI-Chat",     "chat"),
        ("📰 News",        "news"),
        ("📊 Umfragen",    "umfragen"),
    ]
    for label, key in nav_items:
        active = st.session_state.page == key
        style = "background:#388bfd;color:#fff;" if active else ""
        if st.sidebar.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.session_state.panel = None
            st.rerun()

    st.sidebar.markdown("---")

    # --- KATEGORIEN SIDEBAR ---
    if st.session_state.page == "kategorien":
        st.sidebar.markdown("**🗂️ Tools**")
        for label, key in [
            ("📱 Telefon & Nummer","phone"),
            ("📞 Spam-Score","spam"),
            ("📧 E-Mail & Accounts","email"),
            ("🔑 Passwort-Finder","pwfind"),
            ("👤 Social & Namen","social"),
            ("🔎 Sherlock","sherlock"),
            ("🌐 Domain & IP","domain"),
            ("📡 IP-Netzwerk-Scan","ipscan"),
            ("🛡️ VPN-Breaker","vpn"),
            ("📸 Bild & Metadaten","image"),
            ("🖼️ Reverse Image","revimg"),
            ("🔍 Dork Generator","dork"),
            ("₿ Crypto Wallet","crypto"),
            ("🐙 GitHub OSINT","github"),
            ("📍 Adress-Lookup","address"),
        ]:
            if st.sidebar.button(label, key=f"sb_{key}", use_container_width=True):
                st.session_state.panel = key
        st.sidebar.markdown("")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Ausloggen", use_container_width=True):
        st.session_state.password_correct = False
        st.rerun()

    # --- SEITENANZEIGE ---
    pg = st.session_state.page

    if pg == "chat":
        show_chat_page()
    elif pg == "news":
        show_news_page()
    elif pg == "umfragen":
        show_polls_page()
    else:
        # Kategorien-Seite
        st.markdown("""
        <div style='text-align:center;padding:1rem 0 .3rem'>
          <h1 style='color:#58a6ff;font-size:2.2rem;letter-spacing:3px'>🔍 FULL DATA</h1>
          <p style='color:#8b949e;font-size:.9rem'>Klicke auf einen Knoten oder wähle links eine Kategorie</p>
        </div><hr>
        """, unsafe_allow_html=True)
        render_mindmap()
        st.markdown("<hr>", unsafe_allow_html=True)
        p = st.session_state.panel
        if   p == "phone":    show_phone_panel()
        elif p == "email":    show_email_panel()
        elif p == "social":   show_social_panel()
        elif p == "domain":   show_domain_panel()
        elif p == "image":    show_image_panel()
        elif p == "vpn":      show_vpn_panel()
        elif p == "pwfind":   show_pwfind_panel()
        elif p == "sherlock": show_sherlock_panel()
        elif p == "dork":     show_dork_panel()
        elif p == "revimg":   show_revimg_panel()
        elif p == "crypto":   show_crypto_panel()
        elif p == "github":   show_github_panel()
        elif p == "ipscan":   show_ipscan_panel()
        elif p == "address":  show_address_panel()
        elif p == "spam":     show_spam_panel()
        else:
            st.markdown("<div style='text-align:center;color:#8b949e;padding:2rem;font-size:1.1rem'>👆 Wähle eine Kategorie aus der Seitenleiste oder klicke auf einen Knoten</div>", unsafe_allow_html=True)
