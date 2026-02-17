import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Gestion Énergétique Scierie", layout="wide")

st.title("🌲 WoodEnergy Analytics : Pilotage de Production")
st.markdown("---")

# --- PARAMÈTRES EN BARRE LATÉRALE ---
st.sidebar.header("Paramètres de Configuration")
tarif_kwh = st.sidebar.number_input("Tarif Électricité (€/kWh)", value=0.18, step=0.01)
jours_operation = st.sidebar.slider("Jours d'opération par mois", 1, 31, 22)
heures_jour = st.sidebar.slider("Heures de travail par jour", 1, 24, 8)

# --- DONNÉES DES MACHINES ---
# On définit les machines types d'une scierie moderne
data_machines = {
    "Machine": [
        "Scie de tête (Ruban)", "Déligneuse CNC", "Aspirateur de copeaux", 
        "Séchoir Haute Température", "Convoyeur Billons", "Tronçonneuse d'optimisation"
    ],
    "Puissance_Nominale_kW": [75, 30, 45, 110, 15, 22],
    "Facteur_Charge_Moyen": [0.65, 0.50, 0.90, 0.85, 0.40, 0.55]
}

df = pd.DataFrame(data_machines)

# --- CALCULS ANALYTIQUES ---
# Consommation Mensuelle (kWh) = Puissance * Heures * Jours * Charge
df['Conso_Mensuelle_kWh'] = (
    df['Puissance_Nominale_kW'] * heures_jour * jours_operation * df['Facteur_Charge_Moyen']
)
df['Cout_Mensuel_Euro'] = df['Conso_Mensuelle_kWh'] * tarif_kwh

# --- AFFICHAGE DES INDICATEURS CLÉS (KPI) ---
total_conso = df['Conso_Mensuelle_kWh'].sum()
total_budget = df['Cout_Mensuel_Euro'].sum()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Consommation Totale", f"{total_conso:,.0f} kWh", delta="-5% vs mois dernier")
with col2:
    st.metric("Budget Énergie Mensuel", f"{total_budget:,.2f} €", delta="Hausse tarifaire", delta_color="inverse")
with col3:
    st.metric("Nb Machines Actives", len(df))

st.markdown("---")

# --- GRAPHIQUES INTERACTIFS ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Répartition des Coûts par Machine")
    fig_pie = px.pie(df, values='Cout_Mensuel_Euro', names='Machine', 
                     hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("Analyse Puissance vs Consommation")
    fig_bar = px.bar(df, x='Machine', y='Conso_Mensuelle_kWh', 
                     text='Conso_Mensuelle_kWh', color='Cout_Mensuel_Euro')
    fig_bar.update_traces(texttemplate='%{text:.2s} kWh', textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

# --- TABLEAU DE RENTABILITÉ DÉTAILLÉ ---
st.subheader("📋 Tableau de bord analytique des coûts")
st.dataframe(df.style.format({
    'Puissance_Nominale_kW': '{:.0f} kW',
    'Facteur_Charge_Moyen': '{:.0%}',
    'Conso_Mensuelle_kWh': '{:.2f} kWh',
    'Cout_Mensuel_Euro': '{:.2f} €'
}), use_container_width=True)

# --- EXPORTATION ---
st.sidebar.download_button(
    label="Exporter le rapport (CSV)",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name='rapport_energie_scierie.csv',
    mime='text/csv',
)
