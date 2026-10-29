# Wrapped GRIB2 descriptions are copied from grib 0.20.0 (src/def/grib2).
# See AGENTS.md for documentation and numeric-range requirements.
import numpy as np
from datetime import datetime
from typing import final, Union
from . import param_set as param_set

@final
class Identification:
    """Section 1 - Identification section.
    """
    def __new__(cls, /, centre_id: int, subcentre_id: int, master_table_version: int, local_table_version: int, ref_time_significance: int, ref_time: datetime, prod_status: int, data_type: int) -> Identification:
        """Create Identification.

        Parameters
        ----------
        centre_id : int
            Identification of originating/generating centre (see Common Code table
            C-11).

            Encoded as an unsigned 16-bit integer. Accepted range: 0 to 65535
            (inclusive).
        subcentre_id : int
            Identification of originating/generating subcentre (allocated by
            originating/generating centre).

            Encoded as an unsigned 16-bit integer. Accepted range: 0 to 65535
            (inclusive).
        master_table_version : int
            GRIB master table version number (see Common Code table C-0 and Note 1).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        local_table_version : int
            Version number of GRIB Local tables used to augment Master tables (see Code
            table 1.1 and Note 2).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        ref_time_significance : int
            Significance of reference time (see Code table 1.2).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        ref_time : datetime
            Reference time of data.

            Python wrapper: calendar fields are copied directly without timezone
            conversion; supply UTC. Year is encoded as an unsigned 16-bit integer (0 to
            65535); month, day, hour, minute, and second as unsigned 8-bit integers (0
            to 255). Python datetime restricts these to valid calendar values (year 1 to
            9999, month 1 to 12, day 1 to 31 as valid for the month, hour 0 to 23,
            minute and second 0 to 59). Microseconds are not encoded.
        prod_status : int
            Production status of processed data in this GRIB message (see Code table
            1.3).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        data_type : int
            Type of processed data in this GRIB message (see Code table 1.4).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).

        Notes
        -----
        Python wrapper: the optional identification template is not supported.

        Numeric ranges describe representable values accepted by the wrapper, including
        reserved or missing-value codes. They do not imply that every value is valid in
        the referenced code table. Code-table and note references are retained from the
        upstream GRIB2 documentation.
        """
        ...
    def __repr__(self, /) -> str: ...

def grib2_message(discipline: int, ident: Identification, product: Union[ProductDefinition, bytes], lats: np.ndarray[tuple[int], np.dtype[np.float64]], lngs: np.ndarray[tuple[int], np.dtype[np.float64]], values: np.ndarray[tuple[int, int], np.dtype[np.float64]]) -> bytes:
    """Encode a single GRIB2 message.

    Parameters
    ----------
    discipline : int
        Discipline - GRIB Master Table Number (see Code Table 0.0).

        Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        Code-table validity is the caller's responsibility.
    ident : Identification
        Section 1 - Identification section.
    product : Union[ProductDefinition, bytes]
        Section 4 - Product definition section.
        Python wrapper: accepts a structured definition or raw section payload
        bytes, excluding the five-octet section header.
    lats : numpy.ndarray
        Python wrapper: nonempty one-dimensional float64 latitude array.
    lngs : numpy.ndarray
        Python wrapper: nonempty one-dimensional float64 longitude array.
    values : numpy.ndarray or numpy.ma.MaskedArray
        Python wrapper: contiguous two-dimensional float64 data array with
        shape (len(lngs), len(lats)).

    Returns
    -------
    bytes
        The encoded GRIB2 message.
    """
    ...

@final
class ProductDefinition:
    """Section 4 - Product definition section.
    """
    def __new__(cls, template: Union[Template4_0, Template4_1, Template4_8]) -> ProductDefinition:
        """Create ProductDefinition.

        Parameters
        ----------
        template : Union[Template4_0, Template4_1, Template4_8]
            Product Definition Template (see Template 4.X, where X is the Product
            Definition Template Number given in octets 8-9).

        Notes
        -----
        Python wrapper: inputs are copied. The template number is derived automatically,
        and num_coord_values is always zero; trailing vertical coordinate values are not
        supported.

        Raises
        ------
        TypeError
            If template is not Template4_0, Template4_1, or Template4_8.
        """
        ...
    @property
    def template_num(self) -> int:
        """Product definition template number (see Code table 4.0).

        Encoded as an unsigned 16-bit integer. Accepted range: 0 to 65535 (inclusive).

        Python wrapper: read-only and derived from the template. Possible values are 0, 1, and 8.
        """
        ...
    def __repr__(self) -> str: ...

@final
class Template4_0:
    """Product definition template 4.0 - Analysis or forecast at a horizontal level or in a
    horizontal layer at a point in time.
    """
    def __new__(cls, param: param_set.ProductParam, generating_process: param_set.GeneratingProcess, forecast_time: param_set.ForecastTime, horizontal: param_set.Horizontal) -> Template4_0:
        """Create Template4_0.

        Parameters
        ----------
        param : param_set.ProductParam
            Python argument for grib::def::grib2::template::Template4_0::param.
        generating_process : param_set.GeneratingProcess
            Python argument for
            grib::def::grib2::template::Template4_0::generating_process.
        forecast_time : param_set.ForecastTime
            Python argument for
            grib::def::grib2::template::Template4_0::forecast_time.
        horizontal : param_set.Horizontal
            Python argument for grib::def::grib2::template::Template4_0::horizontal.

        Notes
        -----
        Python wrapper: inputs are copied. The upstream grouped members have no
        standalone prose descriptions; their Rust field paths are given above. The
        forecast_time field supplies these upstream contextual descriptions:
        cutoff_hours: "Hours of observational data cutoff after reference time (see Note
        1)"; cutoff_minutes: "Minutes of observational data cutoff after reference
        time".
        """
        ...
    def __repr__(self) -> str: ...

@final
class Template4_1:
    """Product definition template 4.1 - Individual ensemble forecast, control and
    perturbed, at a horizontal level or in a horizontal layer at a point in time.
    """
    def __new__(cls, param: param_set.ProductParam, generating_process: param_set.GeneratingProcess, forecast_time: param_set.ForecastTime, horizontal: param_set.Horizontal, ensemble_forecast: param_set.EnsembleForecast) -> Template4_1:
        """Create Template4_1.

        Parameters
        ----------
        param : param_set.ProductParam
            Python argument for grib::def::grib2::template::Template4_1::param.
        generating_process : param_set.GeneratingProcess
            Python argument for
            grib::def::grib2::template::Template4_1::generating_process.
        forecast_time : param_set.ForecastTime
            Python argument for
            grib::def::grib2::template::Template4_1::forecast_time.
        horizontal : param_set.Horizontal
            Python argument for grib::def::grib2::template::Template4_1::horizontal.
        ensemble_forecast : param_set.EnsembleForecast
            Python argument for
            grib::def::grib2::template::Template4_1::emsemble_forecast.

        Notes
        -----
        Python wrapper: inputs are copied. The upstream grouped members have no
        standalone prose descriptions; their Rust field paths are given above. The
        generating_process field supplies this upstream contextual description for
        process_id: "Forecast generating process identifier (defined by originating
        centre)."
        """
        ...
    def __repr__(self) -> str: ...

@final
class Template4_8:
    """Product definition template 4.8 - Average, accumulation, and/or extreme values or
    other statistically processed values at a horizontal level or in a horizontal layer
    in a continuous or non-continuous time interval.
    """
    def __new__(cls, param: param_set.ProductParam, generating_process: param_set.GeneratingProcess, forecast_time: param_set.ForecastTime, horizontal: param_set.Horizontal, statistical: param_set.Statistical) -> Template4_8:
        """Create Template4_8.

        Parameters
        ----------
        param : param_set.ProductParam
            Python argument for grib::def::grib2::template::Template4_8::param.
        generating_process : param_set.GeneratingProcess
            Python argument for
            grib::def::grib2::template::Template4_8::generating_process.
        forecast_time : param_set.ForecastTime
            Python argument for
            grib::def::grib2::template::Template4_8::forecast_time.
        horizontal : param_set.Horizontal
            Python argument for grib::def::grib2::template::Template4_8::horizontal.
        statistical : param_set.Statistical
            Python argument for
            grib::def::grib2::template::Template4_8::time_interval.

        Notes
        -----
        Python wrapper: inputs are copied. The upstream grouped members have no
        standalone prose descriptions; their Rust field paths are given above.
        """
        ...
    def __repr__(self) -> str: ...
