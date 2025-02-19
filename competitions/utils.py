import random
from .models import Group, Contestant

def split_contestants_into_groups(stage, contestants=None, randomize=True):
    """
    Belirtilen etap (stage) için yarışmacıları verilen grup boyutuna göre gruplara ayırır.
    
    Parametreler:
      - stage: Bölünme yapılacak Stage nesnesi.
      - contestants: Eğer belirtilmezse, stage.competition.contestants.all() kullanılır.
      - randomize: True ise yarışmacı sırası karıştırılır, False ise sıralama korunur.
    
    Fonksiyon, mevcut grupları (varsa) siler, yeni grupları oluşturur ve
    oluşturulan Group nesnelerinin listesini döner.
    """
    # Eğer özel yarışmacı listesi verilmemişse, ilgili yarışmanın tüm katılımcılarını al
    if contestants is None:
        contestants = list(stage.competition.contestants.all())
    else:
        contestants = list(contestants)
    
    # İsteğe bağlı olarak yarışmacıları rastgele karıştır
    if randomize:
        random.shuffle(contestants)
    
    # Bu etapta daha önceden oluşturulmuş gruplar varsa temizleyelim
    stage.groups.all().delete()
    
    groups = []
    group_size = stage.group_size
    
    # Yarışmacıları grup boyutuna göre dilimleyelim
    for i in range(0, len(contestants), group_size):
        group_contestants = contestants[i:i + group_size]
        # Otomatik grup numarası: oluşturulan grupların sayısına göre
        group_number = len(groups) + 1
        # Yeni grup oluşturuluyor
        group = Group.objects.create(
            competition=stage.competition,
            stage=stage,
            group_number=group_number
        )
        # Seçilen yarışmacıları gruba ekleyelim
        group.contestants.set(group_contestants)
        groups.append(group)
    
    return groups

    """
    Belirtilen etap (stage) için, her gruptaki yarışmacıların jürilerce verilen sıralamalarına göre,
    adminin belirlediği sayıda (stage.contestants_to_next_stage) yarışmacının bir sonraki etaba geçmesini sağlar.
    
    Varsayımlar:
      - Her grubun değerlendirmesi için en az bir Ranking kaydı vardır.
      - Ranking.rank alanı, o gruptaki yarışmacıların ID'lerini en iyi olandan başlayarak içeren bir liste olarak kaydedilmiştir.
    
    Dönüş:
      - Seçilen (geçmeye hak kazanan) yarışmacaların listesini döner.
    """
    winners = []
    
    # Her grup için işlemi gerçekleştir
    for group in stage.groups.all():
        # Bu grup için en az bir ranking kaydı olmalı
        ranking_obj = group.rankings.first()
        if not ranking_obj or not ranking_obj.rank:
            continue  # Eğer değerlendirme yoksa bu grubu atla
        
        ranking_list = ranking_obj.rank  # Örneğin: [3, 5, 1, 2] gibi yarışmacı ID'leri
        
        # Admin tarafından belirlenen sayı kadar yarışmacı seç
        count_to_select = stage.contestants_to_next_stage
        
        # Eğer ranking_list içerisindeki eleman sayısı count_to_select'ten azsa, tümünü seçeriz
        selected_ids = ranking_list[:count_to_select]
        
        # Seçilen ID'lere göre grup içindeki yarışmacıları getir ve sıralama sırasına göre düzenle
        selected_contestants = []
        for cid in selected_ids:
            try:
                contestant = group.contestants.get(id=cid)
                selected_contestants.append(contestant)
            except Contestant.DoesNotExist:
                continue
        
        winners.extend(selected_contestants)
    
    return winners