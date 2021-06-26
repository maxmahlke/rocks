class Datacloud(pydantic.BaseModel):
    aams: Optional[str] = ""
    astdys: Optional[str] = ""
    astorb: Optional[str] = ""
    binarymp_tab: Optional[str] = ""
    binarymp_ref: Optional[str] = ""
    diamalbedo: Optional[str] = ""
    families: Optional[str] = ""
    masses: Optional[str] = ""
    mpcatobs: Optional[str] = ""
    mpcorb: Optional[str] = ""
    pairs: Optional[str] = ""
    taxonomy: Optional[str] = ""

    def __str__(self):
        return self.json()


class Pairs(pydantic.BaseModel):
    id_: Optional[int] = pydantic.Field(None, alias="id")
    number: Optional[int] = pydantic.Field(None, alias="num")
    name: Optional[str] = ""
    sibling_num: Optional[float] = np.nan
    sibling_name: Optional[str] = ""
    delta_v: Optional[float] = np.nan
    delta_a: Optional[float] = np.nan
    delta_e: Optional[float] = np.nan
    delta_sini: Optional[float] = np.nan
    delta_i: Optional[float] = np.nan
    membership: Optional[int] = None
    iddataset: Optional[str] = ""
    idcollection: Optional[int] = None
    resourcename: Optional[str] = ""
    datasetname: Optional[str] = ""
    bibcode: Optional[str] = ""
    title: Optional[str] = ""
    link: Optional[str] = ""


class AAMS(pydantic.BaseModel):
    id_: Optional[int] = pydantic.Field(None, alias="id")
    number: Optional[int] = pydantic.Field(None, alias="num")
    name: Optional[str] = ""

    HG_H: Optional[float] = np.nan
    HG_G: Optional[float] = np.nan
    HG_r_err_H: Optional[float] = np.nan
    HG_l_err_H: Optional[float] = np.nan
    HG_r_err_G: Optional[float] = np.nan
    HG_l_err_G: Optional[float] = np.nan
    HG_rms: Optional[float] = np.nan
    HG_convergence: Optional[float] = np.nan
    HG1G2_H: Optional[float] = np.nan
    HG1G2_G1: Optional[float] = np.nan
    HG1G2_G2: Optional[float] = np.nan
    HG1G2_r_err_H: Optional[float] = np.nan
    HG1G2_l_err_H: Optional[float] = np.nan
    HG1G2_r_err_G1: Optional[float] = np.nan
    HG1G2_l_err_G1: Optional[float] = np.nan
    HG1G2_r_err_G2: Optional[float] = np.nan
    HG1G2_l_err_G2: Optional[float] = np.nan
    HG1G2_rms: Optional[float] = np.nan
    HG1G2_convergence: Optional[float] = np.nan
    HG12_H: Optional[float] = np.nan
    HG12_G12: Optional[float] = np.nan
    HG12_r_err_H: Optional[float] = np.nan
    HG12_l_err_H: Optional[float] = np.nan
    HG12_r_err_G12: Optional[float] = np.nan
    HG12_l_err_G12: Optional[float] = np.nan
    HG12_rms: Optional[float] = np.nan
    HG12_convergence: Optional[float] = np.nan
    HG_err_H: Optional[float] = np.nan
    HG_err_G: Optional[float] = np.nan
    HG1G2_err_H: Optional[float] = np.nan
    HG1G2_err_G1: Optional[float] = np.nan
    HG1G2_err_G2: Optional[float] = np.nan
    HG12_err_H: Optional[float] = np.nan
    HG12_err_G12: Optional[float] = np.nan
    iddataset: Optional[str] = ""
    idcollection: Optional[int] = None
    resourcename: Optional[str] = ""
    datasetname: Optional[str] = ""
    bibcode: Optional[str] = ""
    title: Optional[str] = ""
    link: Optional[str] = ""


class Astorb(pydantic.BaseModel):
    id_: Optional[int] = pydantic.Field(None, alias="id")
    number: Optional[int] = pydantic.Field(None, alias="num")
    name: Optional[str] = ""
    OrbComputer: Optional[str] = ""
    H: Optional[float] = np.nan
    G: Optional[float] = np.nan
    B_V: Optional[float] = np.nan
    IRAS_Diameter: Optional[float] = np.nan
    IRAS_Class: Optional[str] = ""
    OrbArc: Optional[int] = None
    NumberObs: Optional[int] = None
    MeanAnomaly: Optional[float] = np.nan
    ArgPerihelion: Optional[float] = np.nan
    LongAscNode: Optional[float] = np.nan
    Inclination: Optional[float] = np.nan
    Eccentricity: Optional[float] = np.nan
    SemimajorAxis: Optional[float] = np.nan
    CEU_value: Optional[float] = np.nan
    CEU_rate: Optional[float] = np.nan
    PEU_value: Optional[float] = np.nan
    GPEU_fromCEU: Optional[float] = np.nan
    GPEU_fromPEU: Optional[float] = np.nan
    Note_1: Optional[int] = None
    Note_2: Optional[int] = None
    Note_3: Optional[int] = None
    Note_4: Optional[int] = None
    Note_5: Optional[int] = None
    Note_6: Optional[int] = None
    YY_calulation: Optional[int] = None
    MM_calulation: Optional[int] = None
    DD_calulation: Optional[int] = None
    YY_osc: Optional[int] = None
    MM_osc: Optional[int] = None
    DD_osc: Optional[int] = None
    CEU_yy: Optional[int] = None
    CEU_mm: Optional[int] = None
    CEU_dd: Optional[int] = None
    PEU_yy: Optional[int] = None
    PEU_mm: Optional[int] = None
    PEU_dd: Optional[int] = None
    GPEU_yy: Optional[int] = None
    GPEU_mm: Optional[int] = None
    GPEU_dd: Optional[int] = None
    GGPEU_yy: Optional[int] = None
    GGPEU_mm: Optional[int] = None
    GGPEU_dd: Optional[int] = None
    JD_osc: Optional[float] = np.nan
    px: Optional[float] = np.nan
    py: Optional[float] = np.nan
    pz: Optional[float] = np.nan
    vx: Optional[float] = np.nan
    vy: Optional[float] = np.nan
    vz: Optional[float] = np.nan
    MeanMotion: Optional[float] = np.nan
    OrbPeriod: Optional[float] = np.nan
    iddataset: Optional[str] = ""
    idcollection: Optional[int] = None
    resourcename: Optional[str] = ""
    datasetname: Optional[str] = ""
    bibcode: Optional[str] = ""
    title: Optional[str] = ""
    link: Optional[str] = ""


class AstDyS(pydantic.BaseModel):
    id_: Optional[int] = pydantic.Field(None, alias="id")
    number: Optional[int] = pydantic.Field(None, alias="num")
    name: Optional[str] = ""
    H: Optional[float] = np.nan
    ProperSemimajorAxis: Optional[float] = np.nan
    err_ProperSemimajorAxis: Optional[float] = np.nan
    ProperEccentricity: Optional[float] = np.nan
    err_ProperEccentricity: Optional[float] = np.nan
    ProperSinI: Optional[float] = np.nan
    err_ProperSinI: Optional[float] = np.nan
    ProperInclination: Optional[float] = np.nan
    err_ProperInclination: Optional[float] = np.nan
    n: Optional[float] = np.nan
    err_n: Optional[float] = np.nan
    g: Optional[float] = np.nan
    err_g: Optional[float] = np.nan
    s: Optional[float] = np.nan
    err_s: Optional[float] = np.nan
    LCE: Optional[float] = np.nan
    My: Optional[float] = np.nan
    lam_fit: Optional[float] = pydantic.Field(np.nan, alias="lam-fit")
    iddataset: Optional[str] = ""
    idcollection: Optional[int] = None
    resourcename: Optional[str] = ""
    datasetname: Optional[str] = ""
    bibcode: Optional[str] = ""
    title: Optional[str] = ""
    link: Optional[str] = ""


class Taxonomies(pydantic.BaseModel):
    link: List[str] = [""]
    datasetname: List[str] = [""]
    resourcename: List[str] = [""]
    doi: List[str] = [""]
    bibcode: List[str] = [""]
    url: List[str] = [""]
    title: List[str] = [""]
    source: List[str] = [""]
    shortbib: List[str] = [""]
    waverange: List[str] = [""]
    method: List[str] = [""]
    scheme: List[str] = [""]
    name: List[str] = [""]
    complex_: List[str] = pydantic.Field([""], alias="complex")
    class_: List[str] = pydantic.Field([""], alias="class")

    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    idcollection: List[Optional[int]] = [None]
    iddataset: List[Optional[int]] = [None]
    year: List[Optional[int]] = [None]
    id_: List[Optional[int]] = pydantic.Field([None], alias="id")

    preferred: List[bool] = [False]

    @pydantic.validator("preferred", pre=True)
    def select_preferred_taxonomy(cls, v, values):
        return rocks.properties.rank_properties("taxonomy", values)

    def __len__(self):
        return len(self.class_)

    def __str__(self):

        if len(self) == 1 and not self.class_[0]:
            return "No taxonomies on record."

        table = rich.table.Table(
            header_style="bold blue",
            box=rich.box.SQUARE,
            footer_style="dim",
        )

        columns = ["class_", "complex_", "method", "waverange", "scheme", "shortbib"]

        for c in columns:
            table.add_column(c)

        # Values are entries for each field
        for i, preferred in enumerate(self.preferred):
            table.add_row(
                *[str(getattr(self, c)[i]) for c in columns],
                style="bold green" if preferred else "white",
            )
        rich.print(table)
        return ""


class Masses(pydantic.BaseModel):
    link: List[str] = [""]
    datasetname: List[str] = [""]
    resourcename: List[str] = [""]
    doi: List[str] = [""]
    bibcode: List[str] = [""]
    url: List[str] = [""]
    title: List[str] = [""]
    source: List[str] = [""]
    shortbib: List[str] = [""]
    method: List[str] = [""]
    name: List[str] = [""]

    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    idcollection: List[Optional[int]] = [None]
    iddataset: List[Optional[int]] = [None]
    year: List[Optional[int]] = [None]
    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    mass: List[float] = [np.nan]
    err_mass: List[float] = [np.nan]

    preferred: List[bool] = [False]

    @pydantic.validator("preferred", pre=True)
    def select_preferred_mass(cls, v, values):
        return rocks.properties.rank_properties("mass", values)


class Mpcatobs(pydantic.BaseModel):
    link: List[str] = [""]
    datasetname: List[str] = [""]
    resourcename: List[str] = [""]
    doi: List[str] = [""]
    bibcode: List[str] = [""]
    title: List[str] = [""]
    iddataset: List[str] = [""]
    idcollection: List[Optional[int]] = [None]
    jd_obs: List[float] = [np.nan]
    ra_obs: List[float] = [np.nan]
    dec_obs: List[float] = [np.nan]
    mag: List[float] = [np.nan]
    vgs_x: List[float] = [np.nan]
    vgs_y: List[float] = [np.nan]
    vgs_z: List[float] = [np.nan]
    packed_name: List[str] = [""]
    orb_type: List[str] = [""]
    discovery: List[str] = [""]
    note1: List[str] = [""]
    note2: List[str] = [""]
    note3: List[str] = [""]
    note4: List[str] = [""]
    iau_code: List[str] = [""]
    date_obs: List[str] = [""]
    filter_: List[str] = pydantic.Field([""], alias="type")
    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    type_: List[str] = pydantic.Field([""], alias="type")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]


class Albedos(pydantic.BaseModel):

    link: List[str] = [""]
    datasetname: List[str] = [""]
    resourcename: List[str] = [""]
    doi: List[str] = [""]
    bibcode: List[str] = [""]
    url: List[str] = [""]
    title: List[str] = [""]
    name: List[str] = [""]
    iddataset: List[Optional[int]] = [None]
    method: List[str] = [""]
    shortbib: List[str] = [""]
    year: List[Optional[int]] = [None]
    source: List[str] = [""]

    idcollection: List[Optional[int]] = [None]
    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    albedo: List[float] = [np.nan]
    err_albedo: List[float] = [np.nan]
    diameter: List[float] = [np.nan]
    err_diameter: List[float] = [np.nan]
    beaming: List[float] = [np.nan]
    err_beaming: List[float] = [np.nan]
    emissivity: List[float] = [np.nan]
    err_emissivity: List[float] = [np.nan]

    preferred_albedo: List[bool] = [False]
    preferred_diameter: List[bool] = [False]

    @pydantic.validator("preferred_albedo", pre=True)
    def select_preferred_albedo(cls, v, values):
        return rocks.properties.rank_properties("albedo", values)

    @pydantic.validator("preferred_diameter", pre=True)
    def select_preferred_diameter(cls, v, values):
        return rocks.properties.rank_properties("diameter", values)

    def __len__(self):
        return len(self.albedo)

    def __str__(self):

        if len(self) == 1 and not self.albedo[0] and not self.diameter[0]:
            return "No albedos on record."

        table = rich.table.Table(
            header_style="bold blue",
            box=rich.box.SQUARE,
            footer_style="dim",
        )

        columns = ["albedo", "err_albedo", "method", "shortbib"]

        for c in columns:
            table.add_column(c)

        # Values are entries for each field
        for i, preferred in enumerate(self.preferred_albedo):

            table.add_row(
                *[str(getattr(self, c)[i]) for c in columns],
                style="bold green" if preferred else "white",
            )
        rich.print(table)
        return ""


class Diameters(pydantic.BaseModel):

    link: List[str] = [""]
    datasetname: List[str] = [""]
    resourcename: List[str] = [""]
    doi: List[str] = [""]
    bibcode: List[str] = [""]
    url: List[str] = [""]
    title: List[str] = [""]
    name: List[str] = [""]
    iddataset: List[Optional[int]] = [None]
    method: List[str] = [""]
    shortbib: List[str] = [""]
    year: List[Optional[int]] = [None]
    source: List[str] = [""]

    idcollection: List[Optional[int]] = [None]
    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    albedo: List[float] = [np.nan]
    err_albedo: List[float] = [np.nan]
    diameter: List[float] = [np.nan]
    err_diameter: List[float] = [np.nan]
    beaming: List[float] = [np.nan]
    err_beaming: List[float] = [np.nan]
    emissivity: List[float] = [np.nan]
    err_emissivity: List[float] = [np.nan]

    preferred_albedo: List[bool] = [False]
    preferred_diameter: List[bool] = [False]

    @pydantic.validator("preferred_albedo", pre=True)
    def select_preferred_albedo(cls, v, values):
        return rocks.properties.rank_properties("albedo", values)

    @pydantic.validator("preferred_diameter", pre=True)
    def select_preferred_diameter(cls, v, values):
        return rocks.properties.rank_properties("diameter", values)

    def __len__(self):
        return len(self.albedo)

    def __str__(self):

        if len(self) == 1 and not self.albedo[0] and not self.diameter[0]:
            return "No diameters on record."

        table = rich.table.Table(
            header_style="bold blue",
            box=rich.box.SQUARE,
            footer_style="dim",
        )

        columns = ["diameter", "err_diameter", "method", "shortbib"]

        for c in columns:
            table.add_column(c)

        # Values are entries for each field
        for i, preferred in enumerate(self.preferred_diameter):

            table.add_row(
                *[str(getattr(self, c)[i]) for c in columns],
                style="bold green" if preferred else "white",
            )
        rich.print(table)
        return ""


class Diamalbedo(pydantic.BaseModel):

    link: List[str] = [""]
    datasetname: List[str] = [""]
    resourcename: List[str] = [""]
    doi: List[str] = [""]
    bibcode: List[str] = [""]
    url: List[str] = [""]
    title: List[str] = [""]
    name: List[str] = [""]
    iddataset: List[Optional[int]] = [None]
    method: List[str] = [""]
    shortbib: List[str] = [""]
    year: List[Optional[int]] = [None]
    source: List[str] = [""]

    idcollection: List[Optional[int]] = [None]
    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    albedo: List[float] = [np.nan]
    err_albedo: List[float] = [np.nan]
    diameter: List[float] = [np.nan]
    err_diameter: List[float] = [np.nan]
    beaming: List[float] = [np.nan]
    err_beaming: List[float] = [np.nan]
    emissivity: List[float] = [np.nan]
    err_emissivity: List[float] = [np.nan]

    preferred_albedo: List[bool] = [False]
    preferred_diameter: List[bool] = [False]

    @pydantic.validator("preferred_albedo", pre=True)
    def select_preferred_albedo(cls, v, values):
        return rocks.properties.rank_properties("albedo", values)

    @pydantic.validator("preferred_diameter", pre=True)
    def select_preferred_diameter(cls, v, values):
        return rocks.properties.rank_properties("diameter", values)

    def __len__(self):
        return len(self.albedo)

    def __str__(self):

        if len(self) == 1 and not self.albedo[0] and not self.diameter[0]:
            return "No diameters or albedos on record."

        table = rich.table.Table(
            header_style="bold blue",
            box=rich.box.SQUARE,
            footer_style="dim",
        )

        columns = [
            "diameter",
            "err_diameter",
            "albedo",
            "err_albedo",
            "method",
            "shortbib",
        ]

        for c in columns:
            table.add_column(c)

        # Make a joint preferred list for albedo and diameter
        preferred = list(map(any, zip(self.preferred_diameter, self.preferred_albedo)))

        # Values are entries for each field
        for i, preferred in enumerate(preferred):

            table.add_row(
                *[str(getattr(self, c)[i]) for c in columns],
                style="bold green" if preferred else "white",
            )
        rich.print(table)
        return ""
