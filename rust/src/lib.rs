use grib::encoder;
use numpy::PyReadonlyArray1;
use pyo3::{prelude::*, types::PyDateTime};

#[pymodule]
#[pyo3(name = "_gribify")]
mod gribify {

    use grib::encoder::{self, WriteGrib2Message};
    use numpy::{PyReadonlyArray1, PyReadonlyArray2};
    use pyo3::{
        exceptions::PyRuntimeError,
        prelude::*,
        types::{PyBytes, PyDateTime},
    };

    #[pyfunction]
    fn generate_grib2<'py>(
        py: Python<'py>,
        datetime: Bound<'py, PyDateTime>,
        product: Bound<'py, PyBytes>,
        lats: PyReadonlyArray1<'py, f64>,
        lngs: PyReadonlyArray1<'py, f64>,
        values: PyReadonlyArray2<'py, f64>,
    ) -> PyResult<Bound<'py, PyBytes>> {
        let grid = super::LatLngGridDef::try_from((lats, lngs))?;
        let value_view = values.as_array();
        let value_shape = value_view.shape();
        if value_shape[0] != grid.ni() || value_shape[1] != grid.nj() {
            return Err(PyRuntimeError::new_err(format!(
                "shape mismatch: lng/lat grid = ({}, {}), value grid = ({}, {})",
                grid.ni(),
                grid.nj(),
                value_shape[0],
                value_shape[1]
            )));
        }
        let encoded = encoder::GpvEncoder::new(
            std::borrow::Cow::Borrowed(values.as_slice()?),
            encoder::EncodingMethod::ComplexPacking(
                encoder::SimplePackingStrategy::Decimal(1),
                encoder::ComplexPackingStrategy::LookAhead(4),
                encoder::SpatialDifferencingOption::None,
            ),
        );

        let discipline = 0;
        let sect1_payload = super::section1(datetime)?;
        let sect3_payload = grid.section3();
        let message = encoder::SingleGrib2Message::new(
            discipline,
            sect1_payload,
            None::<&[u8]>,
            sect3_payload,
            product.as_bytes(),
            encoded,
        );
        let mut buf = vec![0; message.num_octets()];
        let mut _pos = 0;
        message
            .write(&mut buf)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

        Ok(PyBytes::new(py, &buf))
    }

    #[pymodule]
    mod param_set {
        use pyo3::prelude::*;

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

        #[pyclass(new = "from_fields")]
        #[derive(Debug)]
        pub struct GeneratingProcess {
            /// Type of generating process (see Code Table 4.3).
            #[pyo3(get, set)]
            pub process_type: u8,
            /// Background generating process identifier (defined by originating centre).
            #[pyo3(get, set)]
            pub background_process: u8,
            /// Analysis or forecast generating processes identifier (defined by originating centre).
            #[pyo3(get, set)]
            pub process_id: u8,
        }

        #[pymethods]
        impl GeneratingProcess {
            fn __repr__(&self) -> String {
                format!(
                    "GeneratingProcess(process_type={}, background_process={}, process_id={})",
                    self.process_type, self.background_process, self.process_id
                )
            }
        }
    }
}

fn section1<'py>(datetime: Bound<'py, PyDateTime>) -> PyResult<grib::def::grib2::Section1Payload> {
    let sect = grib::def::grib2::Section1Payload {
        centre_id: 0xffff,
        subcentre_id: 0,
        master_table_version: 29,
        local_table_version: 0,
        ref_time_significance: 0,
        ref_time: grib::def::grib2::template::param_set::DateTime {
            year: datetime.getattr("year")?.extract::<u16>()?,
            month: datetime.getattr("month")?.extract::<u8>()?,
            day: datetime.getattr("day")?.extract::<u8>()?,
            hour: datetime.getattr("hour")?.extract::<u8>()?,
            minute: datetime.getattr("minute")?.extract::<u8>()?,
            second: datetime.getattr("second")?.extract::<u8>()?,
        },
        prod_status: 0,
        data_type: 0,
        optional: None,
    };
    Ok(sect)
}

struct LatLngGridDef(encoder::LatLonGrid);

impl LatLngGridDef {
    fn section3(&self) -> grib::def::grib2::Section3Payload {
        grib::def::grib2::Section3Payload {
            grid_def_source: 0,
            num_points: self.num_points() as u32,
            num_point_list_octets: 0,
            point_list_interpretation: 0,
            template_num: 0,
            template: grib::def::grib2::GridDefinitionTemplate::_3_0(
                grib::def::grib2::template::Template3_0 {
                    earth: grib::def::grib2::template::param_set::EarthShape {
                        shape: 6,
                        spherical_earth_radius:
                            grib::def::grib2::template::param_set::ScaledValue {
                                scale_factor: 0xff,
                                scaled_value: 0xffffffff,
                            },
                        major_axis: grib::def::grib2::template::param_set::ScaledValue {
                            scale_factor: 0xff,
                            scaled_value: 0xffffffff,
                        },
                        minor_axis: grib::def::grib2::template::param_set::ScaledValue {
                            scale_factor: 0xff,
                            scaled_value: 0xffffffff,
                        },
                    },
                    lat_lon: grib::def::grib2::template::param_set::LatLonGrid::from(&self.0),
                },
            ),
        }
    }

    fn num_points(&self) -> usize {
        self.0.shape.0 * self.0.shape.1
    }

    fn ni(&self) -> usize {
        self.0.shape.0
    }

    fn nj(&self) -> usize {
        self.0.shape.1
    }
}

impl<'py> TryFrom<(PyReadonlyArray1<'py, f64>, PyReadonlyArray1<'py, f64>)> for LatLngGridDef {
    type Error = PyErr;

    fn try_from(
        value: (PyReadonlyArray1<'py, f64>, PyReadonlyArray1<'py, f64>),
    ) -> Result<Self, Self::Error> {
        let (lats, lngs) = value;
        let ni = lngs.len()? as usize;
        let nj = lats.len()? as usize;
        let lats_arr = lats.as_array();
        let lngs_arr = lngs.as_array();

        Ok(Self(encoder::LatLonGrid {
            shape: (ni, nj),
            first_point: (lats_arr[0], lngs_arr[0]),
            last_point: (lats_arr[lats_arr.len() - 1], lngs_arr[lngs_arr.len() - 1]),
            i_consecutive: true,
        }))
    }
}
