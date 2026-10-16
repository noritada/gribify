from typing import final, List
from datetime import datetime

@final
class GeneratingProcess:
    def __new__(self, /, process_type: int, background_process: int, process_id: int) -> GeneratingProcess: ...
    def __repr__(self, /) -> str: ...
    @property
    def background_process(self, /) -> int:
        """
        Background generating process identifier (defined by originating centre).
        """
    @background_process.setter
    def background_process(self, /, value: int) -> None:
        """
        Background generating process identifier (defined by originating centre).
        """
    @property
    def process_id(self, /) -> int:
        """
        Analysis or forecast generating processes identifier (defined by originating centre).
        """
    @process_id.setter
    def process_id(self, /, value: int) -> None:
        """
        Analysis or forecast generating processes identifier (defined by originating centre).
        """
    @property
    def process_type(self, /) -> int:
        """
        Type of generating process (see Code Table 4.3).
        """
    @process_type.setter
    def process_type(self, /, value: int) -> None:
        """
        Type of generating process (see Code Table 4.3).
        """

@final
class ProductParam:
    def __new__(self, /, category: int, num: int) -> ProductParam: ...
    def __repr__(self, /) -> str: ...
    @property
    def category(self, /) -> int:
        """
        Parameter category (see Code Table 4.1).
        """
    @category.setter
    def category(self, /, value: int) -> None:
        """
        Parameter category (see Code Table 4.1).
        """
    @property
    def num(self, /) -> int:
        """
        Parameter number (see Code Table 4.2).
        """
    @num.setter
    def num(self, /, value: int) -> None:
        """
        Parameter number (see Code Table 4.2).
        """

@final
class ProductParam2:
    def __new__(cls, /, category: int, num: int) -> ProductParam2: ...
    def __repr__(self, /) -> str: ...

@final
class TimeRangeInt32:
    def __new__(cls, /, unit: int, len: int) -> TimeRangeInt32: ...
    def __repr__(self, /) -> str: ...

@final
class ForecastTime:
    def __new__(cls, cutoff_hours: int, cutoff_minutes: int, unit: int, time: int) -> ForecastTime: ...
    def __repr__(self) -> str: ...

@final
class FixedSurface:
    def __new__(cls, surface_type: int, scale_factor: int, scaled_value: int) -> FixedSurface: ...
    def __repr__(self) -> str: ...

@final
class Horizontal:
    def __new__(cls, first_surface: FixedSurface, second_surface: FixedSurface) -> Horizontal: ...
    def __repr__(self) -> str: ...

@final
class EnsembleForecast:
    def __new__(cls, ensemble_forecast_type: int, perturbation_num: int, num_forecasts: int) -> EnsembleForecast: ...
    def __repr__(self) -> str: ...

@final
class StatisticalProcess:
    def __new__(cls, statistical_process_type: int, time_increment_type: int, time_range_unit: int, time_range_length: int, time_increment_unit: int, time_increment_length: int) -> StatisticalProcess: ...
    def __repr__(self) -> str: ...

@final
class Statistical:
    def __new__(cls, end_of_overall_time_interval: datetime, num_missing: int, time_ranges: List[StatisticalProcess]) -> Statistical: ...
    def __repr__(self) -> str: ...
