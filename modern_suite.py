import pandas as pd

def get_modern_drugs_database():
    """
    Erstellt die Datenbank für die aktuellen Blockbuster (2023-2026)
    basierend auf deinen Kriterien und Gewichtungen.
    """
    # Spalten: Name, Efficacy(30), Safety(25), DataQuality(15), Consistency(18), Power(12)
    modern_drugs = [
        {
            'Name': 'Ozempic/Mounjaro (Semaglutide)',
            'Efficacy': 75, 'Safety': 45, 'Data_Quality': 40, 'Consistency': 50, 'Power': 80,
            'Off_Label_Rate': 0.60, 'Current_Cost_Billions': 3.0
        },
        {
            'Name': 'Lecanemab (Leqembi)',
            'Efficacy': 30, 'Safety': 20, 'Data_Quality': 30, 'Consistency': 40, 'Power': 75,
            'Off_Label_Rate': 0.10, 'Current_Cost_Billions': 2.0
        },
        {
            'Name': 'Paxlovid',
            'Efficacy': 80, 'Safety': 60, 'Data_Quality': 70, 'Consistency': 55, 'Power': 85,
            'Off_Label_Rate': 0.45, 'Current_Cost_Billions': 1.5
        },
        {
            'Name': 'Leqvio (Inclisiran)',
            'Efficacy': 55, 'Safety': 70, 'Data_Quality': 50, 'Consistency': 60, 'Power': 70,
            'Off_Label_Rate': 0.05, 'Current_Cost_Billions': 0.8
        },
        {
            'Name': 'Finerenone (Kerendia)',
            'Efficacy': 45, 'Safety': 75, 'Data_Quality': 55, 'Consistency': 65, 'Power': 68,
            'Off_Label_Rate': 0.02, 'Current_Cost_Billions': 0.5
        }
    ]
    return pd.DataFrame(modern_drugs)

class ADAVIDModernValidator:
    def __init__(self, df):
        self.df = df

    def run_audit(self):
        results = []
        total_savings = 0
        
        for idx, row in self.df.iterrows():
            # Exakte Berechnung nach deinem Gewichtungsschlüssel:
            score = (
                (row['Efficacy'] * 0.30) +
                (row['Safety'] * 0.25) +
                (row['Data_Quality'] * 0.15) +
                (row['Consistency'] * 0.18) +
                (row['Power'] * 0.12)
            )
            
            # Status & Einsparungs-Logik ermitteln
            if score < 40:
                status = '🔴 REJECTED'
                savings_pct = 0.80  # 80% Einsparung (nur noch strengste Forschung)
            elif score < 65:
                status = '🟡 CONDITIONAL'
                savings_pct = row['Off_Label_Rate']  # Wir sparen exakt die Off-Label-Kosten ein!
            else:
                status = '✅ APPROVED'
                savings_pct = 0.0
                
            saved_money = row['Current_Cost_Billions'] * savings_pct
            total_savings += saved_money
            
            results.append({
                'Medikament': row['Name'],
                'ADAVID_Score': round(score, 1),
                'Status': status,
                'Kosten Aktuell (€B)': row['Current_Cost_Billions'],
                'Einsparung (€B)': round(saved_money, 2)
            })
            
        return pd.DataFrame(results), total_savings

if __name__ == "__main__":
    print("====================================================")
    print("🔥 ADAVID MODERN BLOCKBUSTER AUDIT (2023-2026)")
    print("====================================================\n")
    
    db = get_modern_drugs_database()
    validator = ADAVIDModernValidator(db)
    scored_df, savings = validator.run_audit()
    
    print(scored_df.to_string(index=False))
    
    print("\n----------------------------------------------------")
    print(f"💰 HOCHRECHNUNG FINANZIELLER IMPACT (TOP 5 MARKER):")
    print(f"   Errechnete Ersparnis im ersten Jahr: €{round(savings, 2)} Milliarden.")
    print("----------------------------------------------------")
