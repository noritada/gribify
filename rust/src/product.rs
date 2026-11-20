use grib::def::grib2::{
    ProductDefinitionTemplate, Section4Payload, table,
    template::{self, param_set as params},
};
use pyo3::{exceptions::PyTypeError, prelude::*};

/// Product definition with no trailing vertical coordinate values.
#[pyclass]
#[derive(Debug)]
pub struct ProductDefinition(pub(crate) Section4Payload);

#[pymethods]
impl ProductDefinition {
    #[new]
    fn new(template: &Bound<'_, PyAny>) -> PyResult<Self> {
        let (template_num, template) = if let Ok(t) = template.extract::<PyRef<Template4_0>>() {
            (0, ProductDefinitionTemplate::_4_0(t.0.clone()))
        } else if let Ok(t) = template.extract::<PyRef<Template4_1>>() {
            (1, ProductDefinitionTemplate::_4_1(t.0.clone()))
        } else if let Ok(t) = template.extract::<PyRef<Template4_8>>() {
            (8, ProductDefinitionTemplate::_4_8(t.0.clone()))
        } else {
            return Err(PyTypeError::new_err(
                "template must be Template4_0, Template4_1 or Template4_8",
            ));
        };
        Ok(Self(Section4Payload {
            num_coord_values: 0,
            template_num: table::ProductDefinitionTemplateNum(template_num),
            template,
        }))
    }
    #[getter]
    fn template_num(&self) -> u16 {
        self.0.template_num.0
    }
    fn __repr__(&self) -> String {
        format!("ProductDefinition({:?})", self.0)
    }
}

/// Analysis or forecast at a horizontal level or layer at a single time.
#[pyclass]
#[derive(Debug)]
pub struct Template4_0(template::Template4_0);
#[pymethods]
impl Template4_0 {
    #[new]
    fn new(
        param: &param_set::ProductParam,
        generating_process: &param_set::GeneratingProcess,
        forecast_time: &param_set::ForecastTime,
        horizontal: &param_set::Horizontal,
    ) -> Self {
        Self(template::Template4_0 {
            param: params::ProductParam {
                category: table::ParamCategory(param.category),
                num: table::ParamNum(param.num),
            },
            generating_process: params::GeneratingProcess {
                process_type: table::GeneratingProcessType(generating_process.process_type),
                background_process: generating_process.background_process,
                process_id: generating_process.process_id,
            },
            forecast_time: forecast_time.0.clone(),
            horizontal: horizontal.0.clone(),
        })
    }
    fn __repr__(&self) -> String {
        format!("{:?}", self.0)
    }
}

/// Individual ensemble member at a horizontal level or layer at a single time.
#[pyclass]
#[derive(Debug)]
pub struct Template4_1(template::Template4_1);
#[pymethods]
impl Template4_1 {
    #[new]
    fn new(
        param: &param_set::ProductParam,
        generating_process: &param_set::GeneratingProcess,
        forecast_time: &param_set::ForecastTime,
        horizontal: &param_set::Horizontal,
        ensemble_forecast: &param_set::EnsembleForecast,
    ) -> Self {
        Self(template::Template4_1 {
            param: params::ProductParam {
                category: table::ParamCategory(param.category),
                num: table::ParamNum(param.num),
            },
            generating_process: params::GeneratingProcess {
                process_type: table::GeneratingProcessType(generating_process.process_type),
                background_process: generating_process.background_process,
                process_id: generating_process.process_id,
            },
            forecast_time: forecast_time.0.clone(),
            horizontal: horizontal.0.clone(),
            emsemble_forecast: ensemble_forecast.0.clone(),
        })
    }
    fn __repr__(&self) -> String {
        format!("{:?}", self.0)
    }
}

/// Statistically processed values over one or more time intervals.
#[pyclass]
#[derive(Debug)]
pub struct Template4_8(template::Template4_8);
#[pymethods]
impl Template4_8 {
    #[new]
    fn new(
        param: &param_set::ProductParam,
        generating_process: &param_set::GeneratingProcess,
        forecast_time: &param_set::ForecastTime,
        horizontal: &param_set::Horizontal,
        statistical: &param_set::Statistical,
    ) -> Self {
        Self(template::Template4_8 {
            param: params::ProductParam {
                category: table::ParamCategory(param.category),
                num: table::ParamNum(param.num),
            },
            generating_process: params::GeneratingProcess {
                process_type: table::GeneratingProcessType(generating_process.process_type),
                background_process: generating_process.background_process,
                process_id: generating_process.process_id,
            },
            forecast_time: forecast_time.0.clone(),
            horizontal: horizontal.0.clone(),
            time_interval: statistical.0.clone(),
        })
    }
    fn __repr__(&self) -> String {
        format!("{:?}", self.0)
    }
}
#[pymodule(gil_used = false)]
pub mod param_set {
    use super::{params, table};
    use pyo3::exceptions::PyValueError;
    use pyo3::prelude::*;
    use pyo3::types::{PyDateTime, PyString};

    #[pyclass(new = "from_fields")]
    #[derive(Debug)]
    pub struct ProductParam {
        /// Parameter category (see Code Table 4.1).
        #[pyo3(get, set)]
        pub category: u8,
        /// Parameter number (see Code Table 4.2).
        #[pyo3(get, set)]
        pub num: u8,
    }

    #[pymethods]
    impl ProductParam {
        fn __repr__(&self) -> String {
            format!("ProductParam(category={}, num={})", self.category, self.num)
        }
    }

    #[pyclass]
    #[derive(Debug)]
    pub struct GeneratingProcess {
        /// Type of generating process (see Code Table 4.3).
        #[pyo3(get)]
        pub process_type: u8,
        /// Background generating process identifier (defined by originating centre).
        #[pyo3(get, set)]
        pub background_process: u8,
        /// Analysis or forecast generating processes identifier (defined by originating centre).
        #[pyo3(get, set)]
        pub process_id: u8,
    }

    fn parse_generating_process_type(value: &Bound<'_, PyAny>) -> PyResult<u8> {
        if let Ok(name) = value.cast::<PyString>() {
            let name = name.to_str()?;
            crate::code_tables::lookup_generating_process_type(name).ok_or_else(|| {
                PyValueError::new_err(format!(
                    "unknown Code Table 4.3 generating process type: {name:?}"
                ))
            })
        } else {
            value.extract::<u8>()
        }
    }

    #[pymethods]
    impl GeneratingProcess {
        #[new]
        fn new(
            process_type: &Bound<'_, PyAny>,
            background_process: u8,
            process_id: u8,
        ) -> PyResult<Self> {
            Ok(Self {
                process_type: parse_generating_process_type(process_type)?,
                background_process,
                process_id,
            })
        }

        #[setter]
        fn set_process_type(&mut self, value: &Bound<'_, PyAny>) -> PyResult<()> {
            self.process_type = parse_generating_process_type(value)?;
            Ok(())
        }

        fn __repr__(&self) -> String {
            format!(
                "GeneratingProcess(process_type={}, background_process={}, process_id={})",
                self.process_type, self.background_process, self.process_id
            )
        }
    }

    // Code Table 4.4 names are shared by forecast and statistical time ranges.
    fn parse_time_range_unit(value: &Bound<'_, PyAny>) -> PyResult<table::TimeRangeUnit> {
        let code = if let Ok(name) = value.cast::<PyString>() {
            crate::code_tables::lookup_time_range_unit(name.to_str()?).ok_or_else(|| {
                PyValueError::new_err(format!("unknown Code Table 4.4 time unit: {:?}", name))
            })?
        } else {
            value.extract::<u8>()?
        };
        Ok(table::TimeRangeUnit(code))
    }

    /// Data cutoff and signed forecast offset; unit uses Code Table 4.4.
    #[pyclass]
    #[derive(Debug)]
    pub struct ForecastTime(pub(super) params::ForecastTime);
    #[pymethods]
    impl ForecastTime {
        #[new]
        fn new(
            cutoff_hours: u16,
            cutoff_minutes: u8,
            unit: &Bound<'_, PyAny>,
            time: i32,
        ) -> PyResult<Self> {
            if time == i32::MIN {
                return Err(PyValueError::new_err(
                    "time must be between -2147483647 and 2147483647",
                ));
            }
            Ok(Self(params::ForecastTime {
                cutoff_hours,
                cutoff_minutes,
                time: params::TimeRange {
                    unit: parse_time_range_unit(unit)?,
                    len: time,
                },
            }))
        }
        fn __repr__(&self) -> String {
            format!("{:?}", self.0)
        }
    }

    /// Fixed surface value = scaled_value * 10^(-scale_factor). Use (255, -127, -2147483647) for an absent surface.
    #[pyclass]
    #[derive(Debug)]
    pub struct FixedSurface(pub(super) params::FixedSurface);
    #[pymethods]
    impl FixedSurface {
        #[new]
        fn new(
            surface_type: &Bound<'_, PyAny>,
            scale_factor: i8,
            scaled_value: i32,
        ) -> PyResult<Self> {
            let surface_type = if let Ok(name) = surface_type.cast::<PyString>() {
                let name = name.to_str()?;
                crate::code_tables::lookup_fixed_surface_type(name).ok_or_else(|| {
                    PyValueError::new_err(format!(
                        "unknown Code Table 4.5 fixed surface type: {name:?}"
                    ))
                })?
            } else {
                surface_type.extract::<u8>()?
            };
            if scale_factor == i8::MIN || scaled_value == i32::MIN {
                return Err(PyValueError::new_err(
                    "GRIB signed values use sign-magnitude: scale_factor must be >= -127 and scaled_value >= -2147483647",
                ));
            }
            Ok(Self(params::FixedSurface {
                surface_type: table::FixedSurfaceType(surface_type),
                value: params::ScaledValue {
                    scale_factor,
                    scaled_value,
                },
            }))
        }
        fn __repr__(&self) -> String {
            format!("{:?}", self.0)
        }
    }

    /// First and second fixed surfaces defining a level or layer.
    #[pyclass]
    #[derive(Debug)]
    pub struct Horizontal(pub(super) params::Horizontal);
    #[pymethods]
    impl Horizontal {
        #[new]
        fn new(first_surface: &FixedSurface, second_surface: &FixedSurface) -> PyResult<Self> {
            Ok(Self(params::Horizontal {
                first_surface: first_surface.0.clone(),
                second_surface: second_surface.0.clone(),
            }))
        }
        fn __repr__(&self) -> String {
            format!("{:?}", self.0)
        }
    }

    /// Ensemble type (Code Table 4.6), member number, and ensemble size.
    #[pyclass]
    #[derive(Debug)]
    pub struct EnsembleForecast(pub(super) params::EnsembleForecast);
    #[pymethods]
    impl EnsembleForecast {
        #[new]
        fn new(
            ensemble_forecast_type: u8,
            perturbation_num: u8,
            num_forecasts: u8,
        ) -> PyResult<Self> {
            Ok(Self(params::EnsembleForecast {
                ensemble_forecast_type: table::EnsembleForecastType(ensemble_forecast_type),
                perturbation_num,
                num_forecasts,
            }))
        }
        fn __repr__(&self) -> String {
            format!("{:?}", self.0)
        }
    }

    /// Statistical operation and unsigned interval/increment lengths with Code Table 4.4 units.
    #[pyclass]
    #[derive(Debug)]
    pub struct StatisticalProcess(pub(super) params::StatisticalProcess);
    #[pymethods]
    impl StatisticalProcess {
        #[new]
        fn new(
            statistical_process_type: u8,
            time_increment_type: u8,
            time_range_unit: &Bound<'_, PyAny>,
            time_range_length: u32,
            time_increment_unit: &Bound<'_, PyAny>,
            time_increment_length: u32,
        ) -> PyResult<Self> {
            Ok(Self(params::StatisticalProcess {
                statistical_process_type: table::StatisticalProcessType(statistical_process_type),
                time_increment_type: table::TimeIncrementType(time_increment_type),
                time_range: params::TimeRange {
                    unit: parse_time_range_unit(time_range_unit)?,
                    len: time_range_length,
                },
                time_increment: params::TimeRange {
                    unit: parse_time_range_unit(time_increment_unit)?,
                    len: time_increment_length,
                },
            }))
        }
        fn __repr__(&self) -> String {
            format!("{:?}", self.0)
        }
    }

    /// Statistical end time (UTC calendar fields), missing count, and 1 to 255 time ranges.
    #[pyclass]
    #[derive(Debug)]
    pub struct Statistical(pub(super) params::Statistical);
    #[pymethods]
    impl Statistical {
        #[new]
        fn new(
            end_of_overall_time_interval: &Bound<'_, PyDateTime>,
            num_missing: u32,
            time_ranges: Vec<PyRef<'_, StatisticalProcess>>,
        ) -> PyResult<Self> {
            let num_time_ranges = u8::try_from(time_ranges.len())
                .map_err(|_| PyValueError::new_err("time_ranges must contain 1 to 255 entries"))?;
            if num_time_ranges == 0 {
                return Err(PyValueError::new_err(
                    "time_ranges must contain 1 to 255 entries",
                ));
            }
            let dt = end_of_overall_time_interval;
            Ok(Self(params::Statistical {
                end_of_overall_time_interval: params::DateTime {
                    year: dt.getattr("year")?.extract()?,
                    month: dt.getattr("month")?.extract()?,
                    day: dt.getattr("day")?.extract()?,
                    hour: dt.getattr("hour")?.extract()?,
                    minute: dt.getattr("minute")?.extract()?,
                    second: dt.getattr("second")?.extract()?,
                },
                num_time_ranges,
                num_missing,
                time_ranges: time_ranges.iter().map(|p| p.0.clone()).collect(),
            }))
        }
        fn __repr__(&self) -> String {
            format!("{:?}", self.0)
        }
    }
}
