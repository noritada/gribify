mod product;

use grib::encoder;
use numpy::PyReadonlyArray1;
use pyo3::prelude::*;

#[pymodule]
#[pyo3(name = "_gribify")]
mod gribify {

    use grib::{
        def::grib2::Section1Payload,
        encoder::{self, WriteGrib2Message},
    };
    use numpy::{PyReadonlyArray1, PyReadonlyArray2};
    use pyo3::{
        exceptions::PyRuntimeError,
        prelude::*,
        types::{PyBytes, PyDateTime},
    };

    #[pyfunction]
    fn grib2_message<'py>(
        py: Python<'py>,
        discipline: u8,
        ident: &Identification,
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

        let sect3_payload = grid.section3();
        let message = encoder::SingleGrib2Message::new(
            discipline,
            ident.inner(),
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

    #[pyclass]
    struct Identification(Section1Payload);

    #[pymethods]
    impl Identification {
        #[new]
        fn new<'py>(
            centre_id: u16,
            subcentre_id: u16,
            master_table_version: u8,
            local_table_version: u8,
            ref_time_significance: u8,
            ref_time: Bound<'py, PyDateTime>,
            prod_status: u8,
            data_type: u8,
        ) -> PyResult<Self> {
            let ref_time = grib::def::grib2::template::param_set::DateTime {
                year: ref_time.getattr("year")?.extract::<u16>()?,
                month: ref_time.getattr("month")?.extract::<u8>()?,
                day: ref_time.getattr("day")?.extract::<u8>()?,
                hour: ref_time.getattr("hour")?.extract::<u8>()?,
                minute: ref_time.getattr("minute")?.extract::<u8>()?,
                second: ref_time.getattr("second")?.extract::<u8>()?,
            };
            Ok(Self(Section1Payload {
                centre_id,
                subcentre_id,
                master_table_version,
                local_table_version,
                ref_time_significance,
                ref_time,
                prod_status,
                data_type,
                optional: None,
            }))
        }

        fn __repr__(&self) -> String {
            format!("{:?}", self.0)
        }
    }

    impl Identification {
        fn inner(&self) -> &Section1Payload {
            &self.0
        }
    }

    #[pymodule_export]
    use crate::product::param_set;
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
