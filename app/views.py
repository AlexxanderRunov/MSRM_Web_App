from django.shortcuts import render

samples = [
    {
        "id": 1,
        "name": "Roubion",
        "description": "Тип грунта, вероятно, назван в честь одной из местностей на Земле или конкретно в контексте геологии Марса. Вопрос требует дальнейшего уточнения, так как такой термин может не быть общепринятым в литературе.",
        "date_discovery": "13 октября 2023г",
        "image": "http://localhost:9000/images/1.png"
    },
    {
        "id": 2,
        "name": "Montdenier",
        "description": "Как и в случае с Roubion, Montdenier может быть теоретически определён как тип грунта, но требуется больше контекста для точного понимания. Возможно, это название связано с определённым геологическим формированием или областью на Марсе.",
        "date_discovery": "5 ноября 2022г",
        "image": "http://localhost:9000/images/2.png"
    },
    {
        "id": 3,
        "name": "Montagnac",
        "description": "Скорее всего, данный термин также не является общепринятым в марсианской геологии. В геологии может использоваться для обозначения членств в определённых формациях.",
        "date_discovery": "9 сентября 2023г",
        "image": "http://localhost:9000/images/3.png"
    },
    {
        "id": 4,
        "name": "Salette",
        "description": "Salette может относиться к типу грунта или конкретному географическому объекту на Марсе. Однако, в доступной геологической литературе о Марсе информации об этом типе, как правило, нет",
        "date_discovery": "5 декабря 2021г",
        "image": "http://localhost:9000/images/4.png"
    },
    {
        "id": 5,
        "name": "Coulettes",
        "description": "Согласно контексту, Coulettes может упоминаться как тип грунта, связанный с особенностями марсианского ландшафта или геологии. Однако, уточнение тоже требуется для большей ясности.",
        "date_discovery": " 8 августа 2021г",
        "image": "http://localhost:9000/images/5.png"
    },
    {
        "id": 6,
        "name": "Robine",
        "description": "Похожим образом, Robine может быть упомянутым типом грунта или местностью на Марсе, но без дополнительных данных сложновато предложить определённые характеристики или детали.",
        "date_discovery": "1 октября 2024г",
        "image": "http://localhost:9000/images/6.png"
    }
]

draft_mission = {
    "id": 123,
    "status": "Черновик",
    "date_created": "12 сентября 2024г",
    "name": "MSR-1",
    "date": "5 октебря 2024г",
    "samples": [
        {
            "id": 1,
            "value": 1
        },
        {
            "id": 2,
            "value": 2
        },
        {
            "id": 3,
            "value": 3
        }
    ]
}


def getSampleById(sample_id):
    for sample in samples:
        if sample["id"] == sample_id:
            return sample


def getSamples():
    return samples


def searchSamples(sample_name):
    res = []

    for sample in samples:
        if sample_name.lower() in sample["name"].lower():
            res.append(sample)

    return res


def getDraftMission():
    return draft_mission


def getMissionById(mission_id):
    return draft_mission


def index(request):
    sample_name = request.GET.get("sample_name", "")
    samples = searchSamples(sample_name) if sample_name else getSamples()
    draft_mission = getDraftMission()

    context = {
        "samples": samples,
        "sample_name": sample_name,
        "samples_count": len(draft_mission["samples"]),
        "draft_mission": draft_mission
    }

    return render(request, "samples_page.html", context)


def sample(request, sample_id):
    context = {
        "id": sample_id,
        "sample": getSampleById(sample_id),
    }

    return render(request, "sample_page.html", context)


def mission(request, mission_id):
    mission = getMissionById(mission_id)
    samples = [
        {**getSampleById(sample["id"]), "value": sample["value"]}
        for sample in mission["samples"]
    ]

    context = {
        "mission": mission,
        "samples": samples
    }

    return render(request, "mission_page.html", context)
