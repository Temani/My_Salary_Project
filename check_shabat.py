import pandas as pd
from app import app, db  # מייבא את האפליקציה ואת מסד הנתונים שלך
from models import Shift  # מייבא את המודל של הטבלה החדשה

file_patch = "shabat_times_2025.xlsx"
# קריאה לקובץ ה-Excel
df = pd.read_excel(file_patch)

# הדפסת הקריאה מהקובץ
# date - תאריכי החגים/שבתות
# Jerusalem_in - זמני כניסת שבת בירושלים
# Jerusalem_out - זמני יציאת שבת בירושלים

