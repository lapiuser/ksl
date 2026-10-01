from dataclasses import dataclass

@dataclass(frozen=True)
class SchoolSpec:
    id: str
    category: str
    category_label: str
    name: str
    folder: str

SCHOOLS = [
    # Universities
    SchoolSpec("bfu_kant", "universities", "ВУЗы", "БФУ им. И. Канта", "bfu_kant"),
    SchoolSpec("kstu", "universities", "ВУЗы", "КГТУ", "kstu"),
    SchoolSpec("bgarf", "universities", "ВУЗы", "БГАРФ", "bgarf"),
    SchoolSpec("ranepa_west", "universities", "ВУЗы", "Западный филиал РАНХиГС", "ranepa_west"),
    SchoolSpec("mfua_kaliningrad", "universities", "ВУЗы", "Калининградский филиал МФЮА", "mfua_kaliningrad"),
    SchoolSpec("kaliningrad_institute_management", "universities", "ВУЗы", "Калининградский институт управления", "kaliningrad_institute_management"),
    SchoolSpec("mvd_university_kaliningrad", "universities", "ВУЗы", "Калининградский филиал Санкт-Петербургского университета МВД России", "mvd_university_kaliningrad"),
    SchoolSpec("naval_academy_kaliningrad", "universities", "ВУЗы", "Калининградский филиал ВУНЦ ВМФ «Военно-морская академия»", "naval_academy_kaliningrad"),

    # Colleges
    SchoolSpec("rachmaninov_music_college", "colleges", "Колледжи и техникумы", "Музыкальный колледж им. С.В. Рахманинова", "rachmaninov_music_college"),
    SchoolSpec("marine_fishing_college", "colleges", "Колледжи и техникумы", "Калининградский морской рыбопромышленный колледж", "marine_fishing_college"),
    SchoolSpec("it_construction_college", "colleges", "Колледжи и техникумы", "Колледж информационных технологий и строительства", "it_construction_college"),
    SchoolSpec("business_college", "colleges", "Колледжи и техникумы", "Бизнес-колледж", "business_college"),
    SchoolSpec("entrepreneurship_college", "colleges", "Колледжи и техникумы", "Колледж предпринимательства", "entrepreneurship_college"),
    SchoolSpec("baltic_shipbuilding_technical_school", "colleges", "Колледжи и техникумы", "Прибалтийский судостроительный техникум", "baltic_shipbuilding_technical_school"),
    SchoolSpec("service_tourism_college", "colleges", "Колледжи и техникумы", "Колледж сервиса и туризма", "service_tourism_college"),
    SchoolSpec("culture_art_college", "colleges", "Колледжи и техникумы", "Калининградский областной колледж культуры и искусства", "culture_art_college"),
    SchoolSpec("agrotechnology_nature_college", "colleges", "Колледжи и техникумы", "Колледж агротехнологий и природообустройства", "agrotechnology_nature_college"),
    SchoolSpec("geodesy_cartography_college", "colleges", "Колледжи и техникумы", "Калининградский филиал Санкт-Петербургского техникума геодезии и картографии", "geodesy_cartography_college"),

    # Lyceums / gymnasiums / boarding schools
    SchoolSpec("gymnasium_40", "lyceums_gymnasiums", "Лицеи, гимназии и школы-интернаты", "Гимназия № 40 им. Ю. А. Гагарина", "gymnasium_40"),
    SchoolSpec("lyceum_49", "lyceums_gymnasiums", "Лицеи, гимназии и школы-интернаты", "Лицей № 49", "lyceum_49"),
    SchoolSpec("lyceum_23", "lyceums_gymnasiums", "Лицеи, гимназии и школы-интернаты", "Лицей № 23", "lyceum_23"),
    SchoolSpec("lyceum_35", "lyceums_gymnasiums", "Лицеи, гимназии и школы-интернаты", "Лицей № 35 им. Буткова В.В.", "lyceum_35"),
    SchoolSpec("lyceum_17", "lyceums_gymnasiums", "Лицеи, гимназии и школы-интернаты", "Лицей № 17", "lyceum_17"),
    SchoolSpec("lyceum_18", "lyceums_gymnasiums", "Лицеи, гимназии и школы-интернаты", "Лицей № 18", "lyceum_18"),
    SchoolSpec("kaliningrad_marine_lyceum", "lyceums_gymnasiums", "Лицеи, гимназии и школы-интернаты", "Калининградский Морской Лицей", "kaliningrad_marine_lyceum"),
    SchoolSpec("shili", "lyceums_gymnasiums", "Лицеи, гимназии и школы-интернаты", "Школа-интернат лицей-интернат (ШИЛИ)", "shili"),
    SchoolSpec("gymnasium_32", "lyceums_gymnasiums", "Лицеи, гимназии и школы-интернаты", "Гимназия № 32", "gymnasium_32"),
    SchoolSpec("gymnasium_22", "lyceums_gymnasiums", "Лицеи, гимназии и школы-интернаты", "Гимназия № 22", "gymnasium_22"),
    SchoolSpec("gymnasium_1", "lyceums_gymnasiums", "Лицеи, гимназии и школы-интернаты", "Гимназия № 1", "gymnasium_1"),
    SchoolSpec("kadet_marine_corps", "lyceums_gymnasiums", "Лицеи, гимназии и школы-интернаты", "Андрея Первозванного Кадетский морской корпус", "kadet_marine_corps"),
    SchoolSpec("nakhimov_school_branch", "lyceums_gymnasiums", "Лицеи, гимназии и школы-интернаты", "Филиал Нахимовского военно-морского училища", "nakhimov_school_branch"),

    # Private
    SchoolSpec("hanzean_ladya", "private_schools", "Частные школы", "Лицей «Ганзейская Ладья»", "hanzean_ladya"),
    SchoolSpec("orthodox_gymnasium", "private_schools", "Частные школы", "Православная Гимназия", "orthodox_gymnasium"),
    SchoolSpec("albertina", "private_schools", "Частные школы", "Альбертина", "albertina"),
    SchoolSpec("dirigible", "private_schools", "Частные школы", "Дирижабль", "dirigible"),
    SchoolSpec("erudit", "private_schools", "Частные школы", "Эрудит", "erudit"),
    SchoolSpec("solnechny_luchik", "private_schools", "Частные школы", "школа-детский сад «Солнечный лучик»", "solnechny_luchik"),
]

# General schools from the supplied specification.
GENERAL_SCHOOL_NUMBERS = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,19,21,24,25,26,28,29,31,33,36,38,39,41,43,44,46,47,48,50,53,56,57,58]
for number in GENERAL_SCHOOL_NUMBERS:
    SCHOOLS.append(SchoolSpec(f"school_{number}", "general_schools", "Общеобразовательные школы", f"СОШ № {number}", f"school_{number}"))

SCHOOL_BY_ID = {s.id: s for s in SCHOOLS}
CATEGORY_ORDER = ["universities", "colleges", "lyceums_gymnasiums", "private_schools", "general_schools"]
CATEGORY_LABELS = {
    "universities": "ВУЗы",
    "colleges": "Колледжи и техникумы",
    "lyceums_gymnasiums": "Лицеи, гимназии и школы-интернаты",
    "private_schools": "Частные школы",
    "general_schools": "Общеобразовательные школы",
}


def asset_paths(school: SchoolSpec) -> dict[str, str]:
    base = f"/assets/{school.category}/{school.folder}"
    return {
        "desktop": f"{base}/desktop.jpg",
        "mobile": f"{base}/mobile.jpg",
    }
