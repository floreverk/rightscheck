import pandas as pd
import numpy as np
import datetime
from tkinter import filedialog
from tkinter.ttk import *
from tkinter import *

hva_im_app = Tk()
hva_im_app.title('rechtencheck')


def info():
    infowindow = Toplevel()
    infolabel = Label(infowindow, text="Neem een export uit adlib met volgende kolommen: \n\nobjectnummer"
                                       "\nvervaardiger\nvervaardiging.datum.begin\nvervaardiging.datum.eind"
                                       "\nassociatie.periode\nonderscheidende_kenmerken\n\nAls format wordt gekozen "
                                       "voor een csv met bij instellingen als veldscheiding ';'. ", justify=LEFT)
    infolabel.grid(row=0, column=0)


def openfile():
    file = filedialog.askopenfilename(title="select file")
    return file


def save_file():
    location = filedialog.askdirectory(title="save file")
    blank2 = Label(hva_im_app, text="", bg="#eff0eb")
    blank2.grid(column=1, row=8)
    show_location = Label(hva_im_app, text='de output kan je hier vinden: ' + location, bg="#eff0eb")
    show_location.grid(column=1, row=9)
    return location


def choose():
    df = pd.read_csv(openfile(), delimiter=";")

    # A. datering selecteren:

    # 1. einddatum
    ed = df[df['vervaardiging.datum.eind'].notna()]
    ed['Datering'] = ed['vervaardiging.datum.eind']
    ed['Datering'] = ed['Datering'].astype(str)
    ed['Datering'] = ed['Datering'].str[:4]

    # 2. begindatum

    bd = pd.isna(df['vervaardiging.datum.eind'])
    bd = df[bd]
    bd['Datering'] = bd['vervaardiging.datum.begin']
    bd['Datering'] = bd['Datering'].astype(str)
    bd['Datering'] = bd['Datering'].str[:4]
    bd = bd.dropna(subset=['Datering'])

    # 3. associatie.periode 1

    ap = pd.isna(bd['vervaardiging.datum.begin'])
    ap = bd[ap]
    ap['associatie.periode'] = ap['associatie.periode'].str.replace('17de eeuw', 'jaren 1691')
    ap['associatie.periode'] = ap['associatie.periode'].str.replace('19de eeuw', 'jaren 1891')
    ap['associatie.periode'] = ap['associatie.periode'].str.replace('18de eeuw', 'jaren 1791')
    ap[['jaren', 'associatie.periode']] = ap['associatie.periode'].str.split(' ', 1, expand=True)
    ap['Datering'] = ap['associatie.periode']
    ap.drop(['jaren'], axis=1, inplace=True)
    ap['Datering'] = ap['Datering'].str[-4:]
    ap = ap.dropna(subset=['Datering'])
    ap['Datering'] = ap['Datering'].astype(int)
    ap['Datering'] = ap['Datering'] + 9
    ap['Datering'] = ap['Datering'].astype(str)

    # 4. drop duplicates

    da = pd.concat([ap, ed, bd])
    da = da.drop_duplicates(subset=['objectnummer'], keep='first')

    # B. rechtencontrole

    # huidig jaartal
    now = datetime.datetime.now().year

    # publiek domein
    da['Datering'] = da['Datering'].astype(float)
    da['rechten1'] = np.where(da['Datering'] < (now - 150), 'Publiek Domein', "")

    # ontbrekende vervaardigers/datering
    da['vervaardiger'] = da['vervaardiger'].fillna(0)
    da['vervaardiger'] = da['vervaardiger'].replace('onbekend', 0)
    da['Datering'] = da['Datering'].fillna(0)

    # Anonieme werken
    da['rechten2'] = np.where(
        (da['Datering'] < (now - 70)) & (da['Datering'] >= (now - 150)) & (da["vervaardiger"] == 0) &
        (da["onderscheidende_kenmerken"] == "OBJECT"), 'Publiek Domein - anonieme werken', "")

    # ICUR objecten
    da['rechten3'] = np.where((da['Datering'] >= (now - 70)) & (da['onderscheidende_kenmerken'] == "OBJECT") &
                              (da["vervaardiger"] == 0), "IN COPYRIGHT UNKNOWN RIGHTSHOLDER", "")
    da['einddatum1'] = np.where((da['rechten3'] == 'IN COPYRIGHT UNKNOWN RIGHTSHOLDER') & (da['Datering'] != 0),
                                da['Datering'] + 71, "")

    # ICUR
    da['rechten4'] = np.where((da['Datering'] == 0) & (da["vervaardiger"] == 0), "IN COPYRIGHT UNKNOWN RIGHTSHOLDER",
                              "")
    da['einddatum2'] = np.where((da['rechten4'] == 'IN COPYRIGHT UNKNOWN RIGHTSHOLDER') & (da['Datering'] != 0),
                                da['Datering'] + 151, "")
    da['rechten7'] = np.where((da['Datering'] >= (now - 150)) & (da["vervaardiger"] == 0) &
                              (da["onderscheidende_kenmerken"] != "OBJECT"), "IN COPYRIGHT UNKNOWN RIGHTSHOLDER", "")
    da['einddatum3'] = np.where((da['rechten7'] == 'IN COPYRIGHT UNKNOWN RIGHTSHOLDER') & (da['Datering'] != 0),
                                da['Datering'] + 151, "")
    # IN COPYRIGHT
    da['rechten5'] = np.where(
        (da["Datering"] >= (now - 150)) & (da['Datering'] < (now - 70)) & (da["vervaardiger"] != 0) &
        (da["onderscheidende_kenmerken"] == "OBJECT"),
        "IN COPYRIGHT - check sterftedatum vervaardiger, mogelijkheid gebruiksvoorwerp", "")
    da['rechten6'] = np.where((da['Datering'] >= (now - 70)) & (da["vervaardiger"] != 0) &
                              (da["onderscheidende_kenmerken"] == "OBJECT"),
                              "IN COPYRIGHT - check sterftedatum vervaardiger", "")
    da['rechten8'] = np.where((da['Datering'] >= (now - 150)) & (da["vervaardiger"] != 0) &
                              (da["onderscheidende_kenmerken"] != "OBJECT"),
                              "IN COPYRIGHT - check sterftedatum vervaardiger", "")
    da['rechten9'] = np.where((da['Datering'] == 0) & (da["vervaardiger"] != 0) &
                              (da["onderscheidende_kenmerken"] != "OBJECT"),
                              "IN COPYRIGHT - check sterftedatum vervaardiger", "")
    da['rechten10'] = np.where((da['Datering'] == 0) & (da["onderscheidende_kenmerken"] == "OBJECT") &
                               (da["vervaardiger"] != 0), "IN COPYRIGHT - check sterftedatum vervaardiger", "")

    # kolommen samenvoegen
    da["rechten"] = da["rechten1"] + da['rechten2'] + da['rechten3'] + da['rechten4'] + da['rechten5'] + \
                    da['rechten6'] + da['rechten7'] + da['rechten8'] + da['rechten9'] + da["rechten10"]
    da.drop(['rechten1', 'rechten2', 'rechten3', 'rechten4', 'rechten5', 'rechten6', 'rechten7', 'rechten8',
             'rechten9', 'rechten10'], axis=1, inplace=True)

    da['einddatum'] = da['einddatum1'] + da['einddatum2'] + da['einddatum3']
    da.drop(['einddatum1'] + ['einddatum2'] + ['einddatum3'], axis=1, inplace=True)
    da['einddatum'] = da['einddatum'].astype(str)
    da['einddatum'] = da['einddatum'].str[:-2]
    da.to_excel(save_file() + r'/output.xlsx', index=False)


hva_im_app.configure(bg="#eff0eb")
hva_im_app.geometry("900x550")

Info = Label(text="Klik om csv op te laden:", bg="#eff0eb")
Info.grid(row=0, column=1)

blank6 = Label(text="", bg="#eff0eb")
blank6.grid(row=2, column=1)

startknop = Button(hva_im_app, text="csv opladen", padx=20, pady=10, borderwidth=4, bg="#eacb48", command=choose)
startknop.grid(row=3, column=1)

buttoninfo = Button(hva_im_app, text="Info", borderwidth=4, bg="#c5c1bb", command=info)
buttoninfo.grid(row=1, column=0)

hva_im_app.mainloop()
