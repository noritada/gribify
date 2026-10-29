# Wrapped GRIB2 descriptions are copied from grib 0.20.0 (src/def/grib2).
# See AGENTS.md for documentation and numeric-range requirements.
from typing import final, List
from datetime import datetime

@final
class GeneratingProcess:
    """Python wrapper for grib::def::grib2::template::param_set::GeneratingProcess.
    """
    def __new__(cls, /, process_type: int, background_process: int, process_id: int) -> GeneratingProcess:
        """Create GeneratingProcess.

        Parameters
        ----------
        process_type : int
            Type of generating process (see Code Table 4.3).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        background_process : int
            Background generating process identifier (defined by originating centre).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        process_id : int
            Analysis or forecast generating processes identifier (defined by originating
            centre).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).

        Notes
        -----
        Numeric ranges describe representable values accepted by the wrapper, including
        reserved or missing-value codes. They do not imply that every value is valid in
        the referenced code table. Code-table and note references are retained from the
        upstream GRIB2 documentation.
        """
        ...
    def __repr__(self, /) -> str: ...
    @property
    def background_process(self, /) -> int:
        """Background generating process identifier (defined by originating centre).

        Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        """
        ...
    @background_process.setter
    def background_process(self, /, value: int) -> None:
        """Background generating process identifier (defined by originating centre).

        Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        """
        ...
    @property
    def process_id(self, /) -> int:
        """Analysis or forecast generating processes identifier (defined by originating
        centre).

        Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        """
        ...
    @process_id.setter
    def process_id(self, /, value: int) -> None:
        """Analysis or forecast generating processes identifier (defined by originating
        centre).

        Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        """
        ...
    @property
    def process_type(self, /) -> int:
        """Type of generating process (see Code Table 4.3).

        Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        """
        ...
    @process_type.setter
    def process_type(self, /, value: int) -> None:
        """Type of generating process (see Code Table 4.3).

        Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        """
        ...

@final
class ProductParam:
    """Python wrapper for grib::def::grib2::template::param_set::ProductParam.
    """
    def __new__(cls, /, category: int, num: int) -> ProductParam:
        """Create ProductParam.

        Parameters
        ----------
        category : int
            Parameter category (see Code Table 4.1).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        num : int
            Parameter number (see Code Table 4.2).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).

        Notes
        -----
        Numeric ranges describe representable values accepted by the wrapper, including
        reserved or missing-value codes. They do not imply that every value is valid in
        the referenced code table. Code-table and note references are retained from the
        upstream GRIB2 documentation.
        """
        ...
    def __repr__(self, /) -> str: ...
    @property
    def category(self, /) -> int:
        """Parameter category (see Code Table 4.1).

        Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        """
        ...
    @category.setter
    def category(self, /, value: int) -> None:
        """Parameter category (see Code Table 4.1).

        Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        """
        ...
    @property
    def num(self, /) -> int:
        """Parameter number (see Code Table 4.2).

        Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        """
        ...
    @num.setter
    def num(self, /, value: int) -> None:
        """Parameter number (see Code Table 4.2).

        Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        """
        ...

@final
class ForecastTime:
    """Python wrapper for grib::def::grib2::template::param_set::ForecastTime.
    """
    def __new__(cls, cutoff_hours: int, cutoff_minutes: int, unit: int, time: int) -> ForecastTime:
        """Create ForecastTime.

        Parameters
        ----------
        cutoff_hours : int
            Hours after reference time of data cutoff (see Note 1).

            Encoded as an unsigned 16-bit integer. Accepted range: 0 to 65535
            (inclusive).
        cutoff_minutes : int
            Minutes after reference time of data cutoff.

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        unit : int
            Indicator of unit of time range (see Code Table 4.4).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        time : int
            Forecast time in units defined by octet 18.

            Encoded as a signed 32-bit sign-magnitude integer. Accepted range:
            -2147483647 to 2147483647 (inclusive).

        Notes
        -----
        Python wrapper: unit and time correspond to ForecastTime::time.unit and
        ForecastTime::time.len. The descriptions above are the field-specific dump
        documentation from grib. Rust i32::MIN (-2147483648) is rejected because GRIB
        uses sign-magnitude representation.

        Numeric ranges describe representable values accepted by the wrapper, including
        reserved or missing-value codes. They do not imply that every value is valid in
        the referenced code table. Code-table and note references are retained from the
        upstream GRIB2 documentation.

        Raises
        ------
        ValueError
            If a signed value is the Rust minimum excluded by GRIB sign-magnitude.
        OverflowError
            If an integer is outside the underlying Rust integer range.
        """
        ...
    def __repr__(self) -> str: ...

@final
class FixedSurface:
    """Python wrapper for grib::def::grib2::template::param_set::FixedSurface.
    """
    def __new__(cls, surface_type: int, scale_factor: int, scaled_value: int) -> FixedSurface:
        """Create FixedSurface.

        Parameters
        ----------
        surface_type : int
            Type of fixed surface (see Code Table 4.5).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        scale_factor : int
            Scale factor.

            Encoded as a signed 8-bit sign-magnitude integer. Accepted range: -127 to
            127 (inclusive).
        scaled_value : int
            Scaled value.

            Encoded as a signed 32-bit sign-magnitude integer. Accepted range:
            -2147483647 to 2147483647 (inclusive).

        Notes
        -----
        Python wrapper: scale_factor and scaled_value correspond to
        FixedSurface::value.scale_factor and FixedSurface::value.scaled_value. The
        represented value is scaled_value * 10**(-scale_factor). To encode an absent
        surface, use surface_type=255, scale_factor=-127, and scaled_value=-2147483647.
        Rust i8::MIN (-128) and i32::MIN (-2147483648) are rejected.

        Numeric ranges describe representable values accepted by the wrapper, including
        reserved or missing-value codes. They do not imply that every value is valid in
        the referenced code table. Code-table and note references are retained from the
        upstream GRIB2 documentation.

        Raises
        ------
        ValueError
            If a signed value is the Rust minimum excluded by GRIB sign-magnitude.
        OverflowError
            If an integer is outside the underlying Rust integer range.
        """
        ...
    def __repr__(self) -> str: ...

@final
class Horizontal:
    """Python wrapper for grib::def::grib2::template::param_set::Horizontal.
    """
    def __new__(cls, first_surface: FixedSurface, second_surface: FixedSurface) -> Horizontal:
        """Create Horizontal.

        Parameters
        ----------
        first_surface : FixedSurface
            Python argument for
            grib::def::grib2::template::param_set::Horizontal::first_surface.
        second_surface : FixedSurface
            Python argument for
            grib::def::grib2::template::param_set::Horizontal::second_surface.

        Notes
        -----
        Python wrapper: inputs are copied. The upstream grouped members have no
        standalone prose descriptions; their Rust field paths are given above. The
        first_surface field supplies these upstream contextual descriptions: "Type of
        first fixed surface (see Code Table 4.5).", "Scale factor of first fixed
        surface.", "Scaled value of first fixed surface." The second_surface field
        supplies: "Type of second fixed surface (see Code Table 4.5).", "Scale factor of
        second fixed surface.", "Scaled value of second fixed surface."
        """
        ...
    def __repr__(self) -> str: ...

@final
class EnsembleForecast:
    """Python wrapper for grib::def::grib2::template::param_set::EnsembleForecast.
    """
    def __new__(cls, ensemble_forecast_type: int, perturbation_num: int, num_forecasts: int) -> EnsembleForecast:
        """Create EnsembleForecast.

        Parameters
        ----------
        ensemble_forecast_type : int
            Type of ensemble forecast (see Code Table 4.6).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        perturbation_num : int
            Perturbation number.

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        num_forecasts : int
            Number of forecasts in ensemble.

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).

        Notes
        -----
        Numeric ranges describe representable values accepted by the wrapper, including
        reserved or missing-value codes. They do not imply that every value is valid in
        the referenced code table. Code-table and note references are retained from the
        upstream GRIB2 documentation.
        """
        ...
    def __repr__(self) -> str: ...

@final
class StatisticalProcess:
    """Python wrapper for grib::def::grib2::template::param_set::StatisticalProcess.
    """
    def __new__(cls, statistical_process_type: int, time_increment_type: int, time_range_unit: int, time_range_length: int, time_increment_unit: int, time_increment_length: int) -> StatisticalProcess:
        """Create StatisticalProcess.

        Parameters
        ----------
        statistical_process_type : int
            Statistical process used to calculate the processed field from the field at
            each time increment during the time range (see Code Table 4.10).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        time_increment_type : int
            Type of time increment between successive fields used in the statistical
            processing (see Code Table 4.11).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        time_range_unit : int
            Indicator of unit of time for time range over which statistical processing
            is done (see Code Table 4.4).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        time_range_length : int
            Length of the time range over which statistical processing is done, in units
            defined by the previous octet.

            Encoded as an unsigned 32-bit integer. Accepted range: 0 to 4294967295
            (inclusive).
        time_increment_unit : int
            Indicator of unit of time for the increment between the successive fields
            used (see Code Table 4.4).

            Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        time_increment_length : int
            Time increment between successive fields, in units defined by the previous
            octet (see Notes 3 and 4).

            Encoded as an unsigned 32-bit integer. Accepted range: 0 to 4294967295
            (inclusive).

        Notes
        -----
        Python wrapper: time_range_unit and time_range_length correspond to
        time_range.unit and time_range.len; time_increment_unit and
        time_increment_length correspond to time_increment.unit and time_increment.len.
        Their descriptions are the field-specific dump documentation from grib.

        Numeric ranges describe representable values accepted by the wrapper, including
        reserved or missing-value codes. They do not imply that every value is valid in
        the referenced code table. Code-table and note references are retained from the
        upstream GRIB2 documentation.
        """
        ...
    def __repr__(self) -> str: ...

@final
class Statistical:
    """Python wrapper for grib::def::grib2::template::param_set::Statistical.
    """
    def __new__(cls, end_of_overall_time_interval: datetime, num_missing: int, time_ranges: List[StatisticalProcess]) -> Statistical:
        """Create Statistical.

        Parameters
        ----------
        end_of_overall_time_interval : datetime
            Time of end of overall time interval.

            Python wrapper: calendar fields are copied directly without timezone
            conversion; supply UTC. Year is encoded as an unsigned 16-bit integer (0 to
            65535); month, day, hour, minute, and second as unsigned 8-bit integers (0
            to 255). Python datetime restricts these to valid calendar values (year 1 to
            9999, month 1 to 12, day 1 to 31 as valid for the month, hour 0 to 23,
            minute and second 0 to 59). Microseconds are not encoded.
        num_missing : int
            Total number of data values missing in statistical process.

            Encoded as an unsigned 32-bit integer. Accepted range: 0 to 4294967295
            (inclusive).
        time_ranges : List[StatisticalProcess]
            Python argument for
            grib::def::grib2::template::param_set::Statistical::time_ranges.

            The wrapper requires 1 to 255 entries and derives num_time_ranges from the
            list length.

        Notes
        -----
        Upstream num_time_ranges description: n - Number of time range
        specifications describing the time intervals used to calculate the statistically
        processed field.

        Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        Python wrapper: this field is computed from time_ranges, and its supported range
        is 1 to 255.

        Numeric ranges describe representable values accepted by the wrapper, including
        reserved or missing-value codes. They do not imply that every value is valid in
        the referenced code table. Code-table and note references are retained from the
        upstream GRIB2 documentation.

        Raises
        ------
        ValueError
            If time_ranges contains fewer than 1 or more than 255 entries.
        OverflowError
            If num_missing is outside the unsigned 32-bit integer range.
        """
        ...
    def __repr__(self) -> str: ...
