import os
import tkinter as tk
import zipfile
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
    veriler = csv.reader(open('columns/' + sutun_adi + '.csv'))
    veriler = list(veriler)[0]
    print(veriler)
    bastirilacak_kayitlar = []

    end = len(veriler)
    for i in range(baslangic, bitis):
        bastirilacaklar = []

        for j in range(0, end):
            rate = benzerlik_tespiti(veriler[i], veriler[j])
            # print(veriler[i], veriler[j])
            # print(rate)

            if rate >= benzerlik_orani:
                # bastirilacaklar.append([veriler[i], veriler[j]])
                bastirilacaklar.append(veriler[j])
        bastirilacaklar = list(bastirilacaklar)
        bastirilacak_kayitlar.append(bastirilacaklar)
    bastirilacak_kayitlar = list(bastirilacak_kayitlar)
    print('sonlandı')

    dosyaya_yaz = open('columns/Bastirilacak_kayitlar.csv', 'a')

    yeni_yazici = csv.writer(dosyaya_yaz)
    for t in bastirilacak_kayitlar:
        yeni_yazici.writerow(t)
    end = time.time()
    print(end - start)


def senaryo_process(benzerlik_orani, sutun_adi, thread_sayisi, okuyucu):
    veriler = csv.reader(open('columns/' + sutun_adi + '.csv'))
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

    reader_bastirilacak = csv.reader(open('columns/Bastirilacak_kayitlar.csv', 'r'))
    reader_bastirilacak = list(reader_bastirilacak)

    for i in reader_bastirilacak:
        print(i)
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


def kayitlari_getir(benzerlik_orani, sutun_adi, thread_sayisi, okuyucu, thread_sureleri):
    bastirilacaklar = senaryo_process(benzerlik_orani, sutun_adi, thread_sayisi, okuyucu)
    processes = []
    rows_per_thread = (len(okuyucu) // thread_sayisi)

    for thread_no in range(thread_sayisi):
        baslangic = rows_per_thread * thread_no
        bitis = rows_per_thread * (thread_no + 1)
        p = mp.Process(target=kayit_oku,
                       args=(bastirilacaklar, sutun_adi, baslangic, bitis, okuyucu, thread_no))
        start = time.time()
        p.start()

        processes.append(p)

    for process in processes:
        process.join()
        end = time.time()
        thread_sureleri.append(end - start)

    print(thread_sureleri)
    os.remove('columns/Bastirilacak_kayitlar.csv')


def senaryo_1(benzerlik_orani, sutun_adi, thread_sayisi, okuyucu):
    thread_sureleri = []
    toplam_sure_start = time.time()
    kayitlari_getir(benzerlik_orani, sutun_adi, thread_sayisi, okuyucu, thread_sureleri)
    veriler = []

    for i in range(thread_sayisi):
        dosya_adi = 'sonuclar/sonuc' + str(i) + '.csv'
        dosya = csv.reader(open('sonuclar/sonuc' + str(i) + '.csv'))
        dosya = list(dosya)
        veriler.extend(dosya)
        os.remove(dosya_adi)

    root = tk.Tk()
    root.title('SENARYO 1')
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

    toplam_sure_end = time.time()
    print(toplam_sure_end - toplam_sure_start)
    thread_sureleri.append(toplam_sure_end - toplam_sure_start)

    count = 0
    for record in veriler:
        my_tree.insert(parent='', index='end', iid=count, text="",
                       values=(record[0], record[1], record[2], record[3], record[4], record[5]))
        count += 1

    my_tree.pack(pady=20)

    root2 = tk.Tk()
    root2.title("Thread Süreleri")
    root2.geometry("300x500")
    my_tree2 = ttk.Treeview(root2, selectmode='browse', height=70)
    my_tree2['columns'] = ('Thread No', 'Thread Süresi')
    my_tree2.column("#0", width=0, stretch=NO)
    my_tree2.column('Thread No', anchor=W, width=100)
    my_tree2.column('Thread Süresi', anchor=W, width=160)

    my_tree2.heading("#0", text="", anchor=W)
    my_tree2.heading('Thread No', text='Thread No', anchor=W)
    my_tree2.heading('Thread Süresi', text='Thread Süresi', anchor=W)

    sutun_1 = []
    for i in range(len(thread_sureleri)):
        sutun_1.append(str(i))
    sutun_1.append('Toplam Süre')

    for i in range(len(thread_sureleri)):
        my_tree2.insert(parent='', index='end', iid=i, text="",
                        values=(sutun_1[i + 1], thread_sureleri[i]))
    my_tree2.pack(pady=20)
    root2.mainloop()

    root.mainloop()


# **********************************************************************************************************************
def senaryo_2(ayni_sutun, benzerlik_orani, benzerlik_sutunu, getirilecek_sutun, thread_sayisi, okuyucu,
              thread_sureleri):
    urunler = csv.reader(open('columns/' + ayni_sutun + '.csv'))
    urunler = list(urunler)[0]

    say = 0
    dosya_adi = 'columns/' + ayni_sutun + '.csv'
    urunler = csv.reader(open(dosya_adi))
    urunler = list(urunler)[0]
    for i in urunler:
        urun_konu = []
        for j in okuyucu:
            if j[okuyucu[0].index(ayni_sutun)] == i:
                if j[okuyucu[0].index(benzerlik_sutunu)] not in urun_konu:
                    urun_konu.append(j[okuyucu[0].index(benzerlik_sutunu)])

        dosyaya_yaz = open('senaryo2/' + str(i) + '.csv', 'a')

        writer = csv.writer(dosyaya_yaz)
        for t in urun_konu:
            writer.writerow([t])

        dosyaya_yaz.close()
        # print(urun_konu)

    bastirilacakalar = []
    for i in urunler:
        bastirilacaklar_iç = []
        oku = csv.reader(open('senaryo2/' + str(i) + '.csv'))
        oku = list(oku)
        os.remove('senaryo2/' + str(i) + '.csv')

        for i in range(len(oku)):
            for j in range(len(oku)):
                say += 1
                # print(oku[i][0], oku[j][0], benzerlik_tespiti(oku[i][0], oku[j][0]), say)
                if benzerlik_tespiti(oku[i][0], oku[j][0]) >= benzerlik_orani:
                    bastirilacaklar_iç.append(oku[j][0])
        bastirilacakalar.append(bastirilacaklar_iç)
        # bastirilacakalar.append(list(set(bastirilacaklar_iç)))

    # for i in bastirilacakalar:
    #     print(i)
    #     print('****************************************************************************************************')

    def senaryo_2_kayit_getir(baslangic, bitis, thread_no):
        sonuclar = []
        for i in urunler:
            # print("************************************************************************************************")
            for j in okuyucu[baslangic:bitis]:
                if j[okuyucu[0].index(ayni_sutun)] == i:
                    for k in bastirilacakalar[urunler.index(i)]:
                        if j[okuyucu[0].index(benzerlik_sutunu)] == k:
                            # print(j[okuyucu[0].index(ayni_sutun)], j[okuyucu[0].index(getirilecek_sutun)])
                            sonuclar.append(j[okuyucu[0].index(getirilecek_sutun)])
        dosyaya_yaz = open('senaryo2/sonuclar' + str(thread_no) + '.csv', 'a')
        writer = csv.writer(dosyaya_yaz)
        for i in sonuclar:
            writer.writerow([i])
        dosyaya_yaz.close()

    rows_per_thread = (len(okuyucu)) // thread_sayisi
    processes = []
    for thread_no in range(thread_sayisi):
        baslangic = rows_per_thread * thread_no
        bitis = rows_per_thread * (thread_no + 1)
        p = mp.Process(target=senaryo_2_kayit_getir,
                       args=(baslangic, bitis, thread_no))
        processes.append(p)

        start_ic = time.time()
        p.start()
        for process in processes:
            process.join()

        start_dis = time.time()
        thread_sureleri.append(start_dis - start_ic)


def senaryo_2_pencere(ayni_sutun, benzerlik_orani, benzerlik_sutunu, getirilecek_sutun, thread_sayisi, okuyucu):
    thread_sureleri = []
    # senaryo_2('Product', 70, 'Issue', 'Company', 4, okuyucu)
    baslangic = time.time()
    senaryo_2(ayni_sutun, benzerlik_orani, benzerlik_sutunu, getirilecek_sutun, thread_sayisi, okuyucu, thread_sureleri)

    veriler = []
    for i in range(thread_sayisi):
        dosya = csv.reader(open('senaryo2/sonuclar' + str(i) + '.csv'))
        os.remove('senaryo2/sonuclar' + str(i) + '.csv')
        dosya = list(dosya)
        veriler.extend(dosya)
    bitis = time.time()
    print(thread_sureleri)
    print(bitis - baslangic)
    toplam_sure = bitis - baslangic

    root = tk.Tk()
    root.title("Senaryo 2")
    root.geometry("800x800")
    my_tree = ttk.Treeview(root, selectmode='browse', height=140)
    verscrlbar = ttk.Scrollbar(root, orient="vertical", command=my_tree.yview, cursor="hand2",
                               style="mystyle.Vertical.TScrollbar")
    verscrlbar.place(x=780, y=0, height=800)
    my_tree['columns'] = (getirilecek_sutun)
    my_tree.column("#0", width=0, stretch=NO)
    my_tree.column(getirilecek_sutun, anchor=W, width=300)

    my_tree.heading("#0", text="", anchor=W)
    my_tree.heading(getirilecek_sutun, text=getirilecek_sutun, anchor=W)

    count = 0
    for record in veriler:
        my_tree.insert(parent='', index='end', iid=count, text="",
                       values=(record[0]))
        count += 1

    my_tree.pack(pady=20)

    root2 = tk.Tk()
    root2.title("Thread Süreleri")
    root2.geometry("300x500")
    my_tree2 = ttk.Treeview(root2, selectmode='browse', height=70)
    my_tree2['columns'] = ('Thread No', 'Thread Süresi')
    my_tree2.column("#0", width=0, stretch=NO)
    my_tree2.column('Thread No', anchor=W, width=100)
    my_tree2.column('Thread Süresi', anchor=W, width=160)

    my_tree2.heading("#0", text="", anchor=W)
    my_tree2.heading('Thread No', text='Thread No', anchor=W)
    my_tree2.heading('Thread Süresi', text='Thread Süresi', anchor=W)

    thread_sureleri.append(toplam_sure)
    sutun_1 = []
    for i in range(len(thread_sureleri)):
        sutun_1.append(str(i))
    sutun_1.append('Toplam Süre')

    for i in range(len(thread_sureleri)):
        my_tree2.insert(parent='', index='end', iid=i, text="",
                        values=(sutun_1[i + 1], thread_sureleri[i]))
    my_tree2.pack(pady=20)
    root2.mainloop()

    root.mainloop()


# **********************************************************************************************************************
def senaryo_3(benzerlik_orani, complaint_id, okuyucu, benzerlik_sutunu):
    start_toplam_sure = time.time()
    okuyucu_sutunlar_benzerlik = csv.reader(open('columns/' + benzerlik_sutunu + '.csv'))
    okuyucu_sutunlar_benzerlik = list(okuyucu_sutunlar_benzerlik)[0]

    konu = ''
    for i in okuyucu:
        ara = i[okuyucu[0].index('Complaint ID')]
        if ara == complaint_id:
            konu = i[okuyucu[0].index(benzerlik_sutunu)]
            # print(i)
            # print(konu)

    bastirilacaklar = []
    sonuclar = []
    for i in okuyucu_sutunlar_benzerlik:
        if benzerlik_tespiti(konu, i) >= benzerlik_orani:
            bastirilacaklar.append(i)
    print(bastirilacaklar)

    for i in okuyucu:
        if i[okuyucu[0].index(benzerlik_sutunu)] in bastirilacaklar:
            sonuclar.append(i)
            # print(i)

    end_toplam_sure = time.time()
    print("Toplam Süre: ", end_toplam_sure - start_toplam_sure)

    root = tk.Tk()
    root.title("Senaryo 3")
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
    for kayit in sonuclar:
        my_tree.insert(parent='', index='end', iid=count, text="",
                       values=(kayit[0], kayit[1], kayit[2], kayit[3], kayit[4], kayit[5]))
        count += 1

    my_tree.pack(pady=20)

    end_toplam_sure_label = tk.Label(root, text="Toplam Süre: " + str(end_toplam_sure - start_toplam_sure))
    end_toplam_sure_label.place(x=10, y=0)

    root.mainloop()


zip_path = "rows2.zip"
csv_file_name = "rows2.csv"
with zipfile.ZipFile(zip_path, 'r') as zfile:
    zfile.extractall()

okuyucu = csv.reader(open(csv_file_name, 'r'))
okuyucu = list(okuyucu)

form = tk.Tk()
form.title("YazLab2")
form.geometry("1200x800")
#


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
senaryo_2_buton = tk.Button(form, text='Calistir', fg='black', bg='red', activebackground='green', command=
lambda: senaryo_2_pencere(ayni_sutun_degeri.get(), senaryo_2_benzerlik_orani_degeri.get(),
                          senaryo_2_benzerlik_sutunu_degeri.get(),
                          senaryo_2_getirilecek_sutun_degeri.get(),
                          thread_sayisi_degeri.get(), okuyucu)).place(x=10, y=430)

# *********************_senaryo_3_******************************************
ayirici_cizgi4 = Canvas(form, width=400, height=1, bg="black").place(x=10, y=470)
ayirici_cizgi4 = Canvas(form, width=400, height=1, bg="black").place(x=10, y=480)
senaryo_3_label = tk.Label(form, text="Senaryo 3 :", font=("Arial", 12), fg="black", bg="grey").place(x=10, y=490)
ayirici_cizgi5 = Canvas(form, width=400, height=1, bg="black").place(x=10, y=520)
senaryo_3_benzerlik_orani_degeri = tk.IntVar()
senaryo_3_benzerlik_orani_label = tk.Label(form, text="Benzerlik Oranı :", font=("Arial", 12), fg="black", bg="grey")
senaryo_3_benzerlik_orani_label.place(x=10, y=530)
senaryo_3_benzerlik_orani_entry = tk.Entry(form, width=10, font=("Arial", 12),
                                           textvariable=senaryo_3_benzerlik_orani_degeri)
senaryo_3_benzerlik_orani_entry.place(x=150, y=530)
senaryo_3_complaint_id_label = tk.Label(form, text="Complaint ID :", font=("Arial", 12), fg="black", bg="grey")
senaryo_3_complaint_id_label.place(x=10, y=570)
senaryo_3_complaint_id_degeri = tk.StringVar()
complaint_id_entry = tk.Entry(form, width=10, font=("Arial", 12), textvariable=senaryo_3_complaint_id_degeri)
complaint_id_entry.place(x=150, y=570)

senaryo_3_benzerlik_sutunu_label = tk.Label(form, text="Benzerlik Sutunu :", font=("Arial", 12), fg="black", bg="grey")
senaryo_3_benzerlik_sutunu_label.place(x=10, y=610)
senaryo_3_benzerlik_sutunu_degeri = tk.StringVar()

kutu_benzerlik_sutunu = Combobox(form, values=sutunlar, height=3, textvariable=senaryo_3_benzerlik_sutunu_degeri)
kutu_benzerlik_sutunu.place(x=150, y=610)
senaryo_3_buton = tk.Button(form, text='Calistir', fg='black', bg='red', activebackground='green',
                            command=lambda: senaryo_3(senaryo_3_benzerlik_orani_degeri.get(),
                                                      senaryo_3_complaint_id_degeri.get(), okuyucu,
                                                      senaryo_3_benzerlik_sutunu_degeri.get())).place(x=10, y=650)

form.mainloop()
