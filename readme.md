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
