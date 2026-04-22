import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

ticker = "AAPL"
print(f"Récupération et analyse des données pour {ticker}...")

# 1. Récupération des données
action = yf.Ticker(ticker)
data = action.history(period="6mo")

# 2. Calcul de la Moyenne Mobile (SMA 20)
data['SMA_20'] = data['Close'].rolling(window=20).mean()

# 3. NOUVEAU : Création des signaux et triangles d'achat/vente

# On initialise les colonnes de signaux à None
data['Signal_Achat'] = None
data['Signal_Vente'] = None

# Boucle pour identifier les croisements et placer les triangles
for i in range(20, len(data)): # On commence après les 20 premiers jours (nécessaires pour l'SMA_20)
    # Croisement haussier (Prix repasse au-dessus de la moyenne) -> ACHAT
    if data.iloc[i]['Close'] > data.iloc[i]['SMA_20'] and data.iloc[i-1]['Close'] <= data.iloc[i-1]['SMA_20']:
        data.at[data.index[i], 'Signal_Achat'] = data.iloc[i]['Close'] * 1.02 # Un peu au-dessus du prix pour visibilité
    
    # Croisement baissier (Prix repasse en dessous de la moyenne) -> VENTE
    elif data.iloc[i]['Close'] < data.iloc[i]['SMA_20'] and data.iloc[i-1]['Close'] >= data.iloc[i-1]['SMA_20']:
        data.at[data.index[i], 'Signal_Vente'] = data.iloc[i]['Close'] * 0.98 # Un peu en dessous du prix pour visibilité

# 4. Création du graphique visuel
print("Génération du graphique...")
plt.figure(figsize=(12, 6))

# Tracé du prix et de la moyenne
plt.plot(data.index, data['Close'], label='Prix Réel (Close)', color='blue', alpha=0.6)
plt.plot(data.index, data['SMA_20'], label='Moyenne Mobile (20 jours)', color='orange', linestyle='--')

# AJOUT DES TRIANGLES :
# 'scatter' trace des points distincts. 'marker' définit la forme, 'color' la couleur.
# s est la taille, edgecolor la couleur du bord.
plt.scatter(data.index, data['Signal_Achat'], label='Signal d\'Achat', marker='^', color='green', s=100, edgecolor='black', alpha=1)
plt.scatter(data.index, data['Signal_Vente'], label='Signal de Vente', marker='v', color='red', s=100, edgecolor='black', alpha=1)

# Décoration du graphique
plt.title(f"Analyse de Tendance avec Signaux d\'Achat/Vente pour {ticker}")
plt.xlabel("Date")
plt.ylabel("Prix (USD)")
plt.legend()
plt.grid(True, alpha=0.3)

# 5. Affichage
plt.show()