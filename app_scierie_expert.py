import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURATION ---
st.set_page_config(page_title="Rentabilité par Essence", layout="wide")

st.title("🌲 WoodEnergy Pro : Rentabilité par Essence de Bois")
st.markdown("Analyse du coût de revient dynamique selon la dureté des matériaux.")

# --- DATASET DES ESSENCES ---
essences = {
    "Sapin/Épicéa (Tendre)": {"coeff_effort": 1.0, "vitesse_relative": 1.2},
    "Pin (Moyen)": {"coeff_effort": 1.1, "vitesse_relative": 1.0},
    "Hêtre (Dur)": {"coeff_effort": 1.4, "vitesse_relative": 0.7},
    "Chêne (Très dur)": {"coeff_effort": 1.6, "vitesse_relative": 0.6}
}

# --- SIDEBAR ---
st.sidebar.header("📋 Paramètres de Production")
essence_choisie = st.sidebar.selectbox("Essence de bois sciée", list(essences.keys()))
tarif_kwh = st.sidebar.number_input("Tarif Électricité (€/kWh)", value=0.18)
volume_cible = st.sidebar.number_input("Volume à produire (m³)", value=500)

# Récupération des coefficients
coeff = essences[essence_choisie]["coeff_effort"]
vitesse = essences[essence_choisie]["vitesse_relative"]

# --- CALCULS ---
data_machines = {
    "Machine": ["Scie de tête", "Déligneuse", "Aspiration", "Séchoir", "Convoyeurs"],
    "Puissance_kW":,
    "Base_Charge": [0.65, 0.50, 0.90, 0.85, 0.40]
}
df = pd.DataFrame(data_machines)

# L'effort moteur augmente avec la dureté, et le temps de sciage s'allonge (vitesse relative)
df['Charge_Ajustee'] = df['Base_Charge'] * coeff
df['Charge_Ajustee'] = df['Charge_Ajustee'].clip(upper=1.0) # On ne peut pas dépasser 100% de la puissance

# Temps de fonctionnement estimé pour produire le volume cible
heures_necessaires = (volume_cible / (10 / vitesse)) # Base de 10m3/h pour du bois standard

df['Conso_Totale_kWh'] = df['Puissance_kW'] * heures_necessaires * df['Charge_Ajustee']
df['Cout_Total_Euro'] = df['Conso_Totale_kWh'] * tarif_kwh
df['Cout_par_m3'] = df['Cout_Total_Euro'] / volume_cible

# --- AFFICHAGE ---
st.subheader(f"Analyse pour : {essence_choisie}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Temps de sciage estimé", f"{heures_necessaires:.1f} h")
c2.metric("Coût Énergie Total", f"{df['Cout_Total_Euro'].sum():,.2f} €")
c3.metric("Coût de revient / m³", f"{df['Cout_par_m3'].sum():.2f} €/m³")
c4.metric("Surcoût Énergie (vs Sapin)", f"{((coeff/1.0)-1)*100:.0f} %")

# --- GRAPHIQUE COMPARATIF ---
fig = px.bar(df, x='Machine', y='Cout_par_m3', 
             title=f"Répartition du coût par m³ ({essence_choisie})",
             color='Cout_par_m3', color_continuous_scale='YlOrRd')
st.plotly_chart(fig, use_container_width=True)

# --- TABLEAU ANALYTIQUE ---
st.write("### Détail technique par machine")
st.table(df[['Machine', 'Puissance_kW', 'Charge_Ajustee', 'Cout_par_m3']])
