from enum import StrEnum, auto


class HttpMethod(StrEnum):
    GET = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()
    PATCH = auto()
    HEAD = auto()
    OPTIONS = auto()
    TRACE = auto()
    CONNECT = auto()


class AssetRoles(StrEnum):
    data = auto()
    metadata = auto()
    thumbnail = auto()
    overview = auto()
    visual = auto()
    date = auto()
    graphic = auto()
    data_mask = auto()
    snow_ice = auto()
    land_water = auto()
    water_mask = auto()
    iso_19115 = auto()

    # from EO
    reflectance = auto()
    temperature = auto()
    saturation = auto()
    cloud = auto()
    cloud_shadow = auto()

    # from View

    incidence_angle = auto()
    azimuth = auto()
    sun_azimuth = auto()
    sun_elevation = auto()
    terrain_shadow = auto()
    terrain_occlusion = auto()
    terrain_illumination = auto()

    # from SAR
    local_incidence_angle = auto()
    ellipsoid_incidence_angle = auto()
    noise_power = auto()
    amplitude = auto()
    magnitude = auto()
    sigma0 = auto()
    beta0 = auto()
    gamma0 = auto()
    date_offset = auto()
    covmat = auto()
    prd = auto()
