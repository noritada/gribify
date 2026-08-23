use grib::def::grib2::template::param_set::ScanningMode;
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
        if value_shape[0] != grid.ni() as usize || value_shape[1] != grid.nj() as usize {
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
}

fn section1<'py>(datetime: Bound<'py, PyDateTime>) -> PyResult<grib::def::grib2::Section1Payload> {
    let sect = grib::def::grib2::Section1Payload {
        centre_id: 0xffff,
        subcentre_id: 0,
        master_table_version: 29,
        local_table_version: 0,
        ref_time_significance: 0,
        ref_time: grib::def::grib2::RefTime {
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

struct LatLngGridDef {
    /// (ni, nj).
    shape: (u32, u32),
    /// (lat, lng) of the first point.
    first_point: (f64, f64),
    /// (lat, lng) of the last point.
    last_point: (f64, f64),
}

impl LatLngGridDef {
    fn section3(&self) -> grib::def::grib2::Section3Payload {
        grib::def::grib2::Section3Payload {
            grid_def_source: 0,
            num_points: self.num_points(),
            num_point_list_octets: 0,
            point_list_interpretation: 0,
            template_num: 0,
            template: grib::def::grib2::GridDefinitionTemplate::_3_0(
                grib::def::grib2::template::Template3_0 {
                    earth: grib::def::grib2::template::param_set::EarthShape {
                        shape: 6,
                        spherical_earth_radius_scale_factor: 0xff,
                        spherical_earth_radius_scaled_value: 0xffffffff,
                        major_axis_scale_factor: 0xff,
                        major_axis_scaled_value: 0xffffffff,
                        minor_axis_scale_factor: 0xff,
                        minor_axis_scaled_value: 0xffffffff,
                    },
                    lat_lon: grib::def::grib2::template::param_set::LatLonGrid {
                        grid: grib::def::grib2::template::param_set::Grid {
                            ni: self.ni(),
                            nj: self.nj(),
                            initial_production_domain_basic_angle: 0,
                            basic_angle_subdivisions: 0xffffffff,
                            first_point_lat: self.first_point_lat(),
                            first_point_lon: self.first_point_lng(),
                            resolution_and_component_flags:
                                grib::def::grib2::template::param_set::ResolutionAndComponentFlags(
                                    0b00110000,
                                ),
                            last_point_lat: self.last_point_lat(),
                            last_point_lon: self.last_point_lng(),
                        },
                        i_direction_inc: self.i_inc(),
                        j_direction_inc: self.j_inc(),
                        scanning_mode: self.scan_mode(),
                    },
                },
            ),
        }
    }

    fn num_points(&self) -> u32 {
        self.shape.0 * self.shape.1
    }

    fn ni(&self) -> u32 {
        self.shape.0
    }

    fn nj(&self) -> u32 {
        self.shape.1
    }

    fn first_point_lat(&self) -> i32 {
        (self.first_point.0 * 1e6) as i32
    }

    fn first_point_lng(&self) -> u32 {
        (normalize_longitude(self.first_point.1) * 1e6) as u32
    }

    fn last_point_lat(&self) -> i32 {
        (self.last_point.0 * 1e6) as i32
    }

    fn last_point_lng(&self) -> u32 {
        (normalize_longitude(self.last_point.1) * 1e6) as u32
    }

    fn i_inc(&self) -> u32 {
        ((self.last_point.1 - self.first_point.1) * 1e6).abs() as u32 / (self.shape.0 - 1) as u32
    }

    fn j_inc(&self) -> u32 {
        ((self.last_point.0 - self.first_point.0) * 1e6).abs() as u32 / (self.shape.1 - 1) as u32
    }

    fn scan_mode(&self) -> ScanningMode {
        let mut scan_mode: u8 = 0b00000000;
        if self.first_point.0 < self.last_point.0 {
            scan_mode |= 0b01000000;
        }
        if self.first_point.1 > self.last_point.1 {
            scan_mode |= 0b10000000;
        }
        ScanningMode(scan_mode)
    }
}

impl<'py> TryFrom<(PyReadonlyArray1<'py, f64>, PyReadonlyArray1<'py, f64>)> for LatLngGridDef {
    type Error = PyErr;

    fn try_from(
        value: (PyReadonlyArray1<'py, f64>, PyReadonlyArray1<'py, f64>),
    ) -> Result<Self, Self::Error> {
        let (lats, lngs) = value;
        let ni = lngs.len()? as u32;
        let nj = lats.len()? as u32;
        let lats_arr = lats.as_array();
        let lngs_arr = lngs.as_array();

        Ok(Self {
            shape: (ni, nj),
            first_point: (lats_arr[0], lngs_arr[0]),
            last_point: (lats_arr[lats_arr.len() - 1], lngs_arr[lngs_arr.len() - 1]),
        })
    }
}

fn normalize_longitude(val: f64) -> f64 {
    if val < 0. { val + 360. } else { val }
}
