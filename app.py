import streamlit as st
import json
import pandas as pd
from domain_recon import get_whois_info, get_dns_records, get_ip_address, get_ip_location
from social_recon import check_social_media, lookup_discord_id, search_real_name
from phone_recon import lookup_phone, check_account_existence, check_breaches
from media_recon import get_exif_data
from PIL import Image
from fpdf import FPDF
import datetime
import io

# --- PDF GENERATOR FUNKTION ---
def create_pdf(report_data, title="OSINT Recherche Bericht"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.set_font("Arial", "", 10)
    pdf.cell(200, 10, txt=f"Erstellt am: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", ln=True, align='C')
    pdf.ln(10)

    for section, data in report_data.items():
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, txt=section.upper(), ln=True)
        pdf.set_font("Arial", "", 10)
        if isinstance(data, dict):
            for k, v in data.items():
                pdf.multi_cell(0, 8, txt=f"{k}: {v}")
        else:
            pdf.multi_cell(0, 8, txt=str(data))
        pdf.ln(5)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- SEITEN KONFIGURATION ---
st.set_page_config(page_title="Manus OSINT Pro Dashboard", page_icon="🔍", layout="wide")

# --- EINFACHER PASSWORTSCHUTZ ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        st.title("🔒 Zugriff geschützt")
        pwd = st.text_input("Bitte Passwort eingeben:", type="password")
        if st.button("Einloggen"):
            if pwd == "osint123": # Standard-Passwort
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("Falsches Passwort!")
        return False
    return True

if check_password():
    st.title("🔍 Pro OSINT Dashboard")
    st.markdown("---")

    # Sidebar Navigation
    menu = st.sidebar.selectbox("Suche auswählen", ["🌐 Domain-Recherche", "👤 Social Media & Namen", "📱 Telefon & Accounts", "📸 Bild-Metadaten"])

    # --- DOMAIN RECHERCHE ---
    if menu == "🌐 Domain-Recherche":
        st.header("Domain- & IP-Infos")
        domain = st.text_input("Domain eingeben (z.B. google.com)")
        if st.button("Domain prüfen"):
            with st.spinner("Recherche läuft..."):
                ip = get_ip_address(domain)
                loc = get_ip_location(ip)
                dns = get_dns_records(domain)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("IP & Standort")
                    st.write(f"**IP:** {ip}")
                    st.json(loc)
                with col2:
                    st.subheader("DNS-Einträge")
                    st.table(pd.DataFrame(dns.items(), columns=["Typ", "Wert"]))
                
                # PDF Export
                report = {"Domain": domain, "IP": ip, "Standort": loc, "DNS": dns}
                pdf_bytes = create_pdf(report, f"Domain Bericht: {domain}")
                st.download_button("📄 Bericht als PDF herunterladen", data=pdf_bytes, file_name=f"OSINT_Domain_{domain}.pdf")

    # --- SOCIAL MEDIA ---
    elif menu == "👤 Social Media & Namen":
        st.header("Social Media & Namens-Suche")
        tab1, tab2, tab3 = st.tabs(["Benutzername", "Echter Name", "Discord-ID"])
        
        with tab1:
            username = st.text_input("Benutzername suchen")
            if st.button("Social Media Check"):
                with st.spinner("Suche läuft..."):
                    results = check_social_media(username)
                    st.table(pd.DataFrame(results.items(), columns=["Plattform", "Ergebnis"]))
                    pdf_bytes = create_pdf(results, f"Social Media Bericht: {username}")
                    st.download_button("📄 Bericht als PDF herunterladen", data=pdf_bytes, file_name=f"OSINT_Social_{username}.pdf")
                    
        with tab2:
            full_name = st.text_input("Echter Name (z.B. Max Mustermann)")
            if st.button("Namens-Suche"):
                with st.spinner("Suche läuft..."):
                    name_data = search_real_name(full_name)
                    st.table(pd.DataFrame(name_data.items(), columns=["Quelle", "Link"]))
                    pdf_bytes = create_pdf(name_data, f"Namens Bericht: {full_name}")
                    st.download_button("📄 Bericht als PDF herunterladen", data=pdf_bytes, file_name=f"OSINT_Name_{full_name}.pdf")
                    
        with tab3:
            d_id = st.text_input("Discord-ID (Zahlenreihe)")
            if st.button("Discord Lookup"):
                with st.spinner("Suche läuft..."):
                    discord_data = lookup_discord_id(d_id)
                    st.table(pd.DataFrame(discord_data.items(), columns=["Service", "Link"]))
                    pdf_bytes = create_pdf(discord_data, f"Discord Bericht: {d_id}")
                    st.download_button("📄 Bericht als PDF herunterladen", data=pdf_bytes, file_name=f"OSINT_Discord_{d_id}.pdf")

    # --- TELEFON & ACCOUNTS ---
    elif menu == "📱 Telefon & Accounts":
        st.header("Telefon- & Account-Recherche")
        col1, col2 = st.columns(2)
        
        with col1:
            phone = st.text_input("Telefonnummer (+49...)")
            if st.button("Telefon-Check"):
                with st.spinner("Suche läuft..."):
                    p_data = lookup_phone(phone)
                    st.table(pd.DataFrame(p_data.items(), columns=["Info", "Wert"]))
                    pdf_bytes = create_pdf(p_data, f"Telefon Bericht: {phone}")
                    st.download_button("📄 Bericht als PDF herunterladen", data=pdf_bytes, file_name=f"OSINT_Phone_{phone}.pdf")
                    
        with col2:
            email = st.text_input("E-Mail Adresse")
            if st.button("Account- & Breach-Check"):
                with st.spinner("Suche läuft..."):
                    e_data = check_account_existence(email)
                    b_data = check_breaches(email)
                    st.subheader("Account-Existenz")
                    st.table(pd.DataFrame(e_data.items(), columns=["Dienst", "Status"]))
                    st.subheader("Datenlecks (Breaches)")
                    st.table(pd.DataFrame(b_data.items(), columns=["Quelle", "Link"]))
                    pdf_bytes = create_pdf({**e_data, **b_data}, f"Email Bericht: {email}")
                    st.download_button("📄 Bericht als PDF herunterladen", data=pdf_bytes, file_name=f"OSINT_Email_{email}.pdf")

    # --- BILD-METADATEN ---
    elif menu == "📸 Bild-Metadaten":
        st.header("Bild-Metadaten (EXIF) Extraktor")
        uploaded_file = st.file_uploader("Bild hochladen", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Hochgeladenes Bild", use_container_width=True)
            
            if st.button("Metadaten auslesen"):
                with open("temp_image.jpg", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                exif = get_exif_data("temp_image.jpg")
                st.subheader("Gefundene Metadaten")
                st.json(exif)
                pdf_bytes = create_pdf(exif, "Bild Metadaten Bericht")
                st.download_button("📄 Bericht als PDF herunterladen", data=pdf_bytes, file_name="OSINT_Bild_Metadaten.pdf")

    st.sidebar.markdown("---")
    if st.sidebar.button("Ausloggen"):
        st.session_state.password_correct = False
        st.rerun()
