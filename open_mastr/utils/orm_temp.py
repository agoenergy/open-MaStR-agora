from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Numeric,
    DateTime,
    Boolean,
    Date,
    JSON,
)

meta = MetaData(schema='temp_mastr')
Base = declarative_base(metadata=meta)


class Extended(object):
    Registrierungsdatum = Column(Date)
    EinheitMastrNummer = Column(String, primary_key=True)
    DatumLetzteAktualisierung = Column(DateTime(timezone=True))
    LokationMastrNummer = Column(String)
    Land = Column(String)
    Bundesland = Column(String)
    Landkreis = Column(String)
    Gemeinde = Column(String)
    Gemeindeschluessel = Column(String)
    Postleitzahl = Column(String)
    Laengengrad = Column(Float)
    Breitengrad = Column(Float)
    Gemarkung = Column(String)
    FlurFlurstuecknummern = Column(String)
    Strasse = Column(String)
    StrasseNichtGefunden = Column(Boolean)
    Hausnummer = Column(String)
    HausnummerNichtGefunden = Column(Boolean)
    Adresszusatz = Column(String)
    Ort = Column(String)
    Meldedatum = Column(Date)
    GeplantesInbetriebnahmedatum = Column(Date)
    Inbetriebnahmedatum = Column(Date)
    DatumEndgueltigeStilllegung = Column(Date)
    DatumBeginnVoruebergehendeStilllegung = Column(Date)
    DatumBeendigungVorlaeufigenStilllegung = Column(Date)
    DatumWiederaufnahmeBetrieb = Column(Date)
    EinheitSystemstatus = Column(String)
    EinheitBetriebsstatus = Column(String)
    DatumDesBetreiberwechsels = Column(Date)
    DatumRegistrierungDesBetreiberwechsels = Column(Date)
    NameStromerzeugungseinheit = Column(String)
    Energietraeger = Column(String)
    Bruttoleistung = Column(Numeric(precision=18, scale=3))
    Nettonennleistung = Column(Numeric(precision=18, scale=3))
    Einspeisungsart = Column(String)
    GenMastrNummer = Column(String)
    FernsteuerbarkeitNb = Column(Boolean)
    FernsteuerbarkeitDv = Column(Boolean)
    FernsteuerbarkeitDr = Column(Boolean)
    Weic = Column(String)
    WeicDisplayName = Column(String)
    Kraftwerksnummer = Column(String)
    Einsatzverantwortlicher = Column(String)


class WindExtended(Extended, Base):
    __tablename__ = "wind_extended"

    # wind specific attributes
    NameWindpark = Column(String)
    Lage = Column(String)
    Seelage = Column(String)
    ClusterOstsee = Column(String)
    ClusterNordsee = Column(String)
    Technologie = Column(String)
    Typenbezeichnung = Column(String)
    Nabenhoehe = Column(Numeric(precision=18, scale=3))
    Rotordurchmesser = Column(Numeric(precision=18, scale=3))
    Wassertiefe = Column(Numeric(precision=18, scale=3))
    Kuestenentfernung = Column(Numeric(precision=18, scale=3))
    Buergerenergie = Column(Boolean)
    EegMastrNummer = Column(String)
    Hersteller = Column(String)
    HerstellerId = Column(String)
    Typenbezeichnung = Column(String)
    Nabenhoehe = Column(Float)
    Rotordurchmesser = Column(Float)
    Rotorblattenteisungssystem = Column(Boolean)
    AuflageAbschaltungLeistungsbegrenzung = Column(Boolean)
    AuflagenAbschaltungSchallimmissionsschutzNachts = Column(Boolean)
    AuflagenAbschaltungSchallimmissionsschutzTagsueber = Column(Boolean)
    AuflagenAbschaltungSchattenwurf = Column(Boolean)
    AuflagenAbschaltungTierschutz = Column(Boolean)
    AuflagenAbschaltungEiswurf = Column(Boolean)
    AuflagenAbschaltungSonstige = Column(Boolean)
    Nachtkennzeichen = Column(Boolean)
    WindAnLandOderAufSee = Column(String)
    TechnologieFlugwind = Column(String)
    Flughoehe = Column(Float)
    Flugradius = Column(Float)


class SolarExtended(Extended, Base):
    __tablename__ = "solar_extended"

    AnzahlModule = Column(Integer)
    Lage = Column(String)
    Leistungsbegrenzung = Column(String)
    InAnspruchGenommeneFlaeche = Column(Numeric(precision=18, scale=3))
    ArtDerFlaeche = Column(String)
    ArtDerFlaecheIds = Column(String)
    InAnspruchGenommeneAckerflaeche = Column(Numeric(precision=18, scale=3))
    EegMastrNummer = Column(String)
    Nutzungsbereich = Column(String)
    Leistungsbegrenzung = Column(String)
    ArtDerSolaranlage = Column(String)
    Zaehlernummer = Column(String)
    InAnspruchGenommeneAckerflaeche = Column(Float)
    SpeicherAmGleichenOrt = Column(String)


class BiomassExtended(Extended, Base):
    __tablename__ = "biomass_extended"

    Hauptbrennstoff = Column(String)
    Biomasseart = Column(String)
    Technologie = Column(String)
    EegMastrNummer = Column(String)


class HydroExtended(Extended, Base):
    __tablename__ = "hydro_extended"

    NameKraftwerk = Column(String)
    ArtDerWasserkraftanlage = Column(String)
    AnzeigeEinerStilllegung = Column(Boolean)
    ArtDerStilllegung = Column(String)
    DatumBeginnVorlaeufigenOderEndgueltigenStilllegung = Column(Date)
    NettonennleistungDeutschland = Column(Numeric(precision=18, scale=3))
    ArtDesZuflusses = Column(String)
    EegMastrNummer = Column(String)


class Eeg(object):
    Registrierungsdatum = Column(Date)
    EegMastrNummer = Column(String, primary_key=True)
    Meldedatum = Column(Date)
    DatumLetzteAktualisierung = Column(DateTime(timezone=True))
    EegInbetriebnahmedatum = Column(Date)
    VerknuepfteEinheit = Column(String)


class WindEeg(Eeg, Base):
    __tablename__ = "wind_eeg"

    InstallierteLeistung = Column(Numeric(precision=18, scale=3))
    AnlageBetriebsstatus = Column(String)


class SolarEeg(Eeg, Base):
    __tablename__ = "solar_eeg"

    InanspruchnahmeZahlungNachEeg = Column(Boolean)
    InstallierteLeistung = Column(Numeric(precision=18, scale=3))
    AnlageBetriebsstatus = Column(String)


class BiomassEeg(Eeg, Base):
    __tablename__ = "biomass_eeg"

    InstallierteLeistung = Column(Numeric(precision=18, scale=3))
    Zuschlagsnummer = Column(String)
    BiogasDatumLeistungserhoehung = Column(Date)
    BiogasUmfangLeistungserhoehung = Column(Numeric(precision=18, scale=3))
    BiogasGaserzeugungskapazitaet = Column(Numeric(precision=18, scale=3))
    Hoechstbemessungsleistung = Column(Numeric(precision=18, scale=3))
    AnlageBetriebsstatus = Column(String)


class HydroEeg(Eeg, Base):
    __tablename__ = "hydro_eeg"

    InstallierteLeistung = Column(Numeric(precision=18, scale=3))
    AnlageBetriebsstatus = Column(String)
    Ertuechtigung = Column(JSON)


class Permit(Base):
    __tablename__ = "permit"

    Registrierungsdatum = Column(Date)
    GenMastrNummer = Column(String, primary_key=True)
    DatumLetzteAktualisierung = Column(DateTime(timezone=True))
    Art = Column(String)
    Datum = Column(Date)
    Behoerde = Column(String)
    Aktenzeichen = Column(String)
    Frist = Column(Date)
    WasserrechtsNummer = Column(String)
    WasserrechtAblaufdatum = Column(Date)
    Meldedatum = Column(Date)
    VerknuepfteEinheiten = Column(String)
    Netzbetreiberzuordnungen = Column(String)

class GridConnections(Base):
    __tablename__ = "grid_connections"

    NetzanschlusspunktMastrNummer = Column(String, primary_key=True)
    NetzanschlusspunktBezeichnung = Column(String)
    LetzteAenderung = Column(DateTime(timezone=True))
    LokationMastrNummer = Column(String)
    Lokationtyp = Column(String)
    MaximaleEinspeiseleistung = Column(Float)
    Gasqualitaet = Column(String)
    NetzMastrNummer = Column(String)
    NochInPlanung = Column(Boolean)
    NameDerTechnischenLokation = Column(String)
    MaximaleAusspeiseleistung = Column(Float)
    Messlokation = Column(String)
    Spannungsebene = Column(String)
    BilanzierungsgebietNetzanschlusspunktId = Column(Integer)
    Nettoengpassleistung = Column(Float)
    Netzanschlusskapazitaet = Column(Float)


tablename_mapping = {
    "anlageneegbiomasse": {
        "__name__": BiomassEeg.__tablename__,
        "__class__": BiomassEeg,
        "replace_column_names": {
            "EegMaStRNummer": "EegMastrNummer",
            "VerknuepfteEinheitenMaStRNummern": "VerknuepfteEinheit",
            "BiogasHoechstbemessungsleistung": "Hoechstbemessungsleistung",
        },
    },
    "einheitenbiomasse": {
        "__name__": BiomassExtended.__tablename__,
        "__class__": BiomassExtended,
        "replace_column_names": {
            "EegMaStRNummer": "EegMastrNummer",
            "KwkMaStRNummer": "KwkMastrNummer",
            "LokationMaStRNummer": "LokationMastrNummer",
        },
    },
    "anlageneeggeothermiegrubengasdruckentspannung": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": {
            "EegMaStRNummer": "EegMastrNummer",
            "VerknuepfteEinheitenMaStRNummern": "VerknuepfteEinheit",
        },
    },
    "einheitengeothermiegrubengasdruckentspannung": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": {
            "EegMaStRNummer": "EegMastrNummer",
            "KwkMaStRNummer": "KwkMastrNummer",
            "LokationMaStRNummer": "LokationMastrNummer",
        },
    },
    "anlageneegsolar": {
        "__name__": SolarEeg.__tablename__,
        "__class__": SolarEeg,
        "replace_column_names": {
            "EegMaStRNummer": "EegMastrNummer",
            "VerknuepfteEinheitenMaStRNummern": "VerknuepfteEinheit",
        },
    },
    "einheitensolar": {
        "__name__": SolarExtended.__tablename__,
        "__class__": SolarExtended,
        "replace_column_names": {
            "EegMaStRNummer": "EegMastrNummer",
            "LokationMaStRNummer": "LokationMastrNummer",
            "VerknuepfteEinheitenMaStRNummern": "VerknuepfteEinheit",
        },
    },
    "anlageneegspeicher": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": {
            "EegMaStRNummer": "EegMastrNummer",
            "VerknuepfteEinheitenMaStRNummern": "VerknuepfteEinheit",
            "Zuschlagsnummer": "eegZuschlagsnummer",
        },
    },
    "anlageneegwasser": {
        "__name__": HydroEeg.__tablename__,
        "__class__": HydroEeg,
        "replace_column_names": {
            "EegMaStRNummer": "EegMastrNummer",
            "VerknuepfteEinheitenMaStRNummern": "VerknuepfteEinheit",
        },
    },
    "einheitenwasser": {
        "__name__": HydroExtended.__tablename__,
        "__class__": HydroExtended,
        "replace_column_names": {
            "EegMaStRNummer": "EegMastrNummer",
            "LokationMaStRNummer": "LokationMastrNummer",
        },
    },
    "anlageneegwind": {
        "__name__": WindEeg.__tablename__,
        "__class__": WindEeg,
        "replace_column_names": {
            "VerknuepfteEinheitenMaStRNummern": "VerknuepfteEinheit",
            "EegMaStRNummer": "EegMastrNummer",
        },
    },
    "einheitenwind": {
        "__name__": WindExtended.__tablename__,
        "__class__": WindExtended,
        "replace_column_names": {
            "LokationMaStRNummer": "LokationMastrNummer",
            "EegMaStRNummer": "EegMastrNummer",
            "Nachtkennzeichnung": "Nachtkennzeichen",
        },
    },
    "anlagengasspeicher": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": {
            "MaStRNummer": "MastrNummer",
            "VerknuepfteEinheitenMaStRNummern": "VerknuepfteEinheit",
        },
    },
    "einheitengasspeicher": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": {
            "LokationMaStRNummer": "LokationMastrNummer",
            "SpeicherMaStRNummer": "SpeicherMastrNummer",
        },
    },
    "anlagenkwk": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": {
            "VerknuepfteEinheitenMaStRNummern": "VerknuepfteEinheiten"
        },
    },
    "geloeschteunddeaktiviertemarktakteure": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": None,
    },
    "anlagenstromspeicher": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": {
            "MaStRNummer": "MastrNummer",
            "VerknuepfteEinheitenMaStRNummern": "VerknuepfteEinheit",
        },
    },
    "bilanzierungsgebiete": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": None,
    },
    "einheitenaenderungnetzbetreiberzuordnungen": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": None,
    },
    "einheitengaserzeuger": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": {
            "LokationMaStRNummer": "LokationMastrNummer",
            "SpeicherMaStRNummer": "SpeicherMastrNummer",
        },
    },
    "einheitengasverbraucher": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": {
            "LokationMaStRNummer": "LokationMastrNummer",
            "VerknuepfteEinheitenMaStRNummern": "VerknuepfteEinheit",
        },
    },
    "einheitengenehmigung": {
        "__name__": Permit.__tablename__,
        "__class__": Permit,
        "replace_column_names": {
            "VerknuepfteEinheitenMaStRNummern": "VerknuepfteEinheiten"
        },
    },
    "einheitenkernkraft": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": {
            "LokationMaStRNummer": "LokationMastrNummer",
        },
    },
    "einheitenstromverbraucher": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": {
            "LokationMaStRNummer": "LokationMastrNummer",
        },
    },
    "einheitenstromspeicher": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": {
            "LokationMaStRNummer": "LokationMastrNummer",
            "EegMaStRNummer": "EegMastrNummer",
        },
    },
    "einheitenverbrennung": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": {
            "LokationMaStRNummer": "LokationMastrNummer",
            "KwkMaStRNummer": "KwkMastrNummer",
        },
    },
    "ertuechtigungen": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": None,
    },
    "geloeschteunddeaktivierteeinheiten": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": None,
    },
    "marktrollen": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": None,
    },
    "marktakteure": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": None,
    },
    "netze": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": None,
    },
    "katalogkategorien": {
        "__name__": "katalogkategorien",
        "__class__": None,
        "replace_column_names": None,
    },
    "katalogwerte": {
        "__name__": "katalogwerte",
        "__class__": None,
        "replace_column_names": None,
    },
    "lokationen": {
        "__name__": None,
        "__class__": None,
        "replace_column_names": {
            "VerknuepfteEinheitenMaStRNummern": "VerknuepfteEinheiten",
            "NetzanschlusspunkteMaStRNummern": "Netzanschlusspunkte",
        },
    },
    "einheitentypen": {
        "__name__": "einheitentypen",
        "__class__": None,
        "replace_column_names": None,
    },
    "netzanschlusspunkte": {
        "__name__": GridConnections.__tablename__,
        "__class__": GridConnections,
        "replace_column_names": {
            "LokationMaStRNummer": "LokationMastrNummer",
            "NetzMaStRNummer": "NetzMastrNummer",
        },
    },
}

