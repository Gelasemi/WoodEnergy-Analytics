import streamlit as st
import pandas as pd
import plotly.express as px
import paho.mqtt.client as mqtt
import json

# --- 1. CONFIGURATION MQTT (SIMULÉE OU RÉELLE) ---
# Si vous avez un broker (ex: Mosquitto), remplacez 'localhost' par son IP
if 'iot_data' not in st.session_state:
    st.session_state.iot_data = {
        "Scie de tête": 0.0, "Déligneuse": 0.0, 
        "Aspiration": 0.0, "Séchoir": 0.0, "Convoyeurs": 0.0
    }

def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        machine = payload.get("machine")
        valeur = payload.get("kw")
        if machine in st.session_state.iot_data:
            st.session_state.iot_data[machine] = valeur
    except:
        pass

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="WoodEnergy Ultimate", layout="wide")
st.title("🌲 WoodEnergy Analytics v5 : Smart Scierie")
st.markdown("---")

# --- 3. BARRE LATÉRALE (INPUTS) ---
st.sidebar.header("📊 Pilotage de Production")
essence = st.sidebar.selectbox("Essence de bois", ["Sapin (Tendre)", "Pin (Moyen)", "Hêtre (Dur)", "Chêne (Très dur)"])
vol_cible = st.sidebar.number_input("Volume cible (m³)", value=1000)

st.sidebar.header("🔌 Énergie & IoT")
mode_iot = st.sidebar.toggle("Activer Capteurs MQTT (Schneider/Siemens)", value=False)
t_plein = st.sidebar.number_input("Tarif Plein (€/kWh)", value=0.22)
t_creux = st.sidebar.number_input("Tarif Creux (€/kWh)", value=0.14)

st.sidebar.header("🌍 Environnement")
mix_co2 = st.sidebar.slider("Mix CO2 (g/kWh)", 0, 500, 50) # France ~50g

# --- 4. LOGIQUE MÉTIER ---
coeffs_bois = {"Sapin (Tendre)": 1.0, "Pin (Moyen)": 1.1, "Hêtre (Dur)": 1.4, "Chêne (Très dur)": 1.7}
c_effort = coeffs_bois[essence]

machines_base = {
    "Scie de tête": {"p": 75, "hc": False},
    "Déligneuse": {"p": 30, "hc": False},
    "Aspiration": {"p": 45, "hc": False},
    "Séchoir": {"p": 110, "hc": True}, # Le séchoir est optimisé pour les heures creuses
    "Convoyeurs": {"p": 15, "hc": False}
}

# --- 5. CALCULS DES DONNÉES ANALYTIQUES ---
results = []
for name, specs in machines_base.items():
    # Utilisation de la donnée IoT si activée, sinon puissance nominale
    p_actuelle = st.session_state.iot_data[name] if mode_iot and st.session_state.iot_data[name] > 0 else specs["p"]
    
    # Ajustement selon dureté du bois
    p_ajustee = p_actuelle * c_effort
    
    # Temps de fonctionnement estimé (22 jours, 8h)
    heures = 176 
    tarif = t_creux if specs["hc"] else t_plein
    
    conso_kwh = p_ajustee * heures * 0.7 # 0.7 = facteur de charge moyen
    cout = conso_kwh * tarif
    co2 = (conso_kwh * mix_co2) / 1_000_000 # En tonnes
    
    results.append({
        "Machine": name,
        "Puissance Live (kW)": round(p_ajustee, 1),
        "Consommation (kWh)": round(conso_kwh, 0),
        "Coût Mensuel (€)": round(cout, 2),
        "Bilan CO2 (T)": round(co2, 3),
        "Coût/m³ (€)": round(cout / vol_cible, 2)
    })

df = pd.DataFrame(results)

# --- 6. AFFICHAGE DES INDICATEURS (KPI) ---
total_cout = df["Coût Mensuel (€)"].sum()
total_co2 = df["Bilan CO2 (T)"].sum()
cout_m3 = total_cout / vol_cible

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Budget Mensuel", f"{total_cout:,.2f} €")
kpi2.metric("Coût moyen / m³", f"{cout_m3:.2f} €/m³")
kpi3.metric("Empreinte Carbone", f"{total_co2:.2f} T.CO2")
kpi4.metric("Facteur Effort Bois", f"x {c_effort}")

st.markdown("---")

# --- 7. VISUALISATION ---
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("💰 Répartition du Coût de Revient (€/m³)")
    fig_cout = px.bar(df, x="Machine", y="Coût/m³ (€)", color="Machine", text_auto=True)
    st.plotly_chart(fig_cout, use_container_width=True)

with col_b:
    st.subheader("🌱 Émissions CO2 par Machine")
    fig_co2 = px.pie(df, values="Bilan CO2 (T)", names="Machine", hole=0.4)
    st.plotly_chart(fig_co2, use_container_width=True)

# --- 8. TABLEAU DE BORD DÉTAILLÉ ---
st.subheader("📋 Rapport Analytique Complet")
st.table(df)

# --- 9. BOUTON DE SIMULATION IOT (POUR TEST) ---
if not mode_iot:
    if st.button("Simuler une variation de charge (Test sans capteurs)"):
        for m in st.session_state.iot_data:
            st.session_state.iot_data[m] = machines_base[m]["p"] * (1 + (pd.Series([random.uniform(-0.1, 0.1)]))[0])
        st.rerun()
