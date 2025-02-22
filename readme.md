Api's
    *Her bir grup için jürilerin sıralama yapması.
    *POST http://localhost:8000/api/rank-group/ 
    {
    "group_id": 14,
    "judge_id": 3,
    "rank": [20, 19]
    }

    *Etabı idsi verilen etap gruplara bölünmesi ve bölünmüş ise cevabı verilmesi.
    *POST http://localhost:8000/api/split-groups/
    {"stage_id": 1, 
    "randomize": true
    }

    *Etabı idsi verilen etap gruplara bölünmesi ve bölünmüş ise cevabı verilmesi.
    *POST http://localhost:8000/api/complete-stage/
    {"stage_id": 1}# django_dance_coompetition


**
source venv/bin/activate
**
admin panali ile yarışma oluşturma adımları :
    1.Admin yarışmacılarıin datasını admin panelinden girer.gerekli bilgiler.
        -isim
    2.Admin jürileri datasını admşn panelinden girer.
        -isim 
        -şifre
    3.Admin gerekli bilglieri girerek yarışmayı oluşturur.gerekli bilgiler:
        -yarışma isimi
        -toplam katılımcı sayısı
        -yarışmaya katılan yarışmacıları ekler
        -jürileri atar [seçilebilir olmalı]
    4.Stagleri düzenlme ve ekleme ekranından admin seçtiği yarışmanın staglerini düzenşler ve ekler. gerekli bilglier :
        -yarışma [seçilebilir olmalı]
        -total staage sayısı.
        -sage iismleri
        -sage gruplara bölünmesi için istenilen grup büyüklüğü
        -bir sonraki sage e geçicek kişi sayısı
    5.tüm bu işlemler bittiğinde yarışmaya katılmış aktif olarn tüm yarışmacılar 1.sage kayıt edilir. 

1.yarışmaının admin panali üzerinden tüm  gerekli işlemleri yapıldıktan sonra işleyiş başlıyor.
2.Api yarışmanın bu satge inde bulunan yarışmacıları bu stage içinde gruplara böler.
3.Api kullanarak jüriler her bir grubukendi içimndeki yarışmacılarını sıralar. 
4.api ile etap bitirilir ve bir sonraki stage e geçicek insanlar belirlenir. eğer sonraki satage geçicek olan yarışmacı sayısı 0 ise yarışma bitiriir
5.Api yarışmanın bu satge inde bulunan yarışmacıları bu stage içinde gruplara böler.
6.Api kullanarak jüriler her bir grubukendi içimndeki yarışmacılarını sıralar.
7.api ile etap bitirilir ve bir sonraki stage e geçicek insanlar belirlenir. eğer sonraki satage geçicek olan yarışmacı sayısı 0 ise yarışma bitiriir


 python3 manage.py makemigrations
 python3 manage.py migrate
 python3 manage.py runserver