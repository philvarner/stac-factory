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


class AssetRole(StrEnum):
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


class LinkRelation(StrEnum):
    self = auto()
    derived_from = auto()
    root = auto()
    parent = auto()
    child = auto()
    item = auto()
    alternate = auto()
    canonical = auto()
    via = auto()
    prev = auto()
    next = auto()
    preview = auto()
    collection = auto()


# derived from pystac.MediaType
class MediaType(StrEnum):
    COG = "image/tiff; application=geotiff; profile=cloud-optimized"
    GEOTIFF = "image/tiff; application=geotiff"
    FLATGEOBUF = "application/vnd.flatgeobuf"
    GEOJSON = "application/geo+json"
    GEOPACKAGE = "application/geopackage+sqlite3"
    HDF = "application/x-hdf"  # <= HDF4
    HDF5 = "application/x-hdf5"
    HTML = "text/html"
    JPEG = "image/jpeg"
    JPEG2000 = "image/jp2"
    JSON = "application/json"
    PNG = "image/png"
    TEXT = "text/plain"
    TIFF = "image/tiff"
    KML = "application/vnd.google-earth.kml+xml"
    XML = "application/xml"
    PDF = "application/pdf"
    NETCDF = "application/netcdf"
    COPC = "application/vnd.laszip+copc"
    VND_PMTILES = "application/vnd.pmtiles"
    VND_APACHE_PARQUET = "application/vnd.apache.parquet"
    VND_ZARR = "application/vnd.zarr"
