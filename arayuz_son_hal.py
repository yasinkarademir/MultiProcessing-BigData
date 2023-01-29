import os
import tkinter as tk
from tkinter.ttk import Combobox
from tkinter import *
from tkinter import ttk

from tkinter import Canvas
import time
import multiprocessing as mp
import csv


# benzerlik oranı hesaplayan fonksiyon
def benzerlik_tespiti(cumle1, cumle2):
    cumle1 = str(cumle1)
    cumle2 = str(cumle2)
    cumle1 = cumle1.split()
    cumle2 = cumle2.split()
    payda = 0
    if len(cumle1) < len(cumle2):
        payda = len(cumle2)
    else:
        payda = len(cumle1)

    pay = 0
    for i in cumle1:
        if i in cumle2:
            pay += 1
    return int((pay / payda) * 100)


def senaryo(benzerlik_orani, sutun_adi, baslangic, bitis, thread_no):
    print('başladı')
    start = time.time()
    veriler = csv.reader(open('sutunlar/' + sutun_adi + '.csv'))
    veriler = list(veriler)[0]
    bastirilacak_kayitlar = []

    end = len(veriler)
    for i in range(baslangic, bitis):

        for j in range(0, end):
            rate = benzerlik_tespiti(veriler[i], veriler[j])
            # print(veriler[i], veriler[j])
            # print(rate)

            if rate >= benzerlik_orani:
                bastirilacak_kayitlar.append(veriler[j])
    print('sonlandı')

    with open('sutunlar/Bastirilacak_kayitlar' + str(thread_no) + '.csv', mode='a+') as yeni_dosya:
        yeni_yazici = csv.writer(yeni_dosya, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        yeni_yazici.writerow(bastirilacak_kayitlar)
    end = time.time()
    print(end - start)


def senaryo_process(benzerlik_orani, sutun_adi, thread_sayisi, okuyucu):
    veriler = csv.reader(open('sutunlar/' + sutun_adi + '.csv'))
    veriler = list(veriler)[0]

    processes = []
    rows_per_thread = (len(veriler)) // thread_sayisi
    for thread_no in range(thread_sayisi):
        baslangic = rows_per_thread * thread_no
        bitis = rows_per_thread * (thread_no + 1)
        p = mp.Process(target=senaryo,
                       args=(benzerlik_orani, sutun_adi, baslangic, bitis, thread_no))

        p.start()
        processes.append(p)
    for process in processes:
        process.join()

    reader_bastirilacak = csv.reader(open('sutunlar/Bastirilacak_kayitlar.csv', 'r'))
    reader_bastirilacak = list(reader_bastirilacak)
    return reader_bastirilacak


def kayit_oku(bastirilacaklar, sutun_adi, baslangic, bitis, okuyucu, thread_no):
    sayac = 0
    dosyaya_yazilacaklar = []

    for i in bastirilacaklar:
        for j in i:
            for k in okuyucu[baslangic:bitis]:
                if j == k[okuyucu[0].index(sutun_adi)]:
                    sayac += 1
                    dosyaya_yazilacaklar.append(k)
                    # print(k)
    dosyaya_yaz = open('sonuclar/sonuc' + str(thread_no) + '.csv', 'a')
    writer = csv.writer(dosyaya_yaz)
    for t in dosyaya_yazilacaklar:
        # dosyaya_yaz.write(t)  # buraya bakılacak
        # print(type(t))
        # dosyaya_yaz.write('\n')
        writer.writerow(t)

    dosyaya_yaz.close()


def kayitlari_getir(benzerlik_orani, sutun_adi, thread_sayisi, okuyucu):
    bastirilacaklar = senaryo_process(benzerlik_orani, sutun_adi, thread_sayisi, okuyucu)
    processes = []
    rows_per_thread = (len(okuyucu) // thread_sayisi)

    for thread_no in range(thread_sayisi):
        baslangic = rows_per_thread * thread_no
        bitis = rows_per_thread * (thread_no + 1)
        p = mp.Process(target=kayit_oku,
                       args=(bastirilacaklar, sutun_adi, baslangic, bitis, okuyucu, thread_no))
        p.start()
        processes.append(p)
    for process in processes:
        process.join()
    # os.remove('sutunlar/Bastirilacak_kayitlar.csv')


def senaryo_1(benzerlik_orani, sutun_adi, thread_sayisi, okuyucu):
    kayitlari_getir(benzerlik_orani, sutun_adi, thread_sayisi, okuyucu)
    veriler = []

    for i in range(thread_sayisi):
        dosya_adi = 'sonuclar/sonuc' + str(i) + '.csv'
        dosya = csv.reader(open('sonuclar/sonuc' + str(i) + '.csv'))
        dosya = list(dosya)
        veriler.extend(dosya)
        os.remove(dosya_adi)

    root = tk.Tk()
    root.title('veriler')
    root.geometry("800x800")
    my_tree = ttk.Treeview(root, selectmode='browse', height=140)
    verscrlbar = ttk.Scrollbar(root, orient="vertical", command=my_tree.yview, cursor="hand2",
                               style="mystyle.Vertical.TScrollbar")
    verscrlbar.place(x=1720, y=20, height=900)
    my_tree.configure(xscrollcommand=verscrlbar.set)
    my_tree['columns'] = ("Product", "Issue", "Company", "State", "ZIP code", "Complaint ID")
    my_tree.column("#0", width=0, minwidth=0)
    my_tree.column("Product", anchor=W, width=450)
    my_tree.column("Issue", anchor=CENTER, width=450)
    my_tree.column("Company", anchor=W, width=300)
    my_tree.column("State", anchor=CENTER, width=90)
    my_tree.column("ZIP code", anchor=CENTER, width=90)
    my_tree.column("Complaint ID", anchor=CENTER, width=120)

    my_tree.heading("#0", text="Label", anchor=W)
    my_tree.heading("Product", text="Product", anchor=W)
    my_tree.heading("Issue", text="Issue", anchor=CENTER)
    my_tree.heading("Company", text="Company", anchor=W)
    my_tree.heading("State", text="State", anchor=CENTER)
    my_tree.heading("ZIP code", text="ZIP code", anchor=CENTER)
    my_tree.heading("Complaint ID", text="Complaint ID", anchor=CENTER)

    count = 0
    for record in veriler:
        my_tree.insert(parent='', index='end', iid=count, text="",
                       values=(record[0], record[1], record[2], record[3], record[4], record[5]))
        count += 1

    my_tree.pack(pady=20)
    root.mainloop()


okuyucu = csv.reader(open('rows2.csv', 'r'))
okuyucu = list(okuyucu)

form = tk.Tk()
form.title("YazLab2")
form.geometry("1200x800")

# def yazdir():
#     print(benzerlik_sutunu_degeri.get())
#     print(thread_sayisi_degeri.get())
#     print(gelmesi_istenen_sutun_degeri.get())
#     print(benzerlik_orani_degeri.get())

# *********************_thread_sayisi_****************************************
thread_sayisi_degeri = tk.IntVar()
thread_sayisi_label = tk.Label(form, text="Thread Sayisi: ", font=("Arial", 12), fg="black", bg="grey")
thread_sayisi_label.place(x=10, y=10)
thread_sayisi_entry = tk.Entry(form, width=10, font=("Arial", 12), textvariable=thread_sayisi_degeri).place(x=140, y=10)

# *********************_senaryolar_****************************************
# *********************_senaryo_1_******************************************

sutunlar = okuyucu[0]

senaryo_1_label = tk.Label(form, text="Senaryo 1 :", font=("Arial", 12), fg="black", bg="grey").place(x=10, y=50)
senaryo_1_benzerlik_sutunu_degeri = tk.StringVar()
senaryo_1_benzerlik_orani_degeri = tk.IntVar()

ayirici_cizgi1 = Canvas(form, width=400, height=1, bg="black").place(x=10, y=80)

senaryo_1_benzerlik_sutunu_label = tk.Label(form, text="Benzerlik Sutunu :", font=("Arial", 12), fg="black", bg="grey")
senaryo_1_benzerlik_sutunu_label.place(x=10, y=90)

kutu_benzerlik_sutunu = Combobox(form, values=sutunlar, height=3, textvariable=senaryo_1_benzerlik_sutunu_degeri).place(
    x=150,
    y=90)

senaryo_1_benzerlik_orani_label = tk.Label(form, text="Benzerlik Oranı :", font=("Arial", 12), fg="black", bg="grey")
senaryo_1_benzerlik_orani_label.place(x=10, y=130)
senaryo_1_benzerlik_orani_entry = tk.Entry(form, width=10, font=("Arial", 12),
                                           textvariable=senaryo_1_benzerlik_orani_degeri)
senaryo_1_benzerlik_orani_entry.place(x=150, y=130)

senaryo_1_buton = tk.Button(form, text='Calistir', fg='black', bg='red', activebackground='green',
                            command=lambda: senaryo_1(senaryo_1_benzerlik_orani_degeri.get(),
                                                      senaryo_1_benzerlik_sutunu_degeri.get(),
                                                      thread_sayisi_degeri.get(),
                                                      okuyucu)
                            ).place(x=10, y=170)

# *********************_senaryo_2_******************************************
ayirici_cizgi2 = Canvas(form, width=400, height=1, bg="black").place(x=10, y=210)
ayirici_cizgi2 = Canvas(form, width=400, height=1, bg="black").place(x=10, y=220)
senaryo_2_label = tk.Label(form, text="Senaryo 2 :", font=("Arial", 12), fg="black", bg="grey").place(x=10, y=230)
ayirici_cizgi3 = Canvas(form, width=400, height=1, bg="black").place(x=10, y=260)
ayni_sutun_label = tk.Label(form, text="Aynı Sutun :", font=("Arial", 12), fg="black", bg="grey").place(x=10, y=270)
ayni_sutun_degeri = tk.StringVar()
kutu_ayni_sutun = Combobox(form, values=sutunlar, height=3, textvariable=ayni_sutun_degeri).place(x=150, y=270)

senaryo_2_benzerlik_orani_label = tk.Label(form, text="Benzerlik Oranı :", font=("Arial", 12), fg="black", bg="grey")
senaryo_2_benzerlik_orani_label.place(x=10, y=310)
senaryo_2_benzerlik_orani_degeri = tk.IntVar()
senaryo_2_benzerlik_orani_entry = tk.Entry(form, width=10, font=("Arial", 12),
                                           textvariable=senaryo_2_benzerlik_orani_degeri)
senaryo_2_benzerlik_orani_entry.place(x=150, y=310)
senaryo_2_benzerlik_sutunu_label = tk.Label(form, text="Benzerlik Sutunu :", font=("Arial", 12), fg="black", bg="grey")
senaryo_2_benzerlik_sutunu_label.place(x=10, y=350)
senaryo_2_benzerlik_sutunu_degeri = tk.StringVar()
kutu_benzerlik_sutunu = Combobox(form, values=sutunlar, height=3, textvariable=senaryo_2_benzerlik_sutunu_degeri)
kutu_benzerlik_sutunu.place(x=150, y=350)
senaryo_2_getirilecek_sutun_label = tk.Label(form, text="Getirilecek Sutun :", font=("Arial", 12), fg="black",
                                             bg="grey")
senaryo_2_getirilecek_sutun_label.place(x=10, y=390)
senaryo_2_getirilecek_sutun_degeri = tk.StringVar()
kutu_getirilecek_sutun = Combobox(form, values=sutunlar, height=3, textvariable=senaryo_2_getirilecek_sutun_degeri)
kutu_getirilecek_sutun.place(x=150, y=390)
# senaryo_2_buton = tk.Button(form, text='Calistir', fg='black', bg='red', activebackground='green',command=

form.mainloop()
