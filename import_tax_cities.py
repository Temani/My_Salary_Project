import pandas as pd
from app import app, db  # מייבא את האפליקציה ואת מסד הנתונים שלך
from models import TaxExemptCity  # מייבא את המודל של הטבלה החדשה



# קריאה לקובץ ה-Excel
file_path = "public_announcment_pa110124.xlsx"
df = pd.read_excel(file_path, skiprows=2)



# שינוי שמות העמודות והתאמה לפורמט שלך
df.columns = ['city_code', 'city_name', 'score', 'tax_discount_percent', 'annual_cap']
df = df[['city_name', 'tax_discount_percent', 'annual_cap']]
df = df.dropna(subset=["city_name"])
df["tax_discount_percent"] = df["tax_discount_percent"].astype(float)
df["annual_cap"] = df["annual_cap"].astype(float)

# הכנסת הנתונים למסד הנתונים
with app.app_context():
    for _, row in df.iterrows():
        city_name = row["city_name"].strip()
        if not TaxExemptCity.query.filter_by(city_name=city_name).first():
            city = TaxExemptCity(
                city_name=city_name,
                tax_discount_percent=row["tax_discount_percent"],
                annual_cap=row["annual_cap"]
            )
            db.session.add(city)
    db.session.commit()

print("✅ הנתונים נשמרו בהצלחה בטבלה tax_exempt_cities.")
