import maxminddb

regions = [
    {
        "id": "BR1",
        "name": "Brazil",
        "abbreviation": "BR",
        "country_codes": ["BR"],
    },
    {
        "id": "EUN1",
        "name": "Europe Nordic & East",
        "abbreviation": "EUNE",
        "country_codes": [
            "NO", "SE", "FI", "DK", "EE",
            "LV", "LT", "BY", "UA", "MD",
            "RO", "BG", "GR", "MK", "AL",
            "RS", "ME", "BA", "HR", "SK",
            "SI", "HU", "CZ", "PL"
        ],
    },
    {
        "id": "EUW1",
        "name": "Europe West",
        "abbreviation": "EUW",
        "country_codes": [
            "IE", "GB", "FR", "CH", "BE",
            "ES", "PT", "IT", "AT", "DE",
            "NL", "LU", "LI", "MC", "AD",
        ],
    },
    {
        "id": "LA1",
        "name": "Latin America North",
        "abbreviation": "LAN",
        "country_codes": [
            "PE", "EC", "CO", "VE", "PA",
            "CR", "NI", "HN", "SV", "GT",
            "BZ", "MX", "CU", "BS", "HT",
            "DO", "PR", "VG", "AI", "VI",
            "KN", "AG", "MS", "GP", "DM",
            "MQ", "LC", "VC", "BB", "GD",
            "TT", "JM", "TC", "KY"
        ],
    },
    {
        "id": "LA2",
        "name": "Latin America South",
        "abbreviation": "LAS",
        "country_codes": [
            "AR", "CL", "BO", "PY", "UY"
        ],
    },
    {
        "id": "NA1",
        "name": "North America",
        "abbreviation": "NA",
        "country_codes": ["CA", "US"],
    },
    {
        "id": "OC1",
        "name": "Oceania",
        "abbreviation": "OCE",
        "country_codes": ["AU", "NZ"],
    },
    {
        "id": "PH2",
        "name": "Philippines",
        "abbreviation": "PH",
        "country_codes": ["PH"]
    },
    {
        "id": "RU1",
        "name": "Russia",
        "abbreviation": "RU",
        "country_codes": ["RU"],
    },
    {
        "id": "SG2",
        "name": "Singapore",
        "abbreviation": "SG",
        "country_codes": ["SG"]
    },
    {
        "id": "TH2",
        "name": "Thailand",
        "abbreviation": "TH",
        "country_codes": ["TH"],
    },
    {
        "id": "TR1",
        "name": "Turkey",
        "abbreviation": "TR",
        "country_codes": ["TR"],
    },
    {
        "id": "TW2",
        "name": "Taiwan",
        "abbreviation": "TW",
        "country_codes": ["TW"],
    },
    {
        "id": "JP1",
        "name": "Japan",
        "abbreviation": "JP",
        "country_codes": ["JP"],
    },
    {
        "id": "KR",
        "name": "Republic of Korea",
        "abbreviation": "KR",
        "country_codes": ["KR"],
    },
    {
        "id": "VN2",
        "name": "Vietnam",
        "abbreviation": "VN",
        "country_codes": ["VN"],
    },
]
regions.sort(key=lambda r: r["abbreviation"])

default_region = "EUW1"

regions_by_id = {region["id"]: region for region in regions}
regions_by_abbreviation = {
    region["abbreviation"]: region for region in regions}
regions_by_country_code = {
    country_code: region
    for region in regions
    for country_code in region["country_codes"]
}



def get_region_from_ip(ip_address):
    try:
        try:
            with maxminddb.open_database("GeoLite2-Country.mmdb") as geoip:
                data = geoip.get(ip_address)
        except:
            print("Can't load IP database")
        country_code = data["country"]["iso_code"]
        region = regions_by_country_code[country_code]
    except:
        print(f"Couldn't fetch {ip_address} country.")
        region = regions_by_id[default_region]
    return region


if __name__ == "__main__":

    print(regions_by_id)
    print(regions_by_country_code)
    print(regions_by_abbreviation)
    # tests

    # Swisscom DNS IP
    print(get_region_from_ip("195.186.1.111"))
    # Google DNS IP
    print(get_region_from_ip("8.8.8.8"))
    # Spin DNS IP
    print(get_region_from_ip("203.23.236.66"))
    # Megacable DNS IP
    print(get_region_from_ip("200.52.196.125"))
    # Arnet DNS IP
    print(get_region_from_ip("200.45.191.35"))

    # Etisalat Egypt DNS IP (non covered country)
    print(get_region_from_ip("41.65.236.37"))
